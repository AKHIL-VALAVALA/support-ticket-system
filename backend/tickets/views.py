from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer
from .filters import TicketFilter
from .models import Ticket, TicketComment
from .permissions import IsAgent, IsCustomer, IsTicketOwnerOrAgent
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    TicketCommentSerializer,
)

User = get_user_model()


class TicketListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tickets  - list tickets (customers see only their own, agents see all)
    POST /api/tickets  - create a ticket (customers only)
    """

    filterset_class = TicketFilter
    search_fields = ["subject", "description"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsCustomer()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        return TicketCreateSerializer if self.request.method == "POST" else TicketListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related("user", "assigned_to")
        if user.is_agent:
            return qs
        return qs.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        output = TicketDetailSerializer(ticket)
        return Response(output.data, status=status.HTTP_201_CREATED)


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tickets/:id  - authorized user (owner or agent)
    PUT    /api/tickets/:id  - agent (any field) or owning customer (subject/description only)
    DELETE /api/tickets/:id  - agents only
    """

    queryset = Ticket.objects.select_related("user", "assigned_to").all()
    serializer_class = TicketDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsTicketOwnerOrAgent]

    def get_object(self):
        obj = generics.get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()
        user = request.user

        if user.is_agent:
            allowed_fields = {"subject", "description", "priority", "status", "assigned_to"}
        elif ticket.user_id == user.id:
            allowed_fields = {"subject", "description"}
        else:
            raise PermissionDenied("You do not have permission to update this ticket.")

        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        serializer = TicketUpdateSerializer(ticket, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TicketDetailSerializer(ticket).data)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_agent:
            raise PermissionDenied("Only support agents can delete tickets.")
        return super().destroy(request, *args, **kwargs)


class TicketCommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tickets/:id/comments  - authorized user (owner or agent)
    POST /api/tickets/:id/comments  - authorized user (owner or agent)
    """

    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_ticket(self):
        try:
            ticket = Ticket.objects.get(pk=self.kwargs["pk"])
        except Ticket.DoesNotExist:
            raise NotFound("Ticket not found.")
        user = self.request.user
        if not user.is_agent and ticket.user_id != user.id:
            raise PermissionDenied("You do not have permission to access this ticket's comments.")
        return ticket

    def get_queryset(self):
        ticket = self._get_ticket()
        return TicketComment.objects.filter(ticket=ticket).select_related("user")

    def create(self, request, *args, **kwargs):
        ticket = self._get_ticket()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(ticket=ticket, user=request.user)
        return Response(self.get_serializer(comment).data, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    """GET /api/users - agents only. Supports ?role=agent to list agents for assignment."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def get_queryset(self):
        qs = User.objects.all().order_by("username")
        role = self.request.query_params.get("role")
        if role in ("agent", "customer"):
            qs = qs.filter(role=role)
        return qs


class TicketStatsView(APIView):
    """GET /api/tickets/stats - agent dashboard summary counts."""

    permission_classes = [permissions.IsAuthenticated, IsAgent]

    def get(self, request):
        by_status = Ticket.objects.values("status").annotate(count=Count("id"))
        by_priority = Ticket.objects.values("priority").annotate(count=Count("id"))
        unassigned = Ticket.objects.filter(assigned_to__isnull=True).count()
        total = Ticket.objects.count()
        return Response(
            {
                "total": total,
                "unassigned": unassigned,
                "by_status": {row["status"]: row["count"] for row in by_status},
                "by_priority": {row["priority"]: row["count"] for row in by_priority},
            }
        )

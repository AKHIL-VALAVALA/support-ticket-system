from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Ticket, TicketComment


class TicketCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(source="user", read_only=True)

    class Meta:
        model = TicketComment
        fields = ["id", "ticket", "author", "comment", "created_at"]
        read_only_fields = ["id", "ticket", "author", "created_at"]

    def validate_comment(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        return value


class TicketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used for list views."""

    customer = UserSerializer(source="user", read_only=True)
    assigned_to_detail = UserSerializer(source="assigned_to", read_only=True)
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id", "subject", "priority", "status", "customer",
            "assigned_to", "assigned_to_detail", "comment_count",
            "created_at", "updated_at",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    customer = UserSerializer(source="user", read_only=True)
    assigned_to_detail = UserSerializer(source="assigned_to", read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id", "subject", "description", "priority", "status",
            "customer", "assigned_to", "assigned_to_detail", "comments",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "customer", "created_at", "updated_at"]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "subject", "description", "priority"]

    def validate_subject(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Subject cannot be empty.")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return Ticket.objects.create(**validated_data)


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Used by agents to update status/priority/assignment, and by anyone authorized for minor edits."""

    class Meta:
        model = Ticket
        fields = ["subject", "description", "priority", "status", "assigned_to"]
        extra_kwargs = {
            "subject": {"required": False},
            "description": {"required": False},
        }

    def validate_assigned_to(self, value):
        if value is not None and value.role != "agent":
            raise serializers.ValidationError("Tickets may only be assigned to support agents.")
        return value

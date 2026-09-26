from django.urls import path
from .views import (
    TicketListCreateView,
    TicketDetailView,
    TicketCommentListCreateView,
    UserListView,
    TicketStatsView,
)

urlpatterns = [
    path("tickets", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("tickets/stats", TicketStatsView.as_view(), name="ticket-stats"),
    path("tickets/<int:pk>", TicketDetailView.as_view(), name="ticket-detail"),
    path("tickets/<int:pk>/comments", TicketCommentListCreateView.as_view(), name="ticket-comments"),
    path("users", UserListView.as_view(), name="user-list"),
]

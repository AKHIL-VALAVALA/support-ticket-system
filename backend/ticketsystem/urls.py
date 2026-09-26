from django.contrib import admin
from django.urls import include, path, reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    endpoint_names = {
        "register": "register",
        "login": "login",
        "refresh_token": "token_refresh",
        "logout": "logout",
        "tickets": "ticket-list-create",
        "users": "user-list",
    }
    endpoints = {
        name: request.build_absolute_uri(reverse(url_name))
        for name, url_name in endpoint_names.items()
    }
    return Response({
        "name": "Support Ticket API",
        "message": "API is running. Authentication is required for ticket and user endpoints.",
        "endpoints": endpoints,
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("tickets.urls")),
]

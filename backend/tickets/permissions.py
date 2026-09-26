from rest_framework import permissions


class IsAgent(permissions.BasePermission):
    """Allows access only to support agents."""

    message = "Only support agents may perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_agent)


class IsCustomer(permissions.BasePermission):
    """Allows access only to customers."""

    message = "Only customers may perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_customer)


class IsTicketOwnerOrAgent(permissions.BasePermission):
    """
    Object-level permission: a customer may only access their own ticket.
    Agents may access any ticket. Applies to Ticket instances and to
    related objects that expose a `.ticket` or `.user` attribute.
    """

    message = "You do not have permission to access this ticket."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_agent:
            return True
        ticket = obj if hasattr(obj, "user_id") and hasattr(obj, "subject") else getattr(obj, "ticket", None)
        owner_id = ticket.user_id if ticket is not None else getattr(obj, "user_id", None)
        return owner_id == user.id

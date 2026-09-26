import pytest
from tickets.models import Ticket


@pytest.mark.django_db
def test_ticket_creation_succeeds(customer_client, customer_user):
    payload = {"subject": "Cannot log in", "description": "Getting a 500 error.", "priority": "high"}
    response = customer_client.post("/api/tickets", payload)
    assert response.status_code == 201
    assert Ticket.objects.filter(subject="Cannot log in", user=customer_user).exists()


@pytest.mark.django_db
def test_agent_cannot_create_ticket(agent_client):
    response = agent_client.post("/api/tickets", {"subject": "x", "description": "y", "priority": "low"})
    assert response.status_code == 403


@pytest.mark.django_db
def test_customer_cannot_access_another_customers_ticket(customer_client, other_customer_client, customer_user):
    ticket = Ticket.objects.create(user=customer_user, subject="Private ticket", description="secret")
    response = other_customer_client.get(f"/api/tickets/{ticket.id}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_customer_can_view_own_ticket(customer_client, customer_user):
    ticket = Ticket.objects.create(user=customer_user, subject="My ticket", description="details")
    response = customer_client.get(f"/api/tickets/{ticket.id}")
    assert response.status_code == 200
    assert response.data["subject"] == "My ticket"


@pytest.mark.django_db
def test_agent_can_update_ticket_status(agent_client, customer_user, agent_user):
    ticket = Ticket.objects.create(user=customer_user, subject="Broken feature", description="details")
    response = agent_client.put(
        f"/api/tickets/{ticket.id}",
        {"status": "in_progress", "assigned_to": agent_user.id},
        format="json",
    )
    assert response.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == "in_progress"
    assert ticket.assigned_to_id == agent_user.id


@pytest.mark.django_db
def test_customer_cannot_change_ticket_status(customer_client, customer_user):
    ticket = Ticket.objects.create(user=customer_user, subject="My ticket", description="details")
    response = customer_client.put(
        f"/api/tickets/{ticket.id}",
        {"status": "closed"},
        format="json",
    )
    assert response.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == "open"


@pytest.mark.django_db
def test_invalid_ticket_id_returns_404(customer_client):
    response = customer_client.get("/api/tickets/999999")
    assert response.status_code == 404


@pytest.mark.django_db
def test_add_comment_to_own_ticket(customer_client, customer_user):
    ticket = Ticket.objects.create(user=customer_user, subject="My ticket", description="details")
    response = customer_client.post(f"/api/tickets/{ticket.id}/comments", {"comment": "Any update?"})
    assert response.status_code == 201
    assert ticket.comments.count() == 1


@pytest.mark.django_db
def test_forbidden_request_for_incorrect_role(customer_client):
    response = customer_client.get("/api/users")
    assert response.status_code == 403


@pytest.mark.django_db
def test_only_agent_can_delete_ticket(customer_client, customer_user):
    ticket = Ticket.objects.create(user=customer_user, subject="My ticket", description="details")
    response = customer_client.delete(f"/api/tickets/{ticket.id}")
    assert response.status_code == 403

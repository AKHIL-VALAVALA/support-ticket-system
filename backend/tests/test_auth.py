import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"


@pytest.mark.django_db
def test_api_root_is_available_without_authentication(api_client):
    response = api_client.get("/api/")
    assert response.status_code == 200
    assert response.data["name"] == "Support Ticket API"
    assert response.data["endpoints"]["tickets"].endswith("/api/tickets")


@pytest.mark.django_db
def test_register_success(api_client):
    payload = {"name": "New Customer", "email": "newcust@example.com", "password": "StrongPass123"}
    response = api_client.post(REGISTER_URL, payload)
    assert response.status_code == 201
    assert User.objects.filter(email="newcust@example.com", role="customer").exists()


@pytest.mark.django_db
def test_register_duplicate_email_rejected(api_client, customer_user):
    payload = {"name": "Dup", "email": customer_user.email, "password": "StrongPass123"}
    response = api_client.post(REGISTER_URL, payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_valid_login_succeeds(api_client, customer_user):
    response = api_client.post(LOGIN_URL, {"email": customer_user.email, "password": "StrongPass123"})
    assert response.status_code == 200
    assert "access" in response.data and "refresh" in response.data
    assert response.data["user"]["role"] == "customer"


@pytest.mark.django_db
def test_invalid_password_is_rejected(api_client, customer_user):
    response = api_client.post(LOGIN_URL, {"email": customer_user.email, "password": "WrongPassword"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthorized_user_cannot_access_protected_data(api_client):
    response = api_client.get("/api/tickets")
    assert response.status_code == 401

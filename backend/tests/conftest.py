import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        username="customer1@example.com",
        email="customer1@example.com",
        password="StrongPass123",
        role="customer",
        first_name="Alice",
    )


@pytest.fixture
def other_customer(db):
    return User.objects.create_user(
        username="customer2@example.com",
        email="customer2@example.com",
        password="StrongPass123",
        role="customer",
        first_name="Bob",
    )


@pytest.fixture
def agent_user(db):
    return User.objects.create_user(
        username="agent1@example.com",
        email="agent1@example.com",
        password="StrongPass123",
        role="agent",
        first_name="Charlie",
    )


def auth_client(client, user):
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def customer_client(api_client, customer_user):
    return auth_client(api_client, customer_user)


@pytest.fixture
def other_customer_client(api_client, other_customer):
    return auth_client(api_client, other_customer)


@pytest.fixture
def agent_client(api_client, agent_user):
    return auth_client(api_client, agent_user)

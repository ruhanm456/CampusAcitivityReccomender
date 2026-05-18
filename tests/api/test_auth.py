from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bcrypt import hashpw, gensalt

from app.api.main import app
from app.db.models import User
from app.db import get_db

@pytest.fixture
def override_db():
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URI,
        connect_args={"check_same_thread": False},
        future=True,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(override_db):
    # Override Any Dependencies
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def example_users(override_db):
    try:
        override_db.add(
            User(
                email="alice@example.com",
                password_hash=hashpw("password123".encode('uft-8'), gensalt()),
                name="Alice Zhang",
                year="Sophomore",
                interests="Robotics,AI",
            )
        )
        override_db.commit()
    finally:
        override_db.close()


def test_login_success_returns_token_and_user(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["name"] == "Alice Zhang"
    assert data["user"]["year"] == "Sophomore"
    assert data["user"]["interests"] == ["Robotics", "AI"]


def test_login_invalid_password_returns_401(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrong-pass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_invalid_email_returns_401(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "unknown@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

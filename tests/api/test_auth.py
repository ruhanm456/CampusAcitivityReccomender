from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from CampusActivityReccomender.app.api.main import app, get_db
from CampusActivityReccomender.app.db.models import Base, User

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


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(
            User(
                email="alice@example.com",
                password_hash=generate_password_hash("password123"),
                name="Alice Zhang",
                year="Sophomore",
                interests="Robotics,AI",
            )
        )
        db.commit()
    finally:
        db.close()


def test_login_success_returns_token_and_user():
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


def test_login_invalid_password_returns_401():
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrong-pass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_invalid_email_returns_401():
    response = client.post(
        "/api/auth/login",
        json={"email": "unknown@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

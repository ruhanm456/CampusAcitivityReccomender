import os

os.environ["DATABASE_URL"] = "sqlite:///test_app.db"

from fastapi.testclient import TestClient
from app.api.main import abb
import jwt

SECRET_KEY = "devkey"

client = TestClient(abb)

def test_successful_user_registration():
    """Test successful user registration with valid data."""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "year": "Freshman",
        "major": "Computer Science",
        "interests": ["coding", "gaming"]
    }
    response = client.put("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == user_data["email"]
    assert data["user"]["name"] == user_data["name"]
    assert data["user"]["year"] == user_data["year"]
    assert data["user"]["interests"] == user_data["interests"]

def test_registration_fails_for_duplicate_email():
    """Test that registration fails when email already exists."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "name": "Test User",
        "year": "Freshman",
        "major": "Computer Science",
        "interests": ["coding"]
    }
    # First registration
    response1 = client.put("/auth/register", json=user_data)
    assert response1.status_code == 200
    
    # Second registration with same email
    response2 = client.put("/auth/register", json=user_data)
    assert response2.status_code == 409
    data = response2.json()
    assert "detail" in data
    assert "email already exists" in data["detail"].lower()

def test_successful_login():
    """Test successful login with correct credentials."""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "password": "password123",
        "name": "Login User"
    }
    client.put("/auth/register", json=user_data)
    
    # Now login
    login_data = {
        "email": "login@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data or "access_token" in data  # Depending on implementation

def test_login_fails_with_wrong_password():
    """Test login fails with incorrect password."""
    # Register a user
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpass",
        "name": "Wrong Pass User"
    }
    client.put("/auth/register", json=user_data)
    
    # Try login with wrong password
    login_data = {
        "email": "wrongpass@example.com",
        "password": "wrongpass"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "incorrect email or password" in data["detail"].lower()

def test_login_fails_with_unregistered_email():
    """Test login fails with email that doesn't exist."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "incorrect email or password" in data["detail"].lower()

def test_token_payload_structure():
    """Test that the JWT token has correct payload structure."""
    user_data = {
        "email": "token@example.com",
        "password": "password123",
        "name": "Token User"
    }
    response = client.put("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    
    # Decode the token
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert "sub" in payload  # User ID
    assert "email" in payload
    assert payload["email"] == user_data["email"]
    assert "exp" in payload  # Expiration
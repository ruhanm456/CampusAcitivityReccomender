import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
import bcrypt
import jwt

from app.db.models import Base, User
from config import Config

router = APIRouter()

# Pydantic models for registration
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    year: Optional[str] = None
    major: Optional[str] = None
    interests: Optional[list[str]] = None

class RegisterResponse(BaseModel):
    access_token: str
    user: dict

def validate_password(password: str) -> bool:
    """Validate password is at least 8 characters"""
    return len(password) >= 8

def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

@router.put("/register", response_model=RegisterResponse)
async def register(data: RegisterRequest):   
    # Validate password length
    if not validate_password(data.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
    
    # todo: check for email uniqueness

    # Hash the password
    password_hash = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # todo: insert actual user
    user_id = 1  # Would be returned from DB insert
    
    # Generate JWT token
    access_token = create_access_token(user_id, data.email)
    
    return RegisterResponse(
        access_token=access_token,
        user={
            "id": user_id,
            "email": data.email,
            "name": data.name,
            "year": data.year,
            "interests": data.interests or []
        }
    )

@router.post("/login")
async def login(email: str, password: str):
    # Actual database check will happen here. Currently providing an example:
    if email == "test@example.com" and password == "password123":
        return {
            "status": "success",
            "token": "fake-jwt-token-123", # This is the digital pass (token)
            "user": {"name": "Ruhan", "year": "Freshman"}
        }
    else:
        # Raise error if password or email is incorrect
        raise HTTPException(status_code=401, detail="Incorrect email or password!")



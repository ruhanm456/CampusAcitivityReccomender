from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import bcrypt
import jwt

from app.db.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db

# Load environment variables from .env file
SECRET_KEY = "devkey"

router = APIRouter()
Sesh = Annotated[Session, Depends(get_db)]

# Pydantic models for registration
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    year: Optional[str] = None
    major: Optional[str] = None
    interests: Optional[list[str]] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    year: Optional[str] = None
    interests: list[str]

class RegisterResponse(BaseModel):
    access_token: str
    user: UserResponse

class LoginResponse(BaseModel):
    access_token: str
    user: UserResponse

def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def serialize_interests(interests: Optional[list[str]]) -> Optional[str]:
    return ",".join(interests) if interests else None

def deserialize_interests(interests: Optional[str]) -> list[str]:
    if not interests:
        return []
    return [item for item in interests.split(",") if item]

@router.put("/register", response_model=RegisterResponse)
async def register(data: RegisterRequest, db: Sesh):   
    existing_user = db.execute(select(User).where(User.email == data.email)).scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    password_hash = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(
        email=data.email,
        password_hash=password_hash,
        name=data.name,
        year=data.year,
        major=data.major,
        interests=serialize_interests(data.interests),
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.id, user.email)

    return RegisterResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            year=user.year,
            interests=deserialize_interests(user.interests),
        )
    )

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Sesh):
    user = db.execute(select(User).where(User.email == data.email)).scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not bcrypt.checkpw(data.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user.id, user.email)
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            year=user.year,
            interests=deserialize_interests(user.interests),
        )
    )



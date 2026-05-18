<<<<<<< HEAD
from fastapi import FastAPI
from app.api.club_routes import router
=======
import base64
import hashlib
import hmac
import json
import time

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from .users import router as users_router
from ..db.models import User
from ..db.session import get_db
from CampusActivityReccomender.config import Config
>>>>>>> de069c8 (Tag vocabulary, user view point updated)

app = FastAPI()
app.include_router(users_router)

app.include_router(router)

@app.get("/")
def root():
    # todo: set up DB
    return {"message": "Server started"}

<<<<<<< HEAD
=======

def base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def create_access_token(payload: dict, secret_key: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload_with_claims = {
        **payload,
        "iat": int(time.time()),
    }
    encoded_header = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = base64url_encode(
        json.dumps(payload_with_claims, separators=(",", ":")).encode()
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(secret_key.encode(), signing_input, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def format_auth_user(user: User) -> dict:
    interests = [
        interest.strip()
        for interest in (user.interests or "").split(",")
        if interest.strip()
    ]
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name or "",
        "year": user.year or "",
        "interests": interests,
    }


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user


@app.post("/api/auth/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email},
        Config.SECRET_KEY,
    )

    return {
        "access_token": access_token,
        "user": format_auth_user(user),
    }


@app.post("/api/login")
async def login_legacy(data: LoginRequest, db: Session = Depends(get_db)):
    return await login(data, db)
>>>>>>> de069c8 (Tag vocabulary, user view point updated)

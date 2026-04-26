from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

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



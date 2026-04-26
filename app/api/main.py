from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from app.api.user_routes import router as user_router

app = FastAPI()

# Include user routes under /api/auth
app.include_router(user_router, prefix="/api/auth", tags=["auth"])

# User data model (Input format)
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
async def login(data: LoginRequest):
    # Actual database check will happen here. Currently providing an example:
    if data.email == "test@example.com" and data.password == "password123":
        return {
            "status": "success",
            "token": "fake-jwt-token-123", # This is the digital pass (token)
            "user": {"name": "Ruhan", "year": "Freshman"}
        }
    else:
        # Raise error if password or email is incorrect
        raise HTTPException(status_code=401, detail="Incorrect email or password!")

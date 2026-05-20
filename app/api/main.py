from fastapi import FastAPI

from app.api.club_routes import router as club_router
from app.api.users import router as users_router
from app.db import get_db

app = FastAPI()
app.include_router(users_router)
app.include_router(club_router)

@app.get("/")
def root():
    return {"message": "Server started"}

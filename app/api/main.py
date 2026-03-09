from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.models import User
from typing import Annotated

app = FastAPI()
= Session

@app.get("/")
def root():
    # set up DB
    return {"message": "Server started"}

@app.post("/clubs/create")
def create_club(name: str, description: str | None = None):
  pass
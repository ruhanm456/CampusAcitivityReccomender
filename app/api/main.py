from fastapi import FastAPI
from db.models import Session, User

app = FastAPI()

@app.get("/")
def root():
    # set up DB
    return {"message": "Server started"}

@app.post("/clubs/create")
def create_club(name: str, description: str | None = None):
  pass
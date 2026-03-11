from datetime import datetime
from typing import Annotated, Literal

from fastapi import FastAPI, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.db.models import Club

app = FastAPI()
Sesh = Annotated[Session, Depends(get_db)]

@app.get("/")
def root():
    # todo: set up DB
    return {"message": "Server started"}

class ClubCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)

class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)

class ClubOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    created_at: datetime

@app.post("/clubs", status_code=status.HTTP_201_CREATED, response_model=ClubOut)
def create_club(payload: ClubCreate, session: Sesh):
    club = Club(
        name=payload.name,
        description=payload.description,
    )
    session.add(club)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Club name already exists")
    session.refresh(club)
    return club

@app.get("/clubs/{club_id}", response_model=ClubOut)
def get_club(club_id: int, session: Sesh):
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    return club

@app.get("/clubs", response_model=list[ClubOut])
def list_clubs(
    session: Sesh,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = None,
    sort: Literal["name", "created_at"] = "created_at",
    order: Literal["asc", "desc"] = "asc",
):
    stmt = select(Club)
    if search:
        stmt = stmt.where(Club.name.ilike(f"%{search}%"))
    sort_col = Club.name if sort == "name" else Club.created_at
    stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col.asc())
    stmt = stmt.offset(offset).limit(limit)
    return list(session.scalars(stmt).all())

@app.put("/clubs/{club_id}", response_model=ClubOut)
def update_club(club_id: int, payload: ClubUpdate, session: Sesh):
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    if payload.name is not None:
        club.name = payload.name
    if payload.description is not None:
        club.description = payload.description
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Club name already exists")
    session.refresh(club)
    return club

@app.delete("/clubs/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(club_id: int, session: Sesh):
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    session.delete(club)
    session.commit()
    return None

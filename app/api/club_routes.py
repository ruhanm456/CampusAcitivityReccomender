from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db import get_db
from app.db.models import Club
from datetime import datetime
from typing import Annotated, Literal
from sqlalchemy.orm import Session
from loguru import logger
import sys

router = APIRouter()
Sesh = Annotated[Session, Depends(get_db)]

# Configure logging
logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
logger.add("club.log", rotation="10 MB", retention="1 week", level="INFO")


class ClubCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    tags: str | None = Field(default=None)
    meeting_time: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    members_count: int = Field(default=0, ge=0)

class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    tags: str | None = Field(default=None)
    meeting_time: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=200)
    members_count: int | None = Field(default=None, ge=0)

class ClubOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    tags: str | None
    meeting_time: str | None
    location: str | None
    members_count: int
    created_at: datetime

@router.post("/clubs", status_code=status.HTTP_201_CREATED, response_model=ClubOut)
def create_club(payload: ClubCreate, session: Sesh):
    logger.info(f"Creating club: {payload.name}")
    club = Club(**payload.model_dump())
    session.add(club)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning(f"Failed to create club due to name conflict: {payload.name}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Club name already exists")
    session.refresh(club)
    logger.info(f"Club created successfully: {club.id}")
    return club

@router.get("/clubs/{club_id}", response_model=ClubOut)
def get_club(club_id: int, session: Sesh):
    logger.info(f"Retrieving club: {club_id}")
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        logger.warning(f"Club not found: {club_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    logger.info(f"Club retrieved: {club_id}")
    return club

@router.get("/clubs", response_model=list[ClubOut])
def list_clubs(
    session: Sesh,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = None,
    sort: Literal["name", "created_at"] = "created_at",
    order: Literal["asc", "desc"] = "asc",
):
    logger.info(f"Listing clubs: limit={limit}, offset={offset}, search={search}, sort={sort}, order={order}")
    stmt = select(Club)
    if search:
        stmt = stmt.where(Club.name.ilike(f"%{search}%"))
    sort_col = Club.name if sort == "name" else Club.created_at
    stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col.asc())
    stmt = stmt.offset(offset).limit(limit)
    clubs = list(session.scalars(stmt).all())
    logger.info(f"Listed {len(clubs)} clubs")
    return clubs

@router.put("/clubs/{club_id}", response_model=ClubOut)
def update_club(club_id: int, payload: ClubUpdate, session: Sesh):
    logger.info(f"Updating club: {club_id}")
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        logger.warning(f"Club not found for update: {club_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(club, key, value)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning(f"Failed to update club due to name conflict: {club_id}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Club name already exists")
    session.refresh(club)
    logger.info(f"Club updated successfully: {club_id}")
    return club

@router.delete("/clubs/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(club_id: int, session: Sesh):
    logger.info(f"Deleting club: {club_id}")
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        logger.warning(f"Club not found for deletion: {club_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    session.delete(club)
    session.commit()
    logger.info(f"Club deleted successfully: {club_id}")
    return None

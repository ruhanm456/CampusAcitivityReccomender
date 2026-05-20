import sys
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from loguru import logger

from app.db import get_db
from app.db.models import (
    Club,
    ClubMember,
    Event,
    EventAttendance,
    User,
)

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


class MembershipRequest(BaseModel):
    user_id: int


class EventFeedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    club_name: str
    title: str
    start_time: datetime
    location: str | None
    attendee_count: int


class AttendRequest(BaseModel):
    user_id: int


class AttendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_id: int
    user_id: int
    attendee_count: int


@router.post("/api/clubs", status_code=status.HTTP_201_CREATED, response_model=ClubOut)
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


@router.get("/api/clubs/{club_id}", response_model=ClubOut)
def get_club(club_id: int, session: Sesh):
    logger.info(f"Retrieving club: {club_id}")
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        logger.warning(f"Club not found: {club_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    logger.info(f"Club retrieved: {club_id}")
    return club


@router.get("/api/clubs", response_model=list[ClubOut])
def list_clubs(
    session: Sesh,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = None,
    sort: str = "created_at",
    order: str = "asc",
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


@router.put("/api/clubs/{club_id}", response_model=ClubOut)
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


@router.delete("/api/clubs/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.post("/api/clubs/{club_id}/join", status_code=status.HTTP_201_CREATED)
def join_club(club_id: int, payload: MembershipRequest, session: Sesh):
    logger.info(f"User {payload.user_id} joining club {club_id}")
    club = session.scalar(select(Club).where(Club.id == club_id))
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    user = session.scalar(select(User).where(User.id == payload.user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    membership = ClubMember(user_id=payload.user_id, club_id=club_id)
    session.add(membership)
    club.members_count += 1
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already joined this club")
    session.refresh(membership)
    logger.info(f"User {payload.user_id} joined club {club_id}")
    return {"id": membership.id, "club_id": club_id, "user_id": payload.user_id, "joined_at": membership.joined_at}


@router.delete("/api/clubs/{club_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_club(club_id: int, session: Sesh, user_id: int = Query(...)):
    logger.info(f"User {user_id} leaving club {club_id}")
    membership = session.scalar(
        select(ClubMember).where(ClubMember.club_id == club_id, ClubMember.user_id == user_id)
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    club = session.scalar(select(Club).where(Club.id == club_id))
    if club and club.members_count > 0:
        club.members_count -= 1
    session.delete(membership)
    session.commit()
    logger.info(f"User {user_id} left club {club_id}")
    return None


@router.get("/api/users/{user_id}/joined-clubs", response_model=list[ClubOut])
def list_joined_clubs(user_id: int, session: Sesh):
    logger.info(f"Listing joined clubs for user {user_id}")
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    stmt = select(Club).join(ClubMember).where(ClubMember.user_id == user_id)
    clubs = list(session.scalars(stmt).all())
    logger.info(f"Found {len(clubs)} joined clubs for user {user_id}")
    return clubs


@router.get("/api/feed/events", response_model=list[EventFeedOut])
def feed_events(
    session: Sesh,
    user_id: int = Query(...),
    upcoming: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
):
    logger.info(f"Fetching feed events for user {user_id}: upcoming={upcoming}, limit={limit}")
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    stmt = select(Event).join(ClubMember, Event.club_id == ClubMember.club_id).where(ClubMember.user_id == user_id)
    if upcoming:
        stmt = stmt.where(Event.start_time >= datetime.now(timezone.utc))
    stmt = stmt.order_by(Event.start_time.asc()).limit(limit)
    events = session.scalars(stmt).all()

    feed = []
    for event in events:
        feed.append(
            EventFeedOut(
                id=event.id,
                club_name=event.club.name,
                title=event.title,
                start_time=event.start_time,
                location=event.location,
                attendee_count=len(event.attendances),
            )
        )
    logger.info(f"Returning {len(feed)} feed events for user {user_id}")
    return feed


@router.post("/api/events/{event_id}/attend", response_model=AttendResponse)
def attend_event(event_id: int, payload: AttendRequest, session: Sesh):
    logger.info(f"User {payload.user_id} attending event {event_id}")
    user = session.scalar(select(User).where(User.id == payload.user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    event = session.scalar(select(Event).where(Event.id == event_id))
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    attendance = EventAttendance(user_id=payload.user_id, event_id=event_id)
    session.add(attendance)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already attending this event")
    attendee_count = session.scalar(
        select(func.count(EventAttendance.id)).where(EventAttendance.event_id == event_id)
    )
    logger.info(f"User {payload.user_id} marked attending event {event_id}")
    return AttendResponse(event_id=event_id, user_id=payload.user_id, attendee_count=attendee_count or 0)

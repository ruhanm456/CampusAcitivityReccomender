from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, synonym

Base = declarative_base()

class VisibilityMode(PyEnum):
    public = "public"
    members_only = "members_only"
    domain_allowlist = "domain_allowlist"
    domain_blocklist = "domain_blocklist"

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    name: Mapped[str | None] = mapped_column(nullable=True)
    year: Mapped[str | None] = mapped_column(nullable=True)
    interests: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    owned_clubs: Mapped[list["Club"]] = relationship(
        secondary="club_owners", back_populates="owners"
    )
    memberships: Mapped[list["ClubMember"]] = relationship(
        "ClubMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    joined_clubs: Mapped[list["Club"]] = relationship(
        "Club",
        secondary="club_members",
        back_populates="member_users",
        viewonly=True,
    )
    event_attendances: Mapped[list["EventAttendance"]] = relationship(
        "EventAttendance",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class ClubOwner(Base):
    __tablename__ = "club_owners"

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

class ClubMember(Base):
    __tablename__ = "club_members"
    __table_args__ = (UniqueConstraint("user_id", "club_id", name="uq_club_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    club: Mapped["Club"] = relationship("Club", back_populates="members")

class Club(Base):
    __tablename__ = 'clubs'
    __table_args__ = (UniqueConstraint("name", name="uq_club_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    meeting_time: Mapped[str | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(nullable=True)
    members_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    owners: Mapped[list[User]] = relationship(
        secondary="club_owners", back_populates="owned_clubs"
    )
    members: Mapped[list[ClubMember]] = relationship(
        "ClubMember",
        back_populates="club",
        cascade="all, delete-orphan",
    )
    member_users: Mapped[list[User]] = relationship(
        "User",
        secondary="club_members",
        back_populates="joined_clubs",
        viewonly=True,
    )
    hosted_events: Mapped[list["Event"]] = relationship(
        back_populates="club",
        cascade="all, delete-orphan",
        foreign_keys="Event.club_id",
    )
    collaborations: Mapped[list["Collaboration"]] = relationship(
        "Collaboration",
        back_populates="club",
        cascade="all, delete-orphan",
    )

class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    host = synonym("club_id")
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=True)
    location: Mapped[str | None]
    is_online: Mapped[bool] = mapped_column(default=False, nullable=False)
    join_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    capacity: Mapped[int] = mapped_column(default=0, nullable=False)
    visibility_mode: Mapped[VisibilityMode] = mapped_column(
        SQLEnum(VisibilityMode, name="visibility_mode"), nullable=False, default=VisibilityMode.public
    )
    visible_email_domains: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
    club: Mapped["Club"] = relationship(
        back_populates="hosted_events",
        foreign_keys=[club_id],
    )
    collaborations: Mapped[list["Collaboration"]] = relationship(
        "Collaboration",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    attendances: Mapped[list["EventAttendance"]] = relationship(
        "EventAttendance",
        back_populates="event",
        cascade="all, delete-orphan",
    )

class EventAttendance(Base):
    __tablename__ = "event_attendances"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_attendance"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="event_attendances")
    event: Mapped["Event"] = relationship("Event", back_populates="attendances")

class Collaboration(Base):
    __tablename__ = "event_collaborations"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True
    )
    event: Mapped["Event"] = relationship(back_populates="collaborations")
    club: Mapped["Club"] = relationship(back_populates="collaborations")

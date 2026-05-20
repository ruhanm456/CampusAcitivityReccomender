import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, Club, ClubMember, User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    yield session
    session.close()


def test_club_member_created_with_joined_at(db_session):
    user = User(email="member@example.com", password_hash="hash", is_verified=True)
    club = Club(name="Study Group", description="Study together")
    db_session.add_all([user, club])
    db_session.commit()

    membership = ClubMember(user_id=user.id, club_id=club.id)
    db_session.add(membership)
    db_session.commit()

    retrieved = db_session.query(ClubMember).filter_by(user_id=user.id, club_id=club.id).first()
    assert retrieved is not None
    assert isinstance(retrieved.joined_at, datetime)
    joined_at = retrieved.joined_at
    if joined_at.tzinfo is None:
        joined_at = joined_at.replace(tzinfo=timezone.utc)
    assert joined_at <= datetime.now(timezone.utc)


def test_duplicate_club_member_raises_integrity_error(db_session):
    user = User(email="member2@example.com", password_hash="hash", is_verified=True)
    club = Club(name="Volunteer Club")
    db_session.add_all([user, club])
    db_session.commit()

    membership1 = ClubMember(user_id=user.id, club_id=club.id)
    db_session.add(membership1)
    db_session.commit()

    membership2 = ClubMember(user_id=user.id, club_id=club.id)
    db_session.add(membership2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_club_member_can_leave_club(db_session):
    user = User(email="member3@example.com", password_hash="hash", is_verified=True)
    club = Club(name="Art Club")
    db_session.add_all([user, club])
    db_session.commit()

    membership = ClubMember(user_id=user.id, club_id=club.id)
    db_session.add(membership)
    db_session.commit()

    db_session.delete(membership)
    db_session.commit()

    count = db_session.query(ClubMember).filter_by(user_id=user.id, club_id=club.id).count()
    assert count == 0

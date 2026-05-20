from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.models import Club, Event, ClubMember, User
from app.db.session import SessionLocal

client = TestClient(app)


def clear_db(session):
    session.query(ClubMember).delete()
    session.query(Event).delete()
    session.query(Club).delete()
    session.query(User).delete()
    session.commit()


def test_feed_events_returns_upcoming_sorted():
    session = SessionLocal()
    clear_db(session)

    user = User(email="feed@example.com", password_hash="hash", is_verified=True)
    club = Club(name="Science Club", description="Science events")
    session.add_all([user, club])
    session.commit()
    session.refresh(user)
    session.refresh(club)

    membership = ClubMember(user_id=user.id, club_id=club.id)
    session.add(membership)

    event1 = Event(
        club_id=club.id,
        title="Physics Seminar",
        start_time=datetime.now(timezone.utc) + timedelta(days=3),
        location="Hall A",
    )
    event2 = Event(
        club_id=club.id,
        title="Chemistry Lab Tour",
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        location="Lab B",
    )
    past_event = Event(
        club_id=club.id,
        title="Last week meetup",
        start_time=datetime.now(timezone.utc) - timedelta(days=4),
        location="Room 12",
    )
    session.add_all([event1, event2, past_event])
    session.commit()

    response = client.get(f"/api/feed/events", params={"user_id": user.id})
    assert response.status_code == 200
    feed = response.json()
    assert len(feed) == 2
    assert feed[0]["title"] == "Chemistry Lab Tour"
    assert feed[1]["title"] == "Physics Seminar"
    assert all(item["club_name"] == club.name for item in feed)

    session.close()


def test_feed_events_includes_past_when_upcoming_false():
    session = SessionLocal()
    clear_db(session)

    user = User(email="feed2@example.com", password_hash="hash", is_verified=True)
    club = Club(name="Drama Club")
    session.add_all([user, club])
    session.commit()
    session.refresh(user)
    session.refresh(club)

    session.add(ClubMember(user_id=user.id, club_id=club.id))
    session.add_all([
        Event(
            club_id=club.id,
            title="Past rehearsal",
            start_time=datetime.now(timezone.utc) - timedelta(days=2),
            location="Theater",
        ),
        Event(
            club_id=club.id,
            title="Future performance",
            start_time=datetime.now(timezone.utc) + timedelta(days=5),
            location="Main Stage",
        ),
    ])
    session.commit()

    response = client.get(f"/api/feed/events", params={"user_id": user.id, "upcoming": "false"})
    assert response.status_code == 200
    feed = response.json()
    assert any(event["title"] == "Past rehearsal" for event in feed)
    assert any(event["title"] == "Future performance" for event in feed)

    session.close()

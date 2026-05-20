from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.main import app
from app.db.models import Club, User, ClubMember, EventAttendance, Event
from app.db.session import SessionLocal

client = TestClient(app)


def clear_db(session: Session):
    session.query(ClubMember).delete()
    session.query(EventAttendance).delete()
    session.query(Event).delete()
    session.query(Club).delete()
    session.query(User).delete()
    session.commit()


def create_sample_user_and_club(session: Session):
    user = User(email="joiner@example.com", password_hash="hash", is_verified=True)
    club = Club(name="Garden Club", description="A community gardening club")
    session.add_all([user, club])
    session.commit()
    session.refresh(user)
    session.refresh(club)
    return user, club


def test_join_and_leave_club_endpoints():
    session = SessionLocal()
    clear_db(session)
    user, club = create_sample_user_and_club(session)

    join_response = client.post(f"/api/clubs/{club.id}/join", json={"user_id": user.id})
    assert join_response.status_code == 201
    assert join_response.json()["user_id"] == user.id
    assert join_response.json()["club_id"] == club.id

    joined_response = client.get(f"/api/users/{user.id}/joined-clubs")
    assert joined_response.status_code == 200
    clubs = joined_response.json()
    assert len(clubs) == 1
    assert clubs[0]["id"] == club.id

    leave_response = client.delete(f"/api/clubs/{club.id}/leave", params={"user_id": user.id})
    assert leave_response.status_code == 204

    joined_response_after = client.get(f"/api/users/{user.id}/joined-clubs")
    assert joined_response_after.status_code == 200
    assert joined_response_after.json() == []

    session.close()

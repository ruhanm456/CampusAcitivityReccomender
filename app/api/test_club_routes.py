import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.db.db import get_db
from app.db.models import Base

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def create_club(client: TestClient, name: str, description: str | None):
    payload = {"name": name, "description": description}
    return client.post("/clubs", json=payload)

def test_create_club_happy_path(client):
    res = create_club(client, "Testing Club", "We test things here!")
    assert res.status_code == 201
    body = res.json()
    assert body["id"] > 0
    assert body["name"] == "Testing Club"

def test_create_club_with_new_fields(client):
    payload = {
        "name": "Expanded Club",
        "description": "Club with extended metadata",
        "tags": "sports,outdoors",
        "meeting_time": "Tue 18:00",
        "location": "Building A Room 101",
        "members_count": 12,
    }
    res = client.post("/clubs", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "Expanded Club"
    assert body["tags"] == "sports,outdoors"
    assert body["meeting_time"] == "Tue 18:00"
    assert body["location"] == "Building A Room 101"
    assert body["members_count"] == 12

def test_update_club_with_new_fields(client):
    club = create_club(client, "Update Club", None).json()
    res = client.put(
        f"/clubs/{club['id']}",
        json={
            "tags": "academic,community",
            "meeting_time": "Wed 19:30",
            "location": "Community Center",
            "members_count": 30,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["tags"] == "academic,community"
    assert body["meeting_time"] == "Wed 19:30"
    assert body["location"] == "Community Center"
    assert body["members_count"] == 30

def test_create_club_invalid_payload(client):
    res = client.post("/clubs", json={"name": "", "description": ""})
    assert res.status_code == 422

def test_read_club_happy_path_and_not_found(client):
    create_res = create_club(client, "Chess Club", "Strategy games")
    club_id = create_res.json()["id"]

    res = client.get(f"/clubs/{club_id}")
    assert res.status_code == 200
    assert res.json()["id"] == club_id

    missing = client.get("/clubs/9999")
    assert missing.status_code == 404

def test_list_clubs_pagination_filter_sort(client):
    create_club(client, "Chess Club", None)
    create_club(client, "Art Club", None)
    create_club(client, "Math Society", None)

    page1 = client.get("/clubs?limit=2&offset=0&sort=name&order=asc")
    page2 = client.get("/clubs?limit=2&offset=2&sort=name&order=asc")
    assert page1.status_code == 200
    assert page2.status_code == 200
    assert len(page1.json()) == 2
    assert len(page2.json()) == 1

    filtered = client.get("/clubs?search=Club&sort=name&order=desc")
    assert filtered.status_code == 200
    names = [c["name"] for c in filtered.json()]
    assert names == ["Chess Club", "Art Club"]

def test_update_club_happy_path_not_found_forbidden_conflict(client):
    club1 = create_club(client, "Drama Club", None).json()
    club2 = create_club(client, "Science Club", None).json()

    ok = client.put(f"/clubs/{club1['id']}", json={"description": "Updated"})
    assert ok.status_code == 200
    assert ok.json()["description"] == "Updated"

    missing = client.put("/clubs/9999", json={"description": "Nope"})
    assert missing.status_code == 404

    conflict = client.put(
        f"/clubs/{club2['id']}",
        json={"name": club1["name"]},
    )
    assert conflict.status_code == 409

def test_delete_club_happy_path_and_repeat_delete(client):
    club = create_club(client, "Delete Me", None).json()

    res = client.delete(f"/clubs/{club['id']}")
    assert res.status_code == 204

    repeat = client.delete(f"/clubs/{club['id']}")
    assert repeat.status_code == 404

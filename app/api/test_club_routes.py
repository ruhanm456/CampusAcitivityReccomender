import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.api import main as api_main
from app.db import get_db
from app.db.models import Base

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    api_main.load_test_data = lambda: None
    api_main.check_test_data = lambda: None

    with TestClient(app) as client_instance:
        yield client_instance

    app.dependency_overrides.clear()


def create_club(client: TestClient, name: str, description: str | None):
    payload = {"name": name, "description": description}
    return client.post("/api/clubs", json=payload)

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
    res = client.post("/api/clubs", json=payload)
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
        f"/api/clubs/{club['id']}",
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
    res = client.post("/api/clubs", json={"name": "", "description": ""})
    assert res.status_code == 422

def test_read_club_happy_path_and_not_found(client):
    create_res = create_club(client, "Chess Club", "Strategy games")
    club_id = create_res.json()["id"]

    res = client.get(f"/api/clubs/{club_id}")
    assert res.status_code == 200
    assert res.json()["id"] == club_id

    missing = client.get("/api/clubs/9999")
    assert missing.status_code == 404

def test_list_clubs_pagination_filter_sort(client):
    create_club(client, "Pagination Club A", None)
    create_club(client, "Pagination Club B", None)
    create_club(client, "Pagination Club C", None)

    page1 = client.get("/api/clubs?search=Pagination&limit=2&offset=0&sort=name&order=asc")
    page2 = client.get("/api/clubs?search=Pagination&limit=2&offset=2&sort=name&order=asc")
    assert page1.status_code == 200
    assert page2.status_code == 200
    assert len(page1.json()) == 2
    assert len(page2.json()) == 1

    filtered = client.get("/api/clubs?search=Pagination&sort=name&order=desc")
    assert filtered.status_code == 200
    names = [c["name"] for c in filtered.json()]
    assert names == ["Pagination Club C", "Pagination Club B", "Pagination Club A"]

def test_update_club_happy_path_not_found_forbidden_conflict(client):
    club1 = create_club(client, "Drama Club", None).json()
    club2 = create_club(client, "Science Club", None).json()

    ok = client.put(f"/api/clubs/{club1['id']}", json={"description": "Updated"})
    assert ok.status_code == 200
    assert ok.json()["description"] == "Updated"

    missing = client.put("/api/clubs/9999", json={"description": "Nope"})
    assert missing.status_code == 404

    conflict = client.put(
        f"/api/clubs/{club2['id']}",
        json={"name": club1["name"]},
    )
    assert conflict.status_code == 409

def test_delete_club_happy_path_and_repeat_delete(client):
    club = create_club(client, "Delete Me", None).json()

    res = client.delete(f"/api/clubs/{club['id']}")
    assert res.status_code == 204

    repeat = client.delete(f"/api/clubs/{club['id']}")
    assert repeat.status_code == 404

def test_get_club_by_id_returns_full_details(client):
    """Test GET /api/clubs/{id} endpoint returns full club details with events and members"""
    payload = {
        "name": "Photography Club",
        "description": "Learn and share photography skills",
        "tags": "photography,art,creative",
        "meeting_time": "Friday 19:00",
        "location": "Room 205, Arts Building",
        "members_count": 24,
    }
    create_res = client.post("/api/clubs", json=payload)
    club_id = create_res.json()["id"]

    res = client.get(f"/api/clubs/{club_id}")
    assert res.status_code == 200
    body = res.json()
    
    # Verify basic club details
    assert body["id"] == club_id
    assert body["name"] == "Photography Club"
    assert body["description"] == "Learn and share photography skills"
    assert body["tags"] == "photography,art,creative"
    assert body["meeting_time"] == "Friday 19:00"
    assert body["location"] == "Room 205, Arts Building"
    assert body["members_count"] == 24
    assert "created_at" in body
    
    # Verify member_preview (first 5 members) is included
    assert "member_preview" in body
    assert isinstance(body["member_preview"], list)
    assert len(body["member_preview"]) <= 5

def test_get_club_members_endpoint_paginated(client):
    """Test GET /api/clubs/{id}/members endpoint returns paginated list of club members"""
    club = create_club(client, "Debate Club", "Competitive debate").json()
    club_id = club["id"]

    # Test with default pagination
    res = client.get(f"/api/clubs/{club_id}/members")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    
    # Test with limit and offset query parameters
    res_paginated = client.get(f"/api/clubs/{club_id}/members?limit=10&offset=0")
    assert res_paginated.status_code == 200
    assert isinstance(res_paginated.json(), list)

def test_get_club_members_not_found(client):
    """Test GET /api/clubs/{id}/members returns 404 for non-existent club"""
    res = client.get("/api/clubs/99999/members")
    assert res.status_code == 404

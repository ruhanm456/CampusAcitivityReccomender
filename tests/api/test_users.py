from fastapi.testclient import TestClient
from CampusActivityReccomender.app.api.main import app

client = TestClient(app)


def test_get_public_profile_returns_only_public_fields():
    response = client.get("/api/users/1/public-profile")
    assert response.status_code == 200
    json_data = response.json()

    assert json_data["id"] == 1
    assert json_data["name"] == "Alice Zhang"
    assert json_data["year"] == "Sophomore"
    assert json_data["major"] == "Computer Science"
    assert json_data["interests"] == ["Robotics", "AI", "Hackathons"]
    assert isinstance(json_data["joined_clubs"], list)
    assert json_data["medal_count"] == 3
    assert json_data["event_attendance_count"] == 12
    assert "email" not in json_data
    assert "password_hash" not in json_data


def test_search_users_filters_by_name():
    response = client.get("/api/users", params={"search": "Brandon"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Brandon Lee"
    assert data[0]["id"] == 2


def test_search_users_returns_all_when_no_query():
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_update_public_profile_returns_updated_fields():
    response = client.put(
        "/api/users/1/public-profile",
        data={
            "name": "Alice Updated",
            "year": "Senior",
            "major": "Computer Engineering",
            "interests": "Robotics, AI, Leadership",
        },
    )
    assert response.status_code == 200
    json_data = response.json()

    assert json_data["name"] == "Alice Updated"
    assert json_data["year"] == "Senior"
    assert json_data["major"] == "Computer Engineering"
    assert json_data["interests"] == ["Robotics", "AI", "Leadership"]
    assert "email" not in json_data
    assert "password_hash" not in json_data

    follow_up = client.get("/api/users/1/public-profile")
    assert follow_up.status_code == 200
    assert follow_up.json()["name"] == "Alice Updated"

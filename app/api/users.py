import base64
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from typing import List

router = APIRouter()

sample_users = [
    {
        "id": 1,
        "name": "Alice Zhang",
        "year": "Sophomore",
        "major": "Computer Science",
        "interests": ["Robotics", "AI", "Hackathons"],
        "joined_clubs": [
            {"id": 101, "name": "Robotics Club"},
            {"id": 102, "name": "AI Society"},
        ],
        "recent_events": [
            {"id": 201, "title": "Hackathon Kickoff", "date": "2026-05-01"},
            {"id": 202, "title": "AI Study Group", "date": "2026-04-22"},
            {"id": 203, "title": "Campus Volunteer Fair", "date": "2026-04-10"},
        ],
        "medal_count": 3,
        "event_attendance_count": 12,
        "email": "alice@example.com",
        "password_hash": "hashed-password-abc",
    },
    {
        "id": 2,
        "name": "Brandon Lee",
        "year": "Junior",
        "major": "Psychology",
        "interests": ["Volunteering", "Debate", "Mental Health"],
        "joined_clubs": [
            {"id": 103, "name": "Debate Club"},
            {"id": 104, "name": "Peer Support Network"},
        ],
        "recent_events": [
            {"id": 204, "title": "Debate Tournament", "date": "2026-03-18"},
            {"id": 205, "title": "Peer Support Training", "date": "2026-03-05"},
        ],
        "medal_count": 1,
        "event_attendance_count": 5,
        "email": "brandon@example.com",
        "password_hash": "hashed-password-def",
    },
]


def get_public_user(user: dict) -> dict:
    public_data = {
        "id": user["id"],
        "name": user["name"],
        "year": user["year"],
        "major": user["major"],
        "interests": user["interests"],
        "joined_clubs": user["joined_clubs"],
        "recent_events": user.get("recent_events", []),
        "medal_count": user["medal_count"],
        "event_attendance_count": user["event_attendance_count"],
    }
    if user.get("avatar_data"):
        public_data["avatar_data"] = user["avatar_data"]
        public_data["avatar_mime"] = user["avatar_mime"]
    return public_data


@router.get("/api/users/{user_id}/public-profile")
async def get_public_profile(user_id: int):
    user = next((user for user in sample_users if user["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return get_public_user(user)


@router.put("/api/users/{user_id}/public-profile")
async def update_public_profile(
    user_id: int,
    name: str | None = Form(None),
    year: str | None = Form(None),
    major: str | None = Form(None),
    interests: str | None = Form(None),
    avatar: UploadFile | None = File(None),
):
    user = next((user for user in sample_users if user["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if name is not None:
        user["name"] = name
    if year is not None:
        user["year"] = year
    if major is not None:
        user["major"] = major
    if interests is not None:
        user["interests"] = [
            interest.strip() for interest in interests.split(",") if interest.strip()
        ]
    if avatar is not None:
        content = await avatar.read()
        user["avatar_data"] = base64.b64encode(content).decode()
        user["avatar_mime"] = avatar.content_type or "application/octet-stream"

    return get_public_user(user)


@router.get("/api/users")
async def search_users(search: str | None = Query(None, description="Search users by name")) -> List[dict]:
    candidates = sample_users
    if search:
        search_lower = search.strip().lower()
        candidates = [
            user for user in candidates if search_lower in user["name"].lower()
        ]
    return [get_public_user(user) for user in candidates]

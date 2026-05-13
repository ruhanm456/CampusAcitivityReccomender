from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

abb = FastAPI()

allowed_origins = ["http://localhost:5173"]

abb.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import Routes
from app.api.user_routes import router as user_router
abb.include_router(user_router, prefix="/auth", tags=["auth"])

@abb.get("/")
async def root():
    # Load test data or perform any startup tasks here
    # load_test_data()
    # check_test_data()
    return {"message": "Welcome to the University Social Platform API!"}

def load_test_data():
    from app.db.models import User, Club #, Event
    from app.db import get_db
    import csv

    session = next(get_db())
    DATA_DIR = Path(__file__).parent / "tests" / "data"
    if not DATA_DIR.exists():
        print("No test data directory found; skipping load.")
        return

    model_map = {
        "users": User,
        "clubs": Club,
    }

    print(f"Loading test data from {DATA_DIR}")
    try:
        for p in DATA_DIR.glob("*.csv"):
            model = model_map.get(p.stem.lower())
            if model is None:
                print(f"Skipping unknown CSV file: {p.name}")
                continue
            with p.open() as f:
                r = csv.DictReader(f)
                for record in r:
                    session.add(model(**record))
            session.commit()
    finally:
        session.close()

def check_test_data():
    from sqlalchemy import select
    from app.db.models import User, Club
    from app.db import get_db

    session = next(get_db())
    users = session.execute(select(User)).scalars().all()
    print("Users:")
    for user in users:
        print(user)
    clubs = session.execute(select(Club)).scalars().all()
    print("Clubs:")
    for club in clubs:
        print(club)
    session.close()
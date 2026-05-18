from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_test_data()
    check_test_data()    
    yield # The server is now fully active and listening for requests

app = FastAPI(lifespan=lifespan)
allowed_origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    pass

# Import Routes
from app.api.user_routes import router as user_router
from app.api.club_routes import router as club_router
app.include_router(user_router, prefix="/auth", tags=["auth"])
app.include_router(club_router, prefix="/api", tags=["clubs"])

# Helper Functions
DATA_DIR = Path(__file__).parent.parent.parent / "tests" / "data"

def load_test_data():
    from app.db.models import User, Club #, Event
    from app.db import get_db
    import csv

    session = next(get_db())
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
                    record['created_at'] = datetime.strptime(record["created_at"], '%Y-%m-%dT%H:%M:%SZ')
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
    print("Users:", len(users))
    clubs = session.execute(select(Club)).scalars().all()
    print("Clubs:", len(clubs))
    session.close()
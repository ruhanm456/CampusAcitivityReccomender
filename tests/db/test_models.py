"""
Tests for database models.
TDD: Tests written first, then implementation follows.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import Base, User, Club


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestUserModel:
    """Tests for User model expansion (Task 1.1)."""

    def test_user_has_required_new_fields(self, db_session: Session):
        """Verify User model has new fields: name, year, major, interests."""
        # Create a user with all new fields
        user = User(
            email="alice@test.com",
            password_hash="hashed_pwd",
            is_verified=True,
            name="Alice Johnson",
            year="freshman",
            major="Computer Science",
            interests="academic_stem_tech,gaming",
        )
        db_session.add(user)
        db_session.commit()

        # Retrieve and verify
        retrieved = db_session.query(User).filter_by(email="alice@test.com").first()
        assert retrieved is not None
        assert retrieved.name == "Alice Johnson"
        assert retrieved.year == "freshman"
        assert retrieved.major == "Computer Science"
        assert retrieved.interests == "academic_stem_tech,gaming"

    def test_user_name_field_optional(self, db_session: Session):
        """Verify name field is optional (nullable)."""
        user = User(
            email="bob@test.com",
            password_hash="hashed_pwd",
            is_verified=False,
            # name intentionally omitted
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="bob@test.com").first()
        assert retrieved is not None
        assert retrieved.name is None

    def test_user_year_field_optional(self, db_session: Session):
        """Verify year field is optional."""
        user = User(
            email="charlie@test.com",
            password_hash="hashed_pwd",
            is_verified=False,
            # year intentionally omitted
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="charlie@test.com").first()
        assert retrieved is not None
        assert retrieved.year is None

    def test_user_major_field_optional(self, db_session: Session):
        """Verify major field is optional."""
        user = User(
            email="diana@test.com",
            password_hash="hashed_pwd",
            is_verified=False,
            # major intentionally omitted
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="diana@test.com").first()
        assert retrieved is not None
        assert retrieved.major is None

    def test_user_interests_field_optional(self, db_session: Session):
        """Verify interests field is optional."""
        user = User(
            email="eve@test.com",
            password_hash="hashed_pwd",
            is_verified=False,
            # interests intentionally omitted
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="eve@test.com").first()
        assert retrieved is not None
        assert retrieved.interests is None

    def test_user_year_field_stores_string(self, db_session: Session):
        """Verify year field stores and retrieves string values."""
        years = ["freshman", "sophomore", "junior", "senior", "other"]
        for idx, year in enumerate(years):
            user = User(
                email=f"user{idx}@test.com",
                password_hash="pwd",
                is_verified=True,
                year=year,
            )
            db_session.add(user)

        db_session.commit()

        for idx, year in enumerate(years):
            retrieved = db_session.query(User).filter_by(email=f"user{idx}@test.com").first()
            assert retrieved is not None
            assert retrieved.year == year

    def test_user_interests_comma_separated_values(self, db_session: Session):
        """Verify interests field can store comma-separated tag values."""
        interests = "academic_stem_tech,gaming,creative_arts"
        user = User(
            email="test@test.com",
            password_hash="pwd",
            is_verified=True,
            interests=interests,
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="test@test.com").first()
        assert retrieved is not None
        assert retrieved.interests == interests

    def test_user_full_profile_creation(self, db_session: Session):
        """Integration test: create a user with complete profile."""
        user = User(
            email="complete@test.com",
            password_hash="complex_hash_123",
            is_verified=True,
            name="Complete User",
            year="junior",
            major="Mathematics",
            interests="academic_stem_tech,service,politics",
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="complete@test.com").first()
        assert retrieved is not None
        assert retrieved.id is not None
        assert retrieved.email == "complete@test.com"
        assert retrieved.name == "Complete User"
        assert retrieved.year == "junior"
        assert retrieved.major == "Mathematics"
        assert retrieved.interests == "academic_stem_tech,service,politics"
        assert retrieved.is_verified is True
        assert isinstance(retrieved.created_at, datetime)

    def test_user_created_at_timestamp_set_automatically(self, db_session: Session):
        """Verify created_at is set automatically on user creation."""
        user = User(
            email="timestamp@test.com",
            password_hash="pwd",
            is_verified=False,
        )
        db_session.add(user)
        db_session.commit()

        retrieved = db_session.query(User).filter_by(email="timestamp@test.com").first()
        assert retrieved is not None
        assert retrieved.created_at is not None
        assert isinstance(retrieved.created_at, datetime)


class TestClubModel:
    """Tests ensure Club model still works (regression test)."""

    def test_club_has_required_fields(self, db_session: Session):
        """Verify Club model has expected fields."""
        club = Club(
            name="AI & Robotics Lab Club",
            description="Learn AI and robotics",
        )
        db_session.add(club)
        db_session.commit()

        retrieved = db_session.query(Club).filter_by(name="AI & Robotics Lab Club").first()
        assert retrieved is not None
        assert retrieved.id is not None
        assert retrieved.name == "AI & Robotics Lab Club"
        assert retrieved.description == "Learn AI and robotics"

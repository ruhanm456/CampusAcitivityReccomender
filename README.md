# Campus Activity Recommender – Progress Summary (as of 2025-11-15)

# 1. Overview

We are building a campus activity / club recommender where students (especially freshmen) can swipe through clubs and events, similar to a dating app UI:
• Students swipe right (like) or left (dislike) on clubs.
• The backend learns from swipes and improves recommendations over time.
• We plan to integrate with Google Calendar API later so users can see/join events in their calendar.
So far, we have:

1. A working Flask backend skeleton with a database and migrations.
1. A unified tag vocabulary for user interests and club categories.
1. A feature engineering pipeline that converts (user, club) into a fixed-length vector.
1. A first implementation of a LinUCB contextual bandit model and simple test scripts.

---

## 2. Backend Stack & Project Structure (High-level)

- Framework: FastAPI
- Database: SQLite (via SQLAlchemy)
- Migrations: Flask-Migrate (Alembic)

### Key files / directories:

- `main.py`
  <!-- - app/extensions.py – SQLAlchemy, Migrate instances. -->
  <!-- - app/models.py – User, Club, Swipe models. -->
- `app/recommendation/` (Recommendation-related code):
   <!-- - vocab.py – shared tag vocabulary.
   - utils.py – tag parsing helpers.
   - features.py – feature vector builder.
   - linucb.py – LinUCB agent implementation.
   - scripts/ – helper scripts:
   - seed.py – seed Users and Clubs.
   - test_features.py – sanity check for feature vectors.
   - test_linucb.py – sanity check for LinUCB behavior. -->

---

## 3. Data Model

Current tables:
User
• id (int, PK)
• email (string, unique, required)
• name (string, optional)
• year (string, e.g. "freshman", "sophomore", …)
• major (string, optional)
• interests (text, e.g. "academic_stem_tech,gaming,creative_arts")
• created_at (datetime)
Club
• id (int, PK)
• name (string, required)
• description (text)
• tags (text, e.g. "service,activism_environment")
• meeting_time (string, e.g. "Tue 18:00")
• location (string)
• created_at (datetime)
Swipe
• id (int, PK)
• user_id (FK → User.id)
• club_id (FK → Club.id)
• liked (boolean, True = like/right swipe, False = dislike/left swipe)
• created_at (datetime)
Swipe will be the main source of reward data for the bandit algorithm.

---

4. Tag System (10-tag Vocabulary)
   We defined a shared tag vocabulary used by both User.interests and Club.tags.
   This keeps feature engineering simple and enables tag-based similarity.
   Defined in app/recommendation/vocab.py as:
   TAG_VOCAB = [
   "academic_stem_tech",
   "business_career",
   "creative_arts",
   "sports",
   "gaming",
   "service",
   "activism_environment",
   "politics",
   "cultural",
   "faith",
   ]
   • User.interests and Club.tags are stored as comma-separated lists of these tags.
   • Examples:
   o User: "academic_stem_tech,gaming,creative_arts"
   o Club: "service,activism_environment"
   Tag parsing
   We implemented parse_tags(tag_string) in app/recommendation/utils.py:
   • Input: "academic_stem_tech,gaming,creative_arts"
   • Output: {"academic_stem_tech", "gaming", "creative_arts"}
   The function:
   • Splits on commas
   • Strips whitespace
   • Lowercases tokens
   • Keeps only tags that appear in TAG_VOCAB
   • Ignores unknown tags
   This parsed set is the basis for:
   • Multi-hot user/club tag vectors
   • Tag overlap / Jaccard similarity features

---

5. Feature Engineering for Recommendation
   We designed a function:
   phi = build_feature_vector(user, club)
   implemented in app/recommendation/features.py, which returns a 38-dimensional NumPy vector:
   Layout of φ(x, y)
1. User year one-hot (5 dims)
   o "freshman", "sophomore", "junior", "senior", "other"
1. User interests tags multi-hot (10 dims)
   o 0/1 per entry of TAG_VOCAB
1. Club tags multi-hot (10 dims)
   o 0/1 per entry of TAG_VOCAB
1. Meeting day one-hot (7 dims)
   o Monday–Sunday, parsed from Club.meeting_time (e.g. "Tue 18:00")
1. Meeting time bucket (3 dims)
   o Morning (0–11), afternoon (12–16), evening (17–23)
1. Tag overlap count (1 dim)
   o |user_tags ∩ club_tags|
1. Tag Jaccard similarity (1 dim)
   o |intersection| / |union| (0–1)
1. Bias term (1 dim)
   o Constant 1.0
   Total:
   5 + 10 + 10 + 7 + 3 + 1 + 1 + 1 = 38 dimensions.
   Sanity test
   We wrote scripts/test_features.py to:
   • Pick the first User and Club from the DB
   • Compute phi = build_feature_vector(user, club)
   • Print:
   o user info
   o club info
   o phi.shape
   o phi values
   Observed example output:
   === Test: build_feature_vector ===
   User: 1 / alice@example.com / year=freshman / interests=academic_stem_tech,gaming,creative_arts
   Club: 1 / AI & Robotics Lab Club / tags=academic_stem_tech / meeting_time=Tue 18:00

---

phi shape: (38,)
phi values: [...]
OK: feature vector has shape (38,)
This confirms:
• The feature layout is correct.
• The encoding (year, tags, meeting_time, overlap, Jaccard, bias) is working as intended.

---

6. LinUCB Algorithm Implementation
   We implemented a global LinUCB contextual bandit model in app/recommendation/linucb.py.
   Model structure
   For a given feature vector φ(x, y) ∈ ℝ^d (d=38):
   • Maintain:
   o A ∈ ℝ^{d×d} – design matrix (initialized to λI)
   o b ∈ ℝ^d – response vector (initialized to 0)
   • Estimate parameters:
   o theta_hat = A^{-1} b
   • For each candidate club (arm):
   o mean = φ^T theta_hat
   o var = sqrt(φ^T A^{-1} φ)
   o ucb = mean + alpha \* var (α is exploration parameter)
   When a swipe response is observed:
   • Reward r = 1.0 if liked, 0.0 if disliked
   • Update:
   o A ← A + φ φ^T
   o b ← b + r φ
   Class API
   class LinUCB:
   def **init**(self, dim: int, alpha: float = 1.0, lambda_reg: float = 1.0): ...
   def reset(self) -> None: ...
   def select_best(self, user, candidate_clubs: List) -> (club, score): ...
   def rank(self, user, candidate_clubs: List, top_k: int = 5) -> List[(club, score)]: ...
   def update(self, user, club, reward: float) -> None: ...
   We also created a convenience instance:
   GLOBAL_LINUCB = LinUCB(dim=38, alpha=1.0, lambda_reg=1.0)
   for simple usage in tests and later in API endpoints.

---

7. LinUCB Test Script
   We added scripts/test_linucb.py to validate LinUCB behavior.
   Test setup
   • Take the first User from the DB (e.g., Alice).
   • Take the first 5 Clubs as candidate arms.
   • Define a fake reward function:
   • reward = 1.0 if user_tags ∩ club_tags is non-empty
   • 0.0 otherwise
   • Run a loop of 10 rounds:
1. GLOBAL_LINUCB.select_best(user, candidate_clubs) to choose a club
1. Compute reward via the fake function
1. Call GLOBAL_LINUCB.update(user, club, reward)
1. Log the selected club, score, and reward
   Example output
   Testing LinUCB with user: 1 / alice@example.com / interests=academic_stem_tech,gaming,creative_arts
   Candidate clubs:

- 1: AI & Robotics Lab Club (tags=academic_stem_tech)
- 2: Startup & Entrepreneurship Circle (tags=business_career,academic_stem_tech)
- 3: Campus Jazz Band (tags=creative_arts)
- 4: Recreational Soccer Club (tags=sports)
- 5: Board Games & Tabletop Society (tags=gaming,creative_arts)

=== LinUCB test loop ===
Round 1: selected club 5 / Board Games & Tabletop Society, score=3.6667, reward=1.0
Round 2: selected club 2 / Startup & Entrepreneurship Circle, score=2.8989, reward=1.0
Round 3: selected club 4 / Recreational Soccer Club, score=2.7014, reward=0.0
Round 4: selected club 1 / AI & Robotics Lab Club, score=2.2005, reward=1.0
Round 5: selected club 3 / Campus Jazz Band, score=2.1568, reward=1.0
Round 6: selected club 5 / Board Games & Tabletop Society, score=1.9127, reward=1.0
Round 7: selected club 2 / Startup & Entrepreneurship Circle, score=1.8106, reward=1.0
Round 8: selected club 1 / AI & Robotics Lab Club, score=1.7481, reward=1.0
Round 9: selected club 3 / Campus Jazz Band, score=1.7233, reward=1.0
Round 10: selected club 5 / Board Games & Tabletop Society, score=1.6791, reward=1.0

Test finished.
Interpretation:
• The fake reward is 1 for clubs whose tags overlap with the user’s interests, 0 otherwise.
• The model briefly explores (e.g., tries the soccer club once, reward=0) and then shifts to exploiting clubs that yield reward=1 (AI/Robotics, Startup, Jazz Band, Board Games).
• Over time, the uncertainty term decreases, so the UCB scores shrink slightly but the relative ranking stabilizes on “good” clubs.
This confirms that:
• LinUCB is wired correctly to our features.
• Updates react sensibly to reward signals.

---

8. How to Run the Current Code
   From the project root:

# Activate venv

source campus_match_env/bin/activate

<!-- # Initialize / reset DB (only needed once or when schema/seed changes)

flask db upgrade
python -m scripts.seed

# Test feature vector

python -m scripts.test_features

# Test LinUCB behavior

python -m scripts.test_linucb -->

# Run the Flask dev server

```
# run in dev mode
uv run fastapi dev app/api/main.py
```

---

<!--
# 9. Next Steps

Suggested next steps for the recommendation & backend side:

1. API integration for recommendation
   o Implement an endpoint like GET /api/recommend:
    Input: current user ID (from session or query param)
    Logic: query candidate clubs, run LinUCB.rank(user, clubs, top_k=N)
    Output: JSON list of clubs (with basic info + maybe score for debugging)
1. API integration for swipe feedback
   o Implement POST /api/swipe:
    Input: user_id, club_id, liked (boolean)
    Logic:
    Create a Swipe row
    Convert liked to reward (1.0 or 0.0)
    Call GLOBAL_LINUCB.update(user, club, reward)
1. Front-end integration
   o Simple UI to:
    Show ranked clubs from /api/recommend
    Allow swipe/like/dislike actions that hit /api/swipe
1. (Later) Persistence of LinUCB state
   o Currently A and b live only in memory.
   o Optionally, serialize/deserialize A and b to the DB or a file so the model survives server restarts.
1. (Later) Google Calendar integration
   o Integrate Google Calendar API so users can:
    See upcoming club meetings/events
    Add events directly to their calendar.
1. Event Model and Database Migration
   We introduced an Event model to represent individual club events and support event-level visibility control.
   Event table (new):
   • id (int, PK)
   • club_id (FK → Club.id)
   • title (string, required)
   • description (text, optional)
   • start_time (datetime, required)
   • end_time (datetime, optional)
   • location (string, e.g. "Engineering Building Room 101" or "Online")
   • is_online (boolean, default False)
   • join_link (string, optional – Zoom/Meet URL, etc.)
   • capacity (int, optional – max attendees, nullable if unlimited)
   • visibility_mode (string, required, default "public")
   o Allowed values (by convention):
    "public" – visible to everyone
    "members_only" – visible only to club members (to be implemented)
    "domain_allowlist" – visible only to users from certain email domains
    "domain_blocklist" – visible to everyone except certain domains
   • visible_email_domains (text, optional)
   o Comma-separated domains, e.g. "albany.edu,kgu.ac.jp"
   o Normalized to lowercase, deduplicated, and comma-joined
   • created_at (datetime)
   • updated_at (datetime)
   We added this model to app/models.py, then created and applied a migration:
   flask db migrate -m "add events table"
   flask db upgrade
   This sets up the database to store events linked to clubs.

---

11. Event APIs and Blueprint Wiring
    We created a dedicated events blueprint and wired several REST endpoints for event CRUD and listing.
    Blueprint:
    • Defined in app/events/**init**.py as:
    • from flask import Blueprint
    •
    • events_bp = Blueprint("events", **name**)
    •
    • from . import routes # noqa
    • Registered in app/**init**.py:
    • from .events import events_bp
    • app.register_blueprint(events_bp, url_prefix="/api")
    This ensures all event routes live under the /api prefix.
    Endpoints (current):
    • POST /api/clubs/<int:club_id>/events
    Create a new event for a club.
    o Input JSON (fields are validated in the handler):
    o {
    o "title": "Intro to Robotics Kickoff",
    o "description": "...",
    o "start_time": "2025-09-20T18:00:00",
    o "end_time": "2025-09-20T20:00:00",
    o "location": "Engineering Building Room 101",
    o "is_online": false,
    o "join_link": null,
    o "capacity": 50,
    o "visibility_mode": "public",
    o "visible_email_domains": ["albany.edu", "kgu.ac.jp"]
    o }
    o The backend:
     Parses ISO8601 datetimes via parse_iso_datetime().
     Validates visibility_mode.
     Normalizes visible_email_domains into a comma-separated string.
     Creates and commits an Event row.
    • PUT /api/events/<int:event_id>
    Update an existing event (partial update, fields present in JSON are updated).
    • DELETE /api/events/<int:event_id>
    Delete an event.
    • GET /api/clubs/<int:club_id>/events
    Public listing of events for a club, with visibility filtering.
    o Logic:
     Query Event by club_id.
     Optionally filter for upcoming events based on ?upcoming=true.
     Filter events through a visibility helper:
     event_is_visible_to_user(event, user)
    (currently basic behavior; see below)
     Serialize each event with event_to_public_dict(event) (no internal visibility config in the response).
    • GET /api/clubs/<int:club_id>/events/manage
    Management view for club admins.
    o Returns all events for the club (ignoring visibility rules).
    o Uses event_to_dict(event) which includes visibility fields like visibility_mode and visible_email_domains.
    Serialization helpers (in app/events/routes.py):
    • event_to_public_dict(event)
    Returns only the user-facing fields:
    • {
    • "id": event.id,
    • "club_id": event.club_id,
    • "title": event.title,
    • "description": event.description,
    • "start_time": "...",
    • "end_time": "...",
    • "location": event.location,
    • "is_online": event.is_online,
    • "join_link": event.join_link,
    • "capacity": event.capacity,
    • }
    • event_to_dict(event)
    Includes all of the above plus internal visibility configuration:
    • {
    • ...
    • "visibility_mode": event.visibility_mode,
    • "visible_email_domains": ["albany.edu", "kgu.ac.jp"],
    • "created_at": "...",
    • "updated_at": "..."
    • }
    Visibility helpers (concept):
    We introduced a visibility helper in app/visibility.py (or equivalent):
    • event_is_visible_to_user(event, user):
    o mode == "public" → visible to everyone (including anonymous users).
    o mode == "domain_allowlist" → only users whose email domain is in visible_email_domains.
    o mode == "domain_blocklist" → all users except those in visible_email_domains.
    o mode == "members_only" → intended to check club membership (to be implemented).
    • user_can_manage_club(user, club_id):
    o Placeholder stub right now.
    o Later will check if the user is an officer/owner of the club.
    For development, the /events/manage endpoint currently skips @login_required and user_can_manage_club to simplify testing; proper auth/authorization will be added later.

---

12. Seeding Sample Events for Testing
    We extended scripts/seed.py to populate the database not only with Users and Clubs but also with realistic Events and a domain-based test user.
    New seeded user:
    • yusuke@albany.edu
    o year="freshman"
    o major="Computer Science"
    o interests="academic_stem_tech,activism_environment"
    o Used for testing domain-based visibility (albany.edu).
    Seeded events (examples):
    All events are linked to existing clubs seeded earlier (Club.id 1–4 in particular):
1. Intro to Robotics Kickoff (Club 1 – AI & Robotics Lab Club)
   o visibility_mode="public"
   o is_online=False
   o location="Engineering Building Room 101"
   o Start/end times set around an evening time slot.
   o Shows up for anyone calling GET /api/clubs/1/events.
1. Research Reading Group (CS Dept only) (Club 1)
   o visibility_mode="domain_allowlist"
   o visible_email_domains="albany.edu,kgu.ac.jp"
   o Intended to be visible only to students from these academic domains.
1. Founder AMA Night (Online) (Club 2 – Startup & Entrepreneurship Circle)
   o is_online=True, join_link="https://example.com/zoom-link"
   o visibility_mode="public".
1. Jazz Jam Session (Campus-only) (Club 3 – Campus Jazz Band)
   o visibility_mode="domain_blocklist"
   o visible_email_domains="gmail.com,yahoo.com"
   o Simple example of blocking generic email domains while keeping campus emails visible.
1. Pick-up Soccer Game (Club 4 – Recreational Soccer Club)
   o Simple public sports event with no capacity limit (capacity=None).
   After updating seed.py, we run:
   python -m scripts.seed
   and verify via Flask shell:
   from app.models import Event, Club
   Event.query.all() # -> 5+ events
   Club.query.all() # -> 10 clubs

---

13. Local Dev Notes (Ports, curl, and macOS AirPlay)
    While testing the API locally on macOS, port 5000 turned out to be already in use by an AirPlay/AirTunes service. Symptoms:
    • curl http://localhost:5000/... returned:
    o HTTP/1.1 403 Forbidden
    o Server: AirTunes/770.8.1
    • No logs appeared in the Flask server terminal.
    Resolution:
    • Switched the Flask dev server to port 5001 and bound explicitly to 127.0.0.1 in run.py:
    • from app import create_app
    •
    • app = create_app()
    •
    • if **name** == "**main**":
    • app.run(debug=True, host="127.0.0.1", port=5001)
    • Now we use:
    • curl -v http://127.0.0.1:5001/api/clubs/1/events
    and see:
    o HTTP/1.1 200 OK
    o Server: Werkzeug/...
    o A JSON list of events (e.g., Intro to Robotics Kickoff).
    This confirms that the event endpoints and seed data are working correctly on the new port.

---

14. Next Steps for Events & Auth
    Short-term next steps around events and authentication:
1. Integrate Flask-Login properly
   o Add LoginManager to app/extensions.py.
   o Initialize it in create_app via login_manager.init_app(app).
   o Make User inherit from UserMixin and define @login_manager.user_loader.
   o Re-enable @login_required on management and mutation endpoints:
    POST /api/clubs/<club_id>/events
    PUT /api/events/<event_id>
    DELETE /api/events/<event_id>
    GET /api/clubs/<club_id>/events/manage
1. Implement user_can_manage_club
   o Decide on a simple permission model:
    e.g., an is_admin flag or a ClubMembership table with a role field.
   o Use this in event management endpoints to restrict creation/edit/delete to authorized users.
1. Refine visibility logic
   o Finalize semantics for:
    "members_only"
    "domain_allowlist" / "domain_blocklist"
   o Decide what happens for anonymous users (no login) for each mode.
   o Add unit tests for visibility behavior.
1. Expose events in the recommendation pipeline (future)
   o Extend feature engineering to support event-level recommendation:
    Use club tags + time features + event-specific attributes.
   o Consider recommending:
    Clubs (as now)
    Upcoming events from those clubs
   o Explore using LinUCB or a separate bandit for events vs clubs.
-->

# Campus Event Recommender – Implementation Tasks

**Estimated Timeline:** 4–8 weeks (MVP, Phases 1–6), 10–14 weeks (with advanced features, Phases 1–7)  
**Status:** 🟡 Planning  
**Collaborators:** (Add names here)

---

## ✅ Phase 1: Database & Data Model Foundation (Weeks 1–1.5)

**Objective:** Establish complete database schema and seed data for all downstream work.

### Task 1.1: Expand User Model

- **Description:** Add missing fields to User model in `app/db/models.py`
- **Acceptance Criteria:**
  - [ ] Add fields: `name` (string), `year` (string), `major` (string), `interests` (text)
  - [ ] `year` field validates against: freshman, sophomore, junior, senior, other
  - [ ] `interests` field stores comma-separated tag list
  - [ ] All fields have sensible defaults or are optional
  - [ ] Model compiles without errors
- **Notes:** Don't migrate yet; wait for batch migration

- **Depends on:** None

### Task 1.2: Expand Club Model

- **Description:** Add missing fields to Club model in `app/db/models.py`
- **Acceptance Criteria:**
  - [ ] Add fields: `tags` (text), `meeting_time` (string), `location` (string), `members_count` (int)
  - [ ] `tags` field stores comma-separated tag list (validate against vocabulary later)
  - [ ] `meeting_time` format: "Tue 18:00" or similar
  - [ ] `members_count` defaults to 0
  - [ ] Model compiles without errors
- **Notes:** Coordinate with Task 1.1

- **Depends on:** None

### Task 1.3: Implement Swipe Model

- **Description:** Create Swipe model in `app/db/models.py` for tracking user-club interactions
- **Acceptance Criteria:**
  - [ ] Model has fields: `id` (PK), `user_id` (FK), `club_id` (FK), `liked` (boolean), `created_at` (datetime)
  - [ ] Foreign key constraints enforced (cascade delete on user/club)
  - [ ] Composite unique constraint: `(user_id, club_id)` or allow re-swiping?
  - [ ] Indexes on `user_id`, `club_id` for query performance
  - [ ] Model compiles and table creation works
- **Notes:** This table is **critical** for LinUCB reward signals. Re-swiping decision: default = allow new swipes (update existing or create new?)

- **Depends on:** Task 1.1, Task 1.2

### Task 1.4: Create Event Model (Optional bonus)

- **Description:** Add Event model for storing club events (optional for MVP, but in README scope)
- **Acceptance Criteria:**
  - [ ] Model has fields: `id`, `club_id` (FK), `title`, `description`, `start_time`, `end_time`, `location`, `is_online`, `join_link`, `capacity`, `visibility_mode`, `visible_email_domains`, `created_at`, `updated_at`
  - [ ] `visibility_mode` enum: public, members_only, domain_allowlist, domain_blocklist
  - [ ] `visible_email_domains` stored as comma-separated text
  - [ ] Model compiles
- **Notes:** Can skip if time-constrained; not needed for core swipe loop

- **Depends on:** Task 1.2

### Task 1.5: Set Up Database Migrations

- **Description:** Create and run migrations for new/updated tables
- **Acceptance Criteria:**
  - [ ] Use Alembic to create migration scripts (or manually via SQLAlchemy if no Alembic)
  - [ ] Migrations for User, Club expansions
  - [ ] Migration for Swipe table
  - [ ] Migration for Event table (if implementing Task 1.4)
  - [ ] All migrations run successfully: `alembic upgrade head` or equivalent
  - [ ] `sqlite3 app.db ".schema"` shows all tables with correct columns
- **Notes:** Coordinate with Tasks 1.1–1.4 for schema finalization

- **Depends on:** Task 1.1, Task 1.2, Task 1.3, Task 1.4

### Task 1.6: Create Seed Data Script

- **Description:** Implement `scripts/seed.py` to populate test database
- **Acceptance Criteria:**
  - [ ] Script creates 20–30 realistic clubs with:
    - [ ] Name, description, tags, meeting_time, location
    - [ ] Sample data includes all 10 tag vocabulary items
  - [ ] Script creates 5–10 test users with:
    - [ ] Email, name, year, major, interests (varied profiles)
    - [ ] Example: alice@test.com (freshman, STEM interests), bob@test.com (senior, business interests)
  - [ ] Script includes: delete existing records, create fresh seed (idempotent)
  - [ ] Script runs without errors: `python -m scripts.seed`
  - [ ] Verify: `SELECT COUNT(*) FROM user; SELECT COUNT(*) FROM club;` shows expected counts
- **Notes:** Use tag vocabulary from README; keep meeting times realistic

- **Depends on:** Task 1.5

### Task 1.7: Verify Database Schema

- **Description:** Write quick verification script to confirm all tables/columns exist
- **Acceptance Criteria:**
  - [ ] Script queries each table and prints column names
  - [ ] Script runs: `python -m scripts.verify_db`
  - [ ] Output confirms: User (id, email, password_hash, name, year, major, interests, created_at), Club (id, name, description, tags, meeting_time, location, members_count, created_at), Swipe (id, user_id, club_id, liked, created_at)
  - [ ] No errors on initial schema check
- **Notes:** Quick sanity check before moving to Phase 2

- **Depends on:** Task 1.6

---

## ✅ Phase 2: Authentication & User API (Weeks 1.5–2.5)

**Objective:** Implement secure user registration, login, JWT auth, and preference updates.

### Task 2.1: Implement User Registration Endpoint

- **Description:** Create `POST /api/auth/register` endpoint in `app/api/main.py`
- **Acceptance Criteria:**
  - [ ] Endpoint accepts JSON: `{ email, password, name, year, major, interests }`
  - [ ] Validates: email format (RFC 5322), email uniqueness, password length (≥8 chars)
  - [ ] Hashes password with werkzeug.security: `generate_password_hash(password)`
  - [ ] Creates User row in database
  - [ ] Returns: `{ access_token, user: { id, email, name, year, interests } }`
  - [ ] Returns 409 Conflict if email already exists
  - [ ] Returns 400 Bad Request if validation fails
  - [ ] Test with curl: `curl -X POST http://localhost:8000/api/auth/register ...` succeeds
- **Notes:** Use `fastapi.security` for JWT if available; else use `PyJWT` package

- **Depends on:** Task 1.1

### Task 2.2: Implement User Login Endpoint

- **Description:** Update/replace hardcoded `POST /api/auth/login` with real User lookup
- **Acceptance Criteria:**
  - [ ] Endpoint accepts JSON: `{ email, password }`
  - [ ] Queries User table by email
  - [ ] Validates password hash with `werkzeug.security.check_password_hash()`
  - [ ] Returns: `{ access_token, user: { id, email, name, year, interests } }` on success
  - [ ] Returns 401 Unauthorized if email not found or password incorrect
  - [ ] No plaintext passwords in logs or responses
  - [ ] Test with curl: successful login returns token
- **Notes:** Coordinate with Task 2.1 on JWT format

- **Depends on:** Task 1.1, Task 2.1

### Task 2.3: Implement JWT Validation & `get_current_user()` Dependency

- **Description:** Create JWT middleware in `app/api/auth.py` for protecting endpoints
- **Acceptance Criteria:**
  - [ ] Create function `get_current_user(token: str = Depends(HTTPBearer()))` that:
    - [ ] Decodes JWT token (using `PyJWT` or FastAPI built-in)
    - [ ] Extracts user_id from token payload
    - [ ] Queries User by ID
    - [ ] Returns User object
  - [ ] Raises 401 if token invalid/expired or user not found
  - [ ] Raises 403 if token missing
  - [ ] All protected endpoints use `Depends(get_current_user)` to get current user
  - [ ] Test: valid token works, expired/invalid token rejected
- **Notes:** Token expiration: recommend 1 hour for access tokens; add refresh tokens later if needed

- **Depends on:** Task 2.2

### Task 2.4: Implement User Preference Update Endpoint

- **Description:** Create `PUT /api/users/<user_id>/preferences` endpoint
- **Acceptance Criteria:**
  - [ ] Endpoint accepts JSON: `{ interests }` (comma-separated tag list)
  - [ ] Requires JWT auth (uses `get_current_user`)
  - [ ] Only user can update their own preferences (check `user.id == user_id`)
  - [ ] Validates interests against tag vocabulary (Task 3.1 needed, or skip validation for now)
  - [ ] Updates User.interests in database
  - [ ] Returns updated user object
  - [ ] Returns 403 if user tries to update another user's preferences
  - [ ] Test: can update own interests, cannot update others'
- **Notes:** May need to coordinate with Task 3.1 for tag validation

- **Depends on:** Task 2.3

### Task 2.5: Create Authentication Tests

- **Description:** Write pytest tests for auth endpoints in `tests/api/test_auth.py`
- **Acceptance Criteria:**
  - [ ] Test successful registration
  - [ ] Test registration with duplicate email (409)
  - [ ] Test registration with invalid email (400)
  - [ ] Test successful login
  - [ ] Test login with wrong password (401)
  - [ ] Test login with non-existent user (401)
  - [ ] Test protected endpoint with valid token (200)
  - [ ] Test protected endpoint with invalid token (401)
  - [ ] Test user preference update: own user (200), other user (403)
  - [ ] All tests pass: `pytest tests/api/test_auth.py -v`
- **Notes:** Use FastAPI TestClient for integration tests

- **Depends on:** Task 2.4

---

## ✅ Phase 3: Club & Swipe API (Weeks 2–3)

**Objective:** Implement endpoints for listing clubs and recording swipes.

### Task 3.1: Implement Club Listing Endpoint

- **Description:** Create `GET /api/clubs` endpoint
- **Acceptance Criteria:**
  - [ ] Endpoint querys Club table, returns all clubs
  - [ ] Response format: `{ clubs: [ { id, name, description, tags, meeting_time, location, members_count }, ... ] }`
  - [ ] Optional query params:
    - [ ] `?tags=academic_stem_tech,gaming` (filter by tags)
    - [ ] `?meeting_day=Tuesday` (filter by meeting day)
  - [ ] Pagination (optional): `?limit=10&offset=0`
  - [ ] Returns 200 with club list
  - [ ] Test: `curl http://localhost:8000/api/clubs` returns JSON array
- **Notes:** Can start simple (no filters); add filtering in Phase 5 if needed

- **Depends on:** Task 1.2

### Task 3.2: Implement Swipe Endpoint

- **Description:** Create `POST /api/swipes` endpoint to record user-club interactions
- **Acceptance Criteria:**
  - [ ] Endpoint accepts JSON: `{ club_id, liked }` (user_id from JWT)
  - [ ] Requires JWT auth
  - [ ] Creates Swipe row: `Swipe(user_id=current_user.id, club_id=club_id, liked=liked)`
  - [ ] **Triggers LinUCB update** (see Phase 4, Task 4.5): parse feature vector, call `GLOBAL_LINUCB.update()`
  - [ ] Returns: `{ swipe_id, reward }` (reward = 1.0 if liked, 0.0 if disliked)
  - [ ] Returns 400 if club_id invalid
  - [ ] Returns 404 if club not found
  - [ ] Test: create swipe via POST, verify Swipe row in DB
- **Notes:** **Important:** This endpoint must integrate with LinUCB (Phase 4). For now, can log reward without LinUCB; add real update in Task 4.5

- **Depends on:** Task 1.3, Task 2.3, Task 4.5 (later)

### Task 3.3: Implement Swipe History Endpoint

- **Description:** Create `GET /api/users/<user_id>/swipes` endpoint
- **Acceptance Criteria:**
  - [ ] Returns all swipes for a user: `{ swipes: [ { id, club_id, liked, created_at }, ... ] }`
  - [ ] Requires JWT auth
  - [ ] Only user can view their own swipes (check user_id match)
  - [ ] Optional: `?liked=true` to filter
  - [ ] Returns 200 with swipe list
  - [ ] Test: create swipes, retrieve via endpoint, verify count
- **Notes:** Useful for debugging and user stats

- **Depends on:** Task 3.2, Task 2.3

### Task 3.4: Create Swipe API Tests

- **Description:** Write pytest tests for swipe endpoints in `tests/api/test_swipes.py`
- **Acceptance Criteria:**
  - [ ] Test create swipe: success (200)
  - [ ] Test create swipe: invalid club (400)
  - [ ] Test create swipe: without auth (401)
  - [ ] Test swipe history: own user (200), other user (403)
  - [ ] Test swipe history: empty list if no swipes
  - [ ] Verify Swipe rows created in DB
  - [ ] All tests pass: `pytest tests/api/test_swipes.py -v`
- **Notes:** \_

- **Depends on:** Task 3.3

---

## ✅ Phase 4: Recommendation Engine (Weeks 3–5)

**Objective:** Implement LinUCB contextual bandit algorithm and integrate with swipe feedback.

### Task 4.1: Implement Tag Vocabulary

- **Description:** Create `app/recommendation/vocab.py` with shared tag constants
- **Acceptance Criteria:**
  - [ ] Define `TAG_VOCAB = ["academic_stem_tech", "business_career", "creative_arts", "sports", "gaming", "service", "activism_environment", "politics", "cultural", "faith"]`
  - [ ] Define `TAG_INDEX = { tag: idx for idx, tag in enumerate(TAG_VOCAB) }`
  - [ ] Function: `get_tag_index(tag: str) -> int` (raises KeyError if tag not in vocab)
  - [ ] Function: `is_valid_tag(tag: str) -> bool`
  - [ ] File imports without error: `from app.recommendation.vocab import TAG_VOCAB`
- **Notes:** This is the single source of truth for all tag-related code

- **Depends on:** None

### Task 4.2: Implement Tag Utilities

- **Description:** Create `app/recommendation/utils.py` with tag parsing and vector conversion
- **Acceptance Criteria:**
  - [ ] Function: `parse_tags(tag_string: str) -> Set[str]`
    - [ ] Input: "academic_stem_tech,gaming,creative_arts"
    - [ ] Output: set of valid tags (lowercase, stripped)
    - [ ] Ignores invalid tags (not in TAG_VOCAB)
    - [ ] Handles empty strings, extra whitespace
  - [ ] Function: `tags_to_vector(tags: Set[str]) -> np.ndarray`
    - [ ] Output: 10-dim binary vector (one-hot for each tag in vocab)
    - [ ] Example: `{academic_stem_tech, gaming}` → `[1, 0, 0, 0, 1, 0, 0, 0, 0, 0]`
  - [ ] Both functions tested: `python -c "from app.recommendation.utils import ..."`
- **Notes:** Coordinate with Task 4.1 for TAG_VOCAB usage

- **Depends on:** Task 4.1

### Task 4.3: Implement Feature Engineering

- **Description:** Create `app/recommendation/features.py` with feature vector builder
- **Acceptance Criteria:**
  - [ ] Function: `build_feature_vector(user: User, club: Club) -> np.ndarray`
  - [ ] Output: 38-dim vector with:
    - [ ] User year one-hot (5 dims)
    - [ ] User interests tags multi-hot (10 dims)
    - [ ] Club tags multi-hot (10 dims)
    - [ ] Meeting day one-hot (7 dims, parsed from "Tue 18:00")
    - [ ] Meeting time bucket (3 dims: morning/afternoon/evening)
    - [ ] Tag overlap count (1 dim)
    - [ ] Tag Jaccard similarity (1 dim)
    - [ ] Bias term (1 dim) = 1.0
  - [ ] Vector shape: `(38,)` with dtype float32 or float64
  - [ ] Test: `phi = build_feature_vector(user, club); assert phi.shape == (38,)`
  - [ ] Verify manually: print a sample feature vector
- **Notes:** Reference README for exact layout. Use numpy for efficiency

- **Depends on:** Task 4.2, Task 1.1, Task 1.2

### Task 4.4: Implement LinUCB Algorithm

- **Description:** Create `app/recommendation/linucb.py` with LinUCB contextual bandit
- **Acceptance Criteria:**
  - [ ] Class: `LinUCB(dim: int, alpha: float = 1.0, lambda_reg: float = 1.0)`
  - [ ] Methods:
    - [ ] `__init__`: initialize A = λI, b = 0
    - [ ] `select_best(user: User, candidates: List[Club]) -> Tuple[Club, float]`: returns best arm and UCB score
    - [ ] `rank(user: User, candidates: List[Club], top_k: int = 5) -> List[Tuple[Club, float]]`: returns top-k by UCB score
    - [ ] `update(user: User, club: Club, reward: float) -> None`: update A and b after observing reward
    - [ ] `reset() -> None`: reinitialize A and b
  - [ ] Algorithm logic (from README):
    - [ ] UCB score = θ^T φ + α √(φ^T A^{-1} φ)
    - [ ] On update: A ← A + φ φ^T, b ← b + r φ
  - [ ] Global instance: `GLOBAL_LINUCB = LinUCB(dim=38, alpha=1.0, lambda_reg=1.0)`
  - [ ] Handles numerical stability: avoid singular matrices (lambda_reg helps)
  - [ ] Test: `from app.recommendation.linucb import GLOBAL_LINUCB`
- **Notes:** Use numpy.linalg for matrix operations; handle edge cases (no candidates, etc.)

- **Depends on:** Task 4.3

### Task 4.5: Integrate Swipe → LinUCB Update

- **Description:** Hook swipe endpoint (Task 3.2) to trigger LinUCB update
- **Acceptance Criteria:**
  - [ ] In `POST /api/swipes` handler:
    - [ ] After creating Swipe row, fetch fresh user and club objects
    - [ ] Call `build_feature_vector(user, club)` to get φ
    - [ ] Compute reward: `1.0 if liked else 0.0`
    - [ ] Call `GLOBAL_LINUCB.update(user, club, reward)`
  - [ ] No crashes on update (handle edge cases)
  - [ ] Log update for debugging: `logger.info(f"Updated LinUCB: user {user.id}, club {club.id}, reward {reward}")`
  - [ ] Test: create 5 swipes, verify no errors
- **Notes:** This task completes Task 3.2; do together or immediately after 3.2

- **Depends on:** Task 3.2, Task 4.1, Task 4.2, Task 4.3, Task 4.4

### Task 4.6: Implement Recommendation Endpoint

- **Description:** Create `GET /api/recommend` endpoint
- **Acceptance Criteria:**
  - [ ] Endpoint requires JWT auth (uses `get_current_user`)
  - [ ] Query params: `?top_k=5` (number of recommendations, default 5)
  - [ ] Logic:
    - [ ] Fetch current user
    - [ ] Fetch all clubs from DB (or unswiped clubs only; decision per collaborators)
    - [ ] Call `GLOBAL_LINUCB.rank(user, clubs, top_k)`
    - [ ] Return: `{ clubs: [ { id, name, description, tags, meeting_time, score }, ... ] }` (sorted by score desc)
  - [ ] Score included for debugging (can hide in production)
  - [ ] Returns 200 with club list
  - [ ] Test: `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/recommend?top_k=5`
- **Notes:** Decision: filter unswiped clubs only, or show all? Default = all clubs for now

- **Depends on:** Task 4.4, Task 4.5

### Task 4.7: Create Recommendation Tests

- **Description:** Write pytest tests for feature engineering and LinUCB in `tests/recommendation/`
- **Acceptance Criteria:**
  - [ ] `test_features.py`:
    - [ ] Test `build_feature_vector` shape: `(38,)`
    - [ ] Test with sample user/club: verify feature values are 0/1 or reasonable
    - [ ] Test tag parsing and encoding
  - [ ] `test_linucb.py`:
    - [ ] Test initialization: A, b shapes
    - [ ] Test `select_best` returns a club
    - [ ] Test `rank` returns top-k sorted by score
    - [ ] Test `update`: verify A and b change after update
    - [ ] Test multiple updates: model should converge on high-reward arms
  - [ ] `test_utils.py`:
    - [ ] Test `parse_tags`: valid/invalid tags, edge cases
    - [ ] Test `tags_to_vector`: shape, one-hot encoding
  - [ ] All tests pass: `pytest tests/recommendation/ -v`
- **Notes:** Use fixtures for sample users/clubs

- **Depends on:** Task 4.1–4.6

### Task 4.8: Create Integration Test: Swipe → Recommendation Loop

- **Description:** Write end-to-end test simulating user swipes and improving recommendations
- **Acceptance Criteria:**
  - [ ] Test file: `tests/integration/test_recommendation_loop.py`
  - [ ] Setup: create test user + 10 test clubs with varied tags
  - [ ] Loop: 10 rounds of:
    - [ ] Call `GET /api/recommend` to get top club
    - [ ] Create swipe with fake reward (e.g., 1.0 if tag overlap, 0.0 otherwise)
    - [ ] Verify recommendation scores change over time
  - [ ] Assert: high-reward clubs score higher in later rounds
  - [ ] Test passes: `pytest tests/integration/test_recommendation_loop.py -v`
- **Notes:** Validates the entire feedback loop works end-to-end

- **Depends on:** Task 4.6

---

## ✅ Phase 5: Frontend Integration (Weeks 4–6)

**Objective:** Build React UI for authentication, club viewing, and swiping.

### Task 5.1: Create API Client Module

- **Description:** Build `src/api/client.ts` with typed API methods
- **Acceptance Criteria:**
  - [ ] Constant: `BASE_URL = "http://localhost:8000/api"`
  - [ ] Functions:
    - [ ] `register(email, password, name, year, major, interests) -> Promise< { access_token, user } >`
    - [ ] `login(email, password) -> Promise< { access_token, user } >`
    - [ ] `getClubs() -> Promise< Club[] >`
    - [ ] `createSwipe(clubId, liked) -> Promise< { swipe_id, reward } >`
    - [ ] `getRecommendations(top_k=5) -> Promise< Club[] >`
    - [ ] `updatePreferences(interests) -> Promise< { user } >`
  - [ ] JWT management:
    - [ ] `setToken(token)` – store in localStorage
    - [ ] `getToken()` – retrieve from localStorage
    - [ ] Auto-attach `Authorization: Bearer <token>` header to all requests
  - [ ] Error handling:
    - [ ] 401 errors trigger logout (clear token, redirect to login)
    - [ ] Network errors show user-friendly messages
  - [ ] TypeScript types for all responses
  - [ ] Test: `import { api } from '@/api/client'` works without errors
- **Notes:** Use `fetch` or `axios`; keep it simple

- **Depends on:** Task 2.1–2.4, Task 3.2, Task 4.6

### Task 5.2: Integrate Authentication Flow in LoginPage

- **Description:** Update `src/pages/LoginPage.tsx` to use real backend auth
- **Acceptance Criteria:**
  - [ ] Replace hardcoded login logic with `api.login()` call
  - [ ] Form fields: email, password
  - [ ] Add register option (toggle or link to register form)
  - [ ] On successful login:
    - [ ] Store token via `api.setToken(token)`
    - [ ] Store user context (id, email, name)
    - [ ] Redirect to Home page (or Survey if first login)
  - [ ] On error: show error message
  - [ ] Loading state while submitting
  - [ ] Test: register new user, log in, verify redirects to Home
- **Notes:** Decide: should first-time login redirect to Survey or Home? Default = Survey

- **Depends on:** Task 5.1, Task 2.1

### Task 5.3: Create SwipeCard Component

- **Description:** Build `src/components/SwipeCard.tsx` to display club and handle swipes
- **Acceptance Criteria:**
  - [ ] Component props: `club: Club`, `onSwipe: (liked: boolean) => void`
  - [ ] Display:
    - [ ] Club name (large, prominent)
    - [ ] Description (multiline text)
    - [ ] Tags (pill-style badges)
    - [ ] Meeting time (e.g., "Tue 18:00")
    - [ ] Location
    - [ ] Members count (optional)
  - [ ] Buttons:
    - [ ] ❌ Dislike (left/red)
    - [ ] ❤️ Like (right/green)
  - [ ] On click: call `onSwipe(true/false)`, show spinning loading state
  - [ ] Styling: clean card design, responsive (mobile-friendly)
  - [ ] Test: render with sample club, click buttons, verify callback triggered
- **Notes:** Can use Tailwind + DaisyUI for styling; consider card animations

- **Depends on:** None

### Task 5.4: Rebuild Home Page with Swipe UI

- **Description:** Update `src/pages/Home.tsx` to show swipe card interface
- **Acceptance Criteria:**
  - [ ] On mount: fetch recommendations via `api.getRecommendations(top_k=10)`
  - [ ] Display top club in SwipeCard component
  - [ ] On swipe:
    - [ ] Call `api.createSwipe(clubId, liked)`
    - [ ] Fetch next recommendation
    - [ ] Remove swiped club from deck, show next
  - [ ] Stats display: "Swiped 5 clubs" counter
  - [ ] Loading state: show skeleton or spinner while fetching
  - [ ] Empty state: "No more clubs" message if recommendations exhausted
  - [ ] Logout button (clear token, redirect to LoginPage)
  - [ ] Test: login, swipe 5+ clubs, verify recommendations update
- **Notes:** Keep state simple: current club index, swipe count

- **Depends on:** Task 5.1, Task 5.3

### Task 5.5: Connect Survey to Backend Preferences

- **Description:** Update `src/pages/Survey.tsx` to submit interests to backend
- **Acceptance Criteria:**
  - [ ] Survey collects 20 questions about interests (keep existing logic)
  - [ ] Convert responses to tag list (e.g., slider values map to tags)
  - [ ] On submit:
    - [ ] Call `api.updatePreferences(interests)` with tag list
    - [ ] Show loading state
    - [ ] On success: redirect to Home page
  - [ ] On error: show error and allow retry
  - [ ] Test: complete survey, verify interests recorded in backend via `GET /api/users/<id>`
- **Notes:** Coordinate on slider-to-tag mapping with collaborators

- **Depends on:** Task 5.1, Task 2.4

### Task 5.6: Implement Protected Route / Auth Guard

- **Description:** Create `src/components/ProtectedRoute.tsx` to guard pages behind authentication
- **Acceptance Criteria:**
  - [ ] Component wrapper that checks if token exists
  - [ ] If no token: redirect to LoginPage
  - [ ] If token exists: render child route
  - [ ] Use in App.tsx for Home, Survey, etc.
  - [ ] Test: navigate to Home without login → redirects to Login
- **Notes:** Can use React Router's `Navigate` component

- **Depends on:** Task 5.2

### Task 5.7: Update App.tsx Routing

- **Description:** Wire all pages and routes in `src/App.tsx`
- **Acceptance Criteria:**
  - [ ] Routes:
    - [ ] `/login` → LoginPage (public)
    - [ ] `/` (Home) → protected, shows swipe cards
    - [ ] `/survey` → protected, preference survey
  - [ ] Default route: `/login` if not authenticated, else `/`
  - [ ] All routes render without errors
  - [ ] Test: navigate between pages, verify auth guard works
- **Notes:** Coordinate with Task 5.6

- **Depends on:** Task 5.2, Task 5.4, Task 5.5, Task 5.6

### Task 5.8: Style & Polish UI

- **Description:** Improve visual design and mobile responsiveness
- **Acceptance Criteria:**
  - [ ] SwipeCard: responsive on mobile, tablet, desktop
  - [ ] LoginPage: clean form layout
  - [ ] Survey: slider UX is smooth
  - [ ] Home page: intuitive swipe flow
  - [ ] Colors: cohesive theme (use DaisyUI config if applicable)
  - [ ] Spacing: consistent padding/margins
  - [ ] Test: view on mobile device (or browser dev tools), verify readable
- **Notes:** Use Tailwind + DaisyUI consistently

- **Depends on:** Task 5.4

### Task 5.9: Create Frontend Component Tests

- **Description:** Write vitest tests for SwipeCard and Home components
- **Acceptance Criteria:**
  - [ ] `src/components/SwipeCard.test.tsx`:
    - [ ] Render with sample club
    - [ ] Verify text content displayed
    - [ ] Click dislike button, verify callback
    - [ ] Click like button, verify callback
  - [ ] `src/pages/Home.test.tsx`:
    - [ ] Render and match snapshot
    - [ ] Mock api.getRecommendations()
    - [ ] Verify club displayed after fetch
  - [ ] `src/pages/LoginPage.test.tsx`:
    - [ ] Render form
    - [ ] Submit form, mock api.login()
  - [ ] All tests pass: `npm run test` (from app/web/)
- **Notes:** Mock API calls using jest/vitest mocks

- **Depends on:** Task 5.3, Task 5.4

---

## ✅ Phase 6: Testing & Optimization (Weeks 6–8)

**Objective:** Comprehensive testing, performance tuning, and documentation.

### Task 6.1: Create Backend Integration Tests

- **Description:** Write pytest tests for full user flow (register → survey → swipe → recommend)
- **Acceptance Criteria:**
  - [ ] Test file: `tests/integration/test_full_flow.py`
  - [ ] Test steps:
    - [ ] Register new user via `POST /api/auth/register`
    - [ ] Log in via `POST /api/auth/login`
    - [ ] Update preferences via `PUT /api/users/<id>/preferences`
    - [ ] Get recommendations via `GET /api/recommend`
    - [ ] Create swipe via `POST /api/swipes`
    - [ ] Verify swipe recorded in DB
  - [ ] All tests pass: `pytest tests/integration/test_full_flow.py -v`
- **Notes:** Use TestClient for integration testing

- **Depends on:** All Phase 2–4 tasks

### Task 6.2: Create End-to-End Manual Testing Checklist

- **Description:** Document manual testing steps for QA
- **Acceptance Criteria:**
  - [ ] Checklist file: `QA_CHECKLIST.md`
  - [ ] Steps:
    - [ ] Register via frontend form
    - [ ] Log in successfully
    - [ ] Complete survey, verify interests saved
    - [ ] Swipe on 10+ clubs
    - [ ] Verify recommendations improve (high-scoring clubs match interests)
    - [ ] Check Swipe table in DB for correct entries
    - [ ] Log out and log back in, verify session preserved
  - [ ] Any bugs logged as Issues with screenshots/steps to reproduce
- **Notes:** Assign to one person; they report bugs to the team

- **Depends on:** Task 5.7

### Task 6.3: Performance Baseline & Profiling

- **Description:** Measure API response times and identify bottlenecks
- **Acceptance Criteria:**
  - [ ] Create benchmark script: `scripts/benchmark.py`
  - [ ] Measure:
    - [ ] `GET /api/clubs`: <100ms for 30 clubs
    - [ ] `GET /api/recommend`: <500ms with 30 clubs
    - [ ] `POST /api/swipes` (including LinUCB update): <50ms
  - [ ] Profile slow endpoints using `time.perf_counter()` or profiler
  - [ ] Document results: `PERFORMANCE.md` with baseline metrics
  - [ ] If slow, identify the culprit (DB query, LinUCB computation, etc.)
- **Notes:** Run on local machine; not production-critical for MVP

- **Depends on:** All API tasks (Phase 2–4)

### Task 6.4: Optimize Slow Queries (if needed)

- **Description:** Add database indexes or refactor queries if baseline reveals slowness
- **Acceptance Criteria:**
  - [ ] If `GET /api/clubs` slow: add index on Club.created_at or other filter columns
  - [ ] If `GET /api/recommend` slow: profile LinUCB computation (should be <200ms for 38-dim)
  - [ ] If `POST /api/swipes` slow: ensure Swipe table has indexes on (user_id, club_id)
  - [ ] Re-measure after optimizations; verify improvement
  - [ ] Document changes in code comments
- **Notes:** Skip if baseline already meets <500ms target

- **Depends on:** Task 6.3

### Task 6.5: Update README with Tech Stack & API Docs

- **Description:** Rewrite README with current implementation details
- **Acceptance Criteria:**
  - [ ] Update tech stack section:
    - [ ] Backend: FastAPI, SQLAlchemy, SQLite
    - [ ] Frontend: React 19, TypeScript, Vite, Tailwind CSS, DaisyUI
    - [ ] Recommendation: LinUCB contextual bandit
  - [ ] Add API endpoint reference (request/response examples):
    - [ ] Auth: POST /auth/register, POST /auth/login
    - [ ] Clubs: GET /clubs, POST /swipes, GET /users/{id}/swipes
    - [ ] Recommendations: GET /recommend
  - [ ] Add setup instructions:
    - [ ] `cd app/web && npm install && npm run dev`
    - [ ] `uv run fastapi dev app/api/main.py`
  - [ ] Add architecture section explaining LinUCB flow
  - [ ] Remove out-of-date info from current README
- **Notes:** Reference this plan; cite code (Task 4.3, Task 4.4, etc.)

- **Depends on:** All tasks (provides overview)

### Task 6.6: Create Developer Guide

- **Description:** Write guide for new collaborators: architecture, code structure, how to extend
- **Acceptance Criteria:**
  - [ ] File: `DEVELOPER.md`
  - [ ] Sections:
    - [ ] Project structure (folder layout)
    - [ ] How recommendations work (brief LinUCB explanation)
    - [ ] How to add a new endpoint
    - [ ] How to add a new recommendation feature
    - [ ] Testing guidelines
    - [ ] Common debugging tips
  - [ ] Code examples for extending the system
- **Notes:** Helps future contributors or onboarding new team members

- **Depends on:** Final phase

### Task 6.7: Create Deployment Plan (Future)

- **Description:** Document steps for deploying to production (not implemented yet)
- **Acceptance Criteria:**
  - [ ] File: `DEPLOYMENT.md`
  - [ ] Outline:
    - [ ] Database migration strategy
    - [ ] Environment variables (JWT secret, DB URL, etc.)
    - [ ] Frontend build process (`npm run build`)
    - [ ] Backend server deployment (Docker, cloud platform, etc.)
    - [ ] Monitoring & logging
  - [ ] Placeholder: "To be completed after MVP"
- **Notes:** Not for MVP; create skeleton for future work

- **Depends on:** None (planning task)

---

## ✅ Phase 7: Advanced Frontend Features (Weeks 7–10)

**Objective:** Build social features, user engagement systems, and community dashboards.

### Task 7.1: Implement Medal & Achievement System

- **Description:** Create backend medal/badge system for user activity tracking
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Add `Medal` model: `id`, `name`, `description`, `icon_url`, `criteria` (e.g., "attended_5_events")
    - [ ] Add `UserMedal` model: `id`, `user_id` (FK), `medal_id` (FK), `earned_at` (datetime)
    - [ ] Endpoint `GET /api/users/<user_id>/medals` returns list of earned medals
    - [ ] Auto-grant medals on event attendance (e.g., "Attended 5 events" → medal granted)
    - [ ] Seed 5–10 medal templates: "Event Regular" (1 event), "Social Butterfly" (5 events), "Club Leader" (10+ organized), etc.
  - [ ] **Frontend:**
    - [ ] Create `src/components/MedalBadge.tsx` to display medal icon + name (small card)
    - [ ] Render medals on user profile page (Task 7.3)
    - [ ] Show "new medal earned!" toast notification when user earns a medal
  - [ ] **Tests:**
    - [ ] `tests/db/test_medals.py`: Test Medal and UserMedal models
    - [ ] `tests/api/test_medals.py`: Test GET /api/users/{id}/medals endpoint
    - [ ] `src/components/MedalBadge.test.tsx`: Test MedalBadge rendering with sample medal
- **Notes:** Keep medal rules simple for MVP; can extend with complex rules later

- **Depends on:** Task 1.1 (User model)

### Task 7.2: Implement User View Profile System

- **Description:** Allow users to view public profiles of other users
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Endpoint `GET /api/users/<user_id>/public-profile` returns public user data
    - [ ] Response includes: id, name, year, major, interests, joined_clubs (list), medal_count, event_attendance_count
    - [ ] Don't expose private data (email, password_hash, etc.)
    - [ ] Add optional `GET /api/users?search=<name>` for user discovery
  - [ ] **Frontend:**
    - [ ] Create `src/pages/UserProfile.tsx` to display user profile
    - [ ] Route: `/users/<user_id>`
    - [ ] Display: user name, year, major, interests (tags), joined clubs, medals, stats
    - [ ] Joined clubs shown as clickable cards linking to club pages
    - [ ] Profile image placeholder (avatar with initials)
  - [ ] **Tests:**
    - [ ] `tests/api/test_users.py`: Test GET /api/users/{id}/public-profile endpoint
    - [ ] `tests/api/test_users.py`: Test search users endpoint
    - [ ] `src/pages/UserProfile.test.tsx`: Mock API, verify profile renders
- **Notes:** Joined clubs require tracking user-club relationships (add `joined_clubs` association or query attendances)

- **Depends on:** Task 1.1, Task 7.1 (medals visible on profile)

### Task 7.3: Implement Direct Messaging System

- **Description:** Allow users to send direct messages to each other
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Add `Message` model: `id`, `sender_id` (FK), `recipient_id` (FK), `body` (text), `created_at`, `is_read` (bool)
    - [ ] Endpoint `POST /api/messages` create new message (requires JWT auth)
    - [ ] Endpoint `GET /api/messages/conversations` list all user conversations (recent first)
    - [ ] Endpoint `GET /api/messages/conversation/<user_id>` retrieve message history with specific user (paginated)
    - [ ] Endpoint `PUT /api/messages/<msg_id>/read` mark message as read
    - [ ] Unread count for each conversation included in response
  - [ ] **Frontend:**
    - [ ] Create `src/pages/Messages.tsx` (landing page for messaging)
      - [ ] Show list of conversations with recent message preview
      - [ ] Unread badge on conversation
      - [ ] Click conversation to open chat
    - [ ] Create `src/components/ChatBox.tsx` (individual conversation view)
      - [ ] Show message history (paginated, older messages at top)
      - [ ] Input box to type and send new message
      - [ ] Auto-scroll to latest message
      - [ ] Real-time message updates (fetch every 2 seconds or WebSocket if time allows)
    - [ ] Route: `/messages` (list), `/messages/<user_id>` (chat with specific user)
  - [ ] **Tests:**
    - [ ] `tests/db/test_messages.py`: Test Message model, save/retrieve
    - [ ] `tests/api/test_messages.py`: Test POST, GET conversations, GET conversation history, mark read
    - [ ] `src/pages/Messages.test.tsx`: Mock API, render conversation list
    - [ ] `src/components/ChatBox.test.tsx`: Mock API, test message sending and rendering
- **Notes:** WebSocket not required for MVP; polling is acceptable. Consider rate-limiting message creation.

- **Depends on:** Task 2.3 (JWT auth), Task 7.2 (user discovery)

### Task 7.4: Implement Events Feed Page

- **Description:** Create a feed showing upcoming events from clubs the user has joined
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Add `ClubMember` model: `id`, `user_id` (FK), `club_id` (FK), `joined_at` (datetime)
    - [ ] Endpoint `POST /api/clubs/<club_id>/join` user joins club (add ClubMember row)
    - [ ] Endpoint `DELETE /api/clubs/<club_id>/leave` user leaves club
    - [ ] Endpoint `GET /api/users/<user_id>/joined-clubs` list clubs user is member of
    - [ ] Endpoint `GET /api/feed/events` returns upcoming events from user's joined clubs, sorted by start_time (asc)
    - [ ] Query params: `?upcoming=true` (default), `?limit=20`
  - [ ] **Frontend:**
    - [ ] Create `src/pages/EventsFeed.tsx`
      - [ ] Display list of upcoming events from joined clubs
      - [ ] Each event card shows: club name, event title, start_time, location, attendee count
      - [ ] "Mark Attending" button (saves user attendance)
      - [ ] Route: `/feed`
    - [ ] Add "Join" button on club cards (home page, club pages) to add ClubMember
  - [ ] **Tests:**
    - [ ] `tests/db/test_clubs.py`: Test ClubMember model
    - [ ] `tests/api/test_clubs.py`: Test join/leave club endpoints
    - [ ] `tests/api/test_feed.py`: Test GET /api/feed/events endpoint with various filters
    - [ ] `src/pages/EventsFeed.test.tsx`: Mock API, verify events render
- **Notes:** Event attendance tracking ties into medal system (automatic medal granting)

- **Depends on:** Task 1.4 (Event model), Task 7.1 (medals)

### Task 7.5: Implement Leaderboard Page

- **Description:** Display ranked users based on medal count and activity
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Endpoint `GET /api/leaderboard` returns ranked users
    - [ ] Ranking criteria: medal_count (desc), then event_attendance_count (desc), then created_at (asc for tiebreak)
    - [ ] Response fields per user: rank, id, name, medal_count, event_count, avatar_url
    - [ ] Query params: `?limit=100` (max users to return), `?sort_by=medals` or `sort_by=activity`
    - [ ] Optional: `GET /api/leaderboard/around-me?user_id=X` returns user's rank + 10 above/below
  - [ ] **Frontend:**
    - [ ] Create `src/pages/Leaderboard.tsx`
      - [ ] Display ranked table: rank, user avatar + name, medal count, activity count
      - [ ] Sort dropdown: by medals, by activity
      - [ ] Click user name to navigate to their profile
      - [ ] Highlight current user's row in table
      - [ ] Route: `/leaderboard`
  - [ ] **Tests:**
    - [ ] `tests/api/test_leaderboard.py`: Test GET /api/leaderboard endpoint, ranking logic
    - [ ] `tests/api/test_leaderboard.py`: Test around-me endpoint
    - [ ] `src/pages/Leaderboard.test.tsx`: Mock API, verify table renders with correct sort order
- **Notes:** Leaderboard should update on page load; consider caching for performance

- **Depends on:** Task 7.1 (medal counts), Task 7.4 (event attendance)

### Task 7.6: Implement Club Home Page

- **Description:** Create dedicated home pages for each club with info, events, and member list
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Endpoint `GET /api/clubs/<club_id>` returns full club details
    - [ ] Response includes: id, name, description, tags, meeting_time, location, member_count, event_list (upcoming 5), member_preview (first 5 members)
    - [ ] Endpoint `GET /api/clubs/<club_id>/members` returns paginated list of club members
  - [ ] **Frontend:**
    - [ ] Create `src/pages/ClubHome.tsx`
      - [ ] Display: club name (large), description, tags (pills), meeting time, location, member count
      - [ ] "Join Club" / "Leave Club" button (toggle based on membership)
      - [ ] Upcoming events section: list of next 5 events with "attending?" RSVP button
      - [ ] Members section: grid of member avatars + names (click to view profile)
      - [ ] Route: `/clubs/<club_id>`
    - [ ] Link to ClubHome from club cards (home page, feed, leaderboard)
  - [ ] **Tests:**
    - [ ] `tests/api/test_clubs.py`: Test GET /api/clubs/{id} endpoint
    - [ ] `tests/api/test_clubs.py`: Test GET /api/clubs/{id}/members endpoint
    - [ ] `src/pages/ClubHome.test.tsx`: Mock API, verify club info, events, members render
- **Notes:** Club leader dashboard (Task 7.7) is separate; this is the public view

- **Depends on:** Task 1.2 (Club model), Task 1.4 (Event model), Task 7.4 (membership)

### Task 7.7: Implement Club Leader Dashboard

- **Description:** Admin dashboard for club leaders to manage club and see attendee analytics
- **Acceptance Criteria:**
  - [ ] **Backend:**
    - [ ] Add `ClubRole` model or enum to ClubMember: `member`, `officer`, `leader`
    - [ ] Endpoint `PUT /api/clubs/<club_id>/members/<user_id>/role` change user role (requires leader auth)
    - [ ] Endpoint `GET /api/clubs/<club_id>/dashboard` returns admin data (requires leader auth)
      - [ ] Returns: member_count, recent_events (with attendance stats), member_list with roles, attendance records
    - [ ] Endpoint `POST /api/clubs/<club_id>/events` create event (requires leader auth) — hook to Task 1.4 or create new
    - [ ] Endpoint `POST /api/events/<event_id>/attendance` mark user as attended event (for leader check-in)
  - [ ] **Frontend:**
    - [ ] Create `src/pages/ClubDashboard.tsx` (restricted to club leaders)
      - [ ] Display: club name (header), stats (total members, upcoming events, attended last event)
      - [ ] "Create Event" button → modal to add new event
      - [ ] Members table: name, role, join_date, last_event_attended
      - [ ] Promote/demote role buttons (leader only)
      - [ ] Route: `/clubs/<club_id>/dashboard` (protected, role-checked)
    - [ ] Create `src/components/EventAttendanceChecklist.tsx` for recording who attended event
  - [ ] **Tests:**
    - [ ] `tests/api/test_clubs.py`: Test role assignment endpoint (auth required)
    - [ ] `tests/api/test_clubs.py`: Test dashboard endpoint (leader vs. non-leader)
    - [ ] `tests/api/test_events.py`: Test event creation and attendance marking
    - [ ] `src/pages/ClubDashboard.test.tsx`: Mock auth + API, verify leader dashboard renders
- **Notes:** Auth/authorization logic: check if user.role in [officer, leader]. Implement role-based access control early.

- **Depends on:** Task 2.3 (JWT auth), Task 1.2 (Club model), Task 1.4 (Event model)

### Task 7.8: Enhance User Profile Page with Joined Clubs & Activity

- **Description:** Expand user profile to show joined clubs and attended events
- **Acceptance Criteria:**
  - [ ] **UPDATES to Task 7.2 user profile:**
    - [ ] Display "Joined Clubs" section as clickable cards → ClubHome pages
    - [ ] Display "Recent Events Attended" section (last 10 events with dates)
    - [ ] Display earned medals prominently
    - [ ] Profile stats: "Member of X clubs", "Attended Y events", "Earned Z medals"
  - [ ] **Tests:**
    - [ ] `src/pages/UserProfile.test.tsx`: Update tests to include clubs and events sections
- **Notes:** Builds on Tasks 7.1–7.4 data fetching

- **Depends on:** Task 7.2, Task 7.1, Task 7.4

### Task 7.9: Add Navigation & Routing for All New Pages

- **Description:** Wire new pages into app routing and add navigation menu
- **Acceptance Criteria:**
  - [ ] **Update `src/App.tsx`:**
    - [ ] Routes: `/feed`, `/leaderboard`, `/messages`, `/clubs/<id>`, `/clubs/<id>/dashboard`, `/users/<id>` (update existing)
    - [ ] Protected: all routes require JWT auth
  - [ ] **Update navigation header/sidebar:**
    - [ ] Add links: Feed, Leaderboard, Messages (with unread badge), Profile, Club Dashboard (if leader)
    - [ ] Mobile responsive hamburger menu
  - [ ] **Tests:**
    - [ ] `src/App.test.tsx`: Verify all routes accessible and protected routes redirect to login when unauthenticated
- **Notes:** Navigation should reflect user role (leaders see Club Dashboard link)

- **Depends on:** Task 7.1–7.8 (all pages exist)

---

## 🔒 Notes & Constraints

1. **Token Expiration**: Recommend short-lived access tokens (1 hour); refresh tokens for longer sessions (optional post-MVP)
2. **Unswiped Clubs Only**: Decide early: should `/api/recommend` hide clubs user already swiped? Default = show all
3. **LinUCB Persistence**: Currently lives only in server memory. If server restarts, A/b matrices are lost. Serialize to DB post-MVP if needed
4. **Google Calendar**: Not included in this MVP; documented in README for future work
5. **Admin Panel**: Not included; assume all clubs are pre-seeded by admins via migration/script
6. **Mobile App**: Not planned; MVP is web-only
   7 **Scalability**: MVP designed for 100–1000 users, 50–200 clubs. For larger scale, consider:
   - Vectorize LinUCB operations
   - Cache recommendations
   - Shard LinUCB model by user cohorts

---

## 📋 Collaboration Guidelines

- **Assign tasks** to team members as they begin (update "Owner" field)
- **Mark as In Progress** when starting work
- **Pull requests**: link GitHub issue in PR description
- **Testing**: ensure all tests pass before merging
- **Code Review**: pair review on recommendation engine (Phase 4) and critical auth (Phase 2)
- **Sync**: weekly check-ins to unblock dependencies and coordinate database/API changes (Phases 1–3)

---

## ✅ Success Criteria (MVP Complete - Phases 1-6)

- [ ] User can register, log in, complete survey
- [ ] User sees list of clubs (via `/api/clubs`)
- [ ] User can swipe left/right on clubs (via `/api/swipes`)
- [ ] Swipes are stored in database
- [ ] Recommendations improve over time (via LinUCB)
- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] Manual QA checklist complete (Task 6.2)
- [ ] README and DEVELOPER.md updated

## ✅ Success Criteria (Extended Features - Phase 7)

- [ ] Users earn medals for attending events
- [ ] Users can view other users' public profiles
- [ ] Users can send direct messages to each other (DM system working)
- [ ] Events feed shows upcoming events from joined clubs
- [ ] Leaderboard displays users ranked by medals and activity
- [ ] Club home pages display club info, events, members
- [ ] Club leaders can access dashboard with analytics
- [ ] All new backend tests pass
- [ ] All new frontend tests pass
- [ ] Navigation menu includes all new pages
- [ ] Role-based access control working (leader-only routes)

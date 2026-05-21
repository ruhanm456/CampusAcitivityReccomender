# Campus Activity Recommender

This repository contains an early-stage web application for recommending campus clubs and events to students. The UX is inspired by swipe-based apps: students swipe right to like a club/event and left to skip; the system learns from swipes to improve recommendations.

This README explains the project's goals, current implementation state, structure, and how to run the code locally for development.

Overview

- Goal: provide an interactive recommender for campus activities where students can discover clubs/events, swipe to express interest, and receive improved suggestions over time.
- Short-term scope (MVP):
  - User registration/login, preference survey
  - Club listing and swipe actions
  - A recommendation endpoint (planned) designed to be driven by a contextual bandit (LinUCB)
  - Frontend swipe UI (React + Vite)
- Long-term / Phase 7: social and engagement features (medals, profiles, DMs, feed, leaderboard, club dashboards).

Current implementation (snapshot)

- Backend: FastAPI application skeleton with SQLAlchemy models. The `User` model has been expanded (see below). Some endpoints exist; most API endpoints described in the plan are TODO and tracked in `TASKS.md`.
- Frontend: React + TypeScript + Vite app under `app/web/` with placeholder pages (`Home`, `Login`, `Survey`, `ChatWindow`). Some components and tests exist.
- Recommendation: design and documentation for LinUCB and feature engineering are in the repo notes and `TASKS.md`, but the full system is still a planned implementation (Phase 4 in `TASKS.md`).

Quick facts

- Project root: repository root contains `app/` (backend + web frontend), `tests/`, and `TASKS.md` (detailed plan & tasks).
- Key backend module: `app/db/models.py` (SQLAlchemy models). The `User` model now includes `name`, `year`, `major`, `interests`, and `created_at`.
- Frontend root: `app/web/` (Vite + React app). Run commands and tests live under that folder.

Repository layout (important paths)

- `app/api/` — FastAPI entrypoints and route handlers (work in progress)
- `app/db/models.py` — SQLAlchemy models (User, Club, etc.)
- `app/recommendation/` — planned feature engineering and LinUCB code (Phase 4)
- `app/web/` — frontend app (React + TypeScript + Vite)
- `scripts/` — automation scripts (seed, test helpers; some scripts will be added as part of tasks)
- `tests/` — pytest tests for backend and vitest tests for frontend
- `tests/data` — test data loaded in at server bootup
- `TASKS.md` — project roadmap and per-task acceptance criteria (use this to onboard contributors)

Data model summary

The current canonical model fields (subject to migrations in Phase 1):

- `User` (app/db/models.py)
  - `id`, `email`, `password_hash`, `is_verified`, `name`, `year`, `major`, `interests`, `created_at`
  - `interests` is stored as a comma-separated list of tags (vocabulary defined in the plan)

- `Club`
  - `id`, `name`, `description`, `tags`, `meeting_time`, `location`, `created_at`

See `TASKS.md` for the full schema and planned additional models (Event, ClubMember, Medal, Message, etc.).

How to run the project (development)

Prerequisites

- Python 3.11+ (a virtualenv is recommended)
- Node.js (or Bun) for the frontend
- `git` and optionally `gh` (GitHub CLI) if you want to create issues programmatically

1. Install all prequisites into virtual environment
2. Run backend dev server (FastAPI)

The project provides a FastAPI app at `app/api/main.py`. Use one of these commands from the project root:

```pwsh
# Option A: using uvicorn
uvicorn app.api.main:app --reload --port 8000

# Option B: if a helper alias is available (recommended)
fastapi dev
```

API base URL (local): `http://127.0.0.1:8000/`

3. Frontend: run the Vite dev server

```pwsh
cd app/web
npm install   # or `bun install` if using Bun
npm run dev   # or `bun run dev`
```

Open the frontend in your browser (Vite will display the local dev URL, typically `http://localhost:5173`). The frontend currently includes placeholder pages; work in `src/pages/`.

Running tests

- Backend unit tests: from repository root

```pwsh
& .venv\Scripts\Activate.ps1
python -m pytest tests/db -q
```

- Frontend tests: from `app/web/`

```pwsh
cd app\web
npm run test    # or `bun run test` depending on your package manager
```

Development workflow & tasks

- This repo uses a task-driven plan stored in `TASKS.md`. It lists phases (database, auth, swipes, recommendations, frontend integration, testing, and advanced features) with detailed acceptance criteria and test requirements.
- We use TDD for critical model changes. Example: `tests/db/test_models.py` was created to drive changes to `User`.
- To create GitHub issues from `TASKS.md`, a helper script exists at `scripts/create_github_issues.py` which uses `gh` (GitHub CLI). Authenticate with `gh auth login` before running it.

Notes on current status and next steps

- The `User` model has been expanded (name, year, major, interests). You can see the implementation in `app/db/models.py` and its tests in `tests/db/test_models.py`.
- The recommendation system (LinUCB and feature engineering) is planned in `TASKS.md` (Phase 4) and documented in the repository notes; the fully persistent LinUCB service and related endpoints are to be implemented as part of the roadmap.
- Advanced social features (medals, DM, feed, leaderboard, club dashboard) are defined as Phase 7 in `TASKS.md` and include tests as subtasks.

Contributing & onboarding

- If you're joining as a new contributor:
  1.  Read `TASKS.md` to pick a task with clear acceptance criteria.
  2.  Follow TDD: add tests under `tests/`, run them, implement code, then run tests again.
  3.  Push a branch and open a PR referencing the related issue/task.

- Important files to look at first:
  - `app/db/models.py` — database models
  - `app/api/main.py` — FastAPI app entrypoint
  - `app/web/src/pages/` — React pages (Login, Survey, Home)
  - `TASKS.md` — detailed roadmap (priority and dependencies)

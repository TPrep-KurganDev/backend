# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

T-Prep Backend is a FastAPI-based learning platform for creating and taking exams with spaced repetition features. The application uses PostgreSQL with SQLAlchemy ORM and Alembic for migrations.

**Stack**: FastAPI, SQLAlchemy, PostgreSQL, Alembic, Poetry, Python 3.13

## Development Commands

### Initial Setup (macOS)
```bash
make init              # Create venv, install Poetry, and install dependencies
```

### Environment Configuration
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/db_name
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Docker Deployment
```bash
make build                            # Build Docker images
make up                               # Start both app and database in background
make down                             # Stop and remove containers
make logs                             # Follow application logs
make restart                          # Restart services (down + up)

# Or use docker-compose directly:
docker-compose up -d                  # Start both app and database
docker-compose up --build             # Rebuild and start
docker-compose down                   # Stop and remove containers
docker-compose logs -f app            # Follow application logs
docker-compose exec app alembic revision --autogenerate -m "msg"  # Create migration in container
```

The docker-compose setup includes:
- PostgreSQL 15 on port 5432
- FastAPI app on port 8000 with hot-reload
- Automatic database initialization and migrations on startup
- Health checks for database readiness

### Database Management
```bash
python init_db.py                                    # Initialize database (creates DB if not exists)
alembic revision --autogenerate -m "description"     # Create new migration after model changes
alembic upgrade head                                 # Apply all pending migrations
alembic downgrade -1                                 # Rollback last migration
```

### Running the Application
```bash
uvicorn tprep.app.main:app --reload                  # Start dev server on http://127.0.0.1:8000
# API docs available at: http://127.0.0.1:8000/api/docs
# Health check: http://127.0.0.1:8000/health
```

### Code Quality
```bash
make mypy              # Type checking with mypy (strict mode enabled)
make ruff-lint         # Lint code with ruff
make pytest-lint       # Check for dead/duplicate fixtures
make lint              # Run all linters (mypy + ruff + pytest-lint)
make pretty            # Auto-format with ruff and apply fixes
make plint             # Format then lint (pretty + lint)
```

### Testing
```bash
pytest                 # Run tests (pytest.ini configures async tests)
```

## Architecture

The codebase follows a **layered architecture** pattern with clear separation of concerns:

### Layer Structure

```
tprep/
├── app/                    # Application/API layer
│   ├── main.py            # FastAPI app, routes, exception handlers, lifespan
│   ├── *_schemas.py       # Pydantic request/response models
│   └── api/routes/        # Route handlers (auth, exams, session)
├── domain/                 # Domain/Business logic layer
│   ├── exam_session.py    # In-memory session management for active exams
│   └── services/          # Business logic services (SessionFactory)
├── infrastructure/         # Data access layer
│   ├── models.py          # SQLAlchemy Base class
│   ├── database.py        # DB connection and session management
│   ├── authorization.py   # JWT auth, password hashing
│   ├── user/              # User model and repository
│   ├── exam/              # Exam, Card, UserPinnedExam models and repository
│   ├── statistic/         # Statistics model and repository
│   └── exceptions/        # Custom exception classes
└── helpers/                # Utility scripts (init_db, clear_db)
```

### Key Architectural Patterns

**Repository Pattern**: Each entity (User, Exam, Statistic) has a dedicated repository class in `infrastructure/*/` for database operations. Keep business logic out of repositories.

**Domain Models vs Database Models**:
- `infrastructure/*/*.py` contains SQLAlchemy ORM models (database layer)
- `domain/` contains pure business logic with minimal dependencies
- `app/*_schemas.py` contains Pydantic models for API requests/responses

**In-Memory Session Management**: Active exam sessions are stored in memory via `SessionFactory.session_ids` dict in `domain/services/session_factory.py`. This is NOT persisted to the database and will be lost on restart.

**Session Strategies**:
- `full`: All cards in exam
- `random`: Random N cards from exam
- `smart`: Prioritizes cards with most mistakes (uses Statistic table)

**Authentication**: JWT-based auth using `python-jose`. Token verification is in `infrastructure/authorization.py`. Use `get_current_user()` dependency for protected endpoints.

**Exception Handling**: Custom exceptions in `infrastructure/exceptions/` are mapped to HTTP status codes in `APP_ERRORS` dict in `main.py`. Add new exceptions there when creating custom errors.

## Database Schema Key Relationships

- **User** → many **Exam** (via `creator_id`)
- **User** ↔ **Exam** (many-to-many via `UserPinnedExam` for pinned exams)
- **Exam** → many **Card** (exam questions/answers)
- **Statistic** tracks user performance per card (mistake counts for smart session strategy)

All relationships use `CASCADE DELETE` with `passive_deletes=True`.

## Important Alembic Configuration

When creating new models, update `migrations/env.py` to import them:
```python
from infrastructure.models import *
from infrastructure.user.user import *
from infrastructure.exam.exam import *
# Add new model imports here
```

The `target_metadata` must be set to `Base.metadata` (not `None`) for autogenerate to work.

## Notes on Testing

- `pytest.ini` configures async test mode
- Only one test exists: `tests/test_health.py`
- Mock users are created on startup via `create_mock_users()` in `mocks/mock_users.py`
- Database is cleared on startup via `clear_db()` in lifespan

## Working with This Codebase

- Always run migrations after modifying SQLAlchemy models
- Import paths use `tprep.` prefix (e.g., `from tprep.infrastructure.user.user import User`)
- Configuration is loaded via `config.py` which reads from `.env`
- The app uses Python 3.13 with strict mypy type checking
- Database sessions are managed via `get_db()` dependency injection
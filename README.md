# SprintSync

AI-powered task management for engineering teams. Built with FastAPI, PostgreSQL, and Google Gemini.

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd SprintSync
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload
```

## Features

- **Task Management**: CRUD operations with status tracking
- **AI Integration**: Task descriptions and daily plans via Gemini
- **Hybrid Auth**: JWT tokens with cookie/header support
- **Real-time UI**: HTMX for dynamic updates
- **Production Ready**: Structured logging, metrics, health checks

## API Endpoints

```
POST   /auth/signup          # User registration
POST   /auth/login           # User authentication
GET    /tasks/               # List user tasks
POST   /tasks/               # Create task
POST   /tasks/{id}/status    # Update task status
POST   /ai/suggest           # Generate task descriptions (draft) or daily plans (plan)
GET    /metrics              # Prometheus metrics
GET    /health               # Health check
```

## Development

```bash
# Run tests
pytest tests/ -v

# Lint code
flake8 app/ tests/
black --check app/ tests/

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```


## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design and database schema.

## Tech Stack

- **Backend**: FastAPI + Python 3.10
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Frontend**: HTMX + Tailwind CSS
- **AI**: Google Gemini 2.5 Flash
- **Deployment**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Structured logs + Prometheus metrics 
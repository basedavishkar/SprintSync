> An AI-powered, fullstack task manager with real-time UI and observability — built for real-world software teams.
# SprintSync - AI-Powered Task Management

A production-ready task management system built with FastAPI, HTMX, and Google Gemini AI. Deployed on Railway with full observability and comprehensive testing.

## Live Demo

**Deployed Application:** [SprintSync on Railway](https://sprintsync-production-9d7f.up.railway.app)

**Demo Access:**
- **Admin User:** `admin` / `admin123` (Full system overview, user management, analytics)
- **Regular Users:** `user1`, `user2`, `user3` / `password123` (Personal task management)

## What I Built

SprintSync is a task management system with AI integration, real-time updates, and admin features.

**Key Features:**
- Real-time UI with HTMX for seamless interactions
- AI-powered task generation using Google Gemini
- Production deployment with monitoring and logging
- Comprehensive testing with full API coverage
- Admin dashboard with system analytics
- Secure authentication with JWT and role-based access

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design and technical decisions.

**Tech Stack:** FastAPI, PostgreSQL, HTMX, Google Gemini, Railway

## Quick Start

```bash
# Clone and setup
git clone https://github.com/basedavishkar/SprintSync
cd SprintSync
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Add your GEMINI_API_KEY to .env

# Database setup
alembic upgrade head
python -m app.seed_data

# Run development server
uvicorn app.main:app --reload
```

## Features

- **Task Management:** Create, update, delete, and track task status
- **Real-time Updates:** HTMX-powered dynamic UI without page refreshes
- **AI Integration:** Generate task descriptions and daily plans with Google Gemini
- **User Authentication:** Secure JWT-based authentication with role-based access
- **Admin Dashboard:** System overview, user management, completion analytics
- **Production Ready:** Structured logging, health checks, error handling

## API

See [docs/API.md](docs/API.md) for complete API documentation and examples.

## Testing

```bash
# Run all tests
pytest
```

**Test Coverage:** Comprehensive API testing with edge cases

## Monitoring

- **Prometheus Metrics:** Request counts, error rates, response times
- **Structured Logging:** Per-request logging with correlation IDs
- **Health Checks:** Application health monitoring

## Development

```bash
# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Seed database
python -m app.seed_data
```

## Technology Choices

See [docs/DECISIONS.md](docs/DECISIONS.md) for detailed reasoning behind each technology choice and architectural decision.





## Conclusion

Deployed and ready for use.

**Repository:** [https://github.com/basedavishkar/SprintSync](https://github.com/basedavishkar/SprintSync)

---

**Built with FastAPI, HTMX, Google Gemini, and Swagger UI** 
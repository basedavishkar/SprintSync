# SprintSync Architecture

FastAPI + PostgreSQL + Gemini AI task management system.

## System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        UI[Web UI - HTMX]
        API_CLIENT[API Clients]
    end
    
    subgraph "Backend"
        FASTAPI[FastAPI Server]
        AUTH[Auth Middleware]
        SERVICES[Service Layer]
    end
    
    subgraph "Data & External"
        DB[(PostgreSQL)]
        GEMINI[Google Gemini API]
    end
    
    UI --> FASTAPI
    API_CLIENT --> FASTAPI
    FASTAPI --> AUTH
    AUTH --> SERVICES
    SERVICES --> DB
    SERVICES --> GEMINI
```

**Implementation:**
- **Layered Architecture**: Clean separation of concerns
- **Hybrid Authentication**: JWT tokens with cookie/header support
- **AI Integration**: Gemini API with graceful fallbacks
- **Production Ready**: PostgreSQL, Docker, CI/CD

## Database Schema

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string hashed_password
        boolean is_admin
        timestamp created_at
    }
    
    TASKS {
        int id PK
        string title
        text description
        string status
        int total_minutes
        int user_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    USERS ||--o{ TASKS : "has"
```

**Schema Design:**
- **Multi-tenant**: User isolation with foreign keys
- **Audit Trail**: Timestamps for tracking changes
- **Performance**: Indexed queries for fast lookups
- **Scalability**: PostgreSQL for production workloads

## Technology Stack

- **Backend**: FastAPI + Python 3.10
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Frontend**: HTMX + Tailwind CSS
- **AI**: Google Gemini 2.5 Flash
- **Deployment**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Structured logging + Prometheus metrics 
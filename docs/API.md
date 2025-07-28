# SprintSync API Reference

Simple REST API for task management with AI integration. Built with FastAPI.

## Authentication

JWT tokens with cookie/header support:

```bash
# Get token
curl -X POST "https://sprintsync-production-9d7f.up.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token
curl -H "Authorization: Bearer <token>" \
  "https://sprintsync-production-9d7f.up.railway.app/tasks/"
```

## Endpoints

### Auth
```
POST /auth/signup     # Register user
POST /auth/login      # Login, get JWT token
GET  /auth/users      # List users (admin only)
GET  /auth/admin/stats # System stats (admin only)
```

### Tasks
```
GET    /tasks/              # List user tasks
POST   /tasks/              # Create task
GET    /tasks/{id}          # Get task
PUT    /tasks/{id}          # Update task
DELETE /tasks/{id}          # Delete task
POST   /tasks/{id}/status   # Update status (HTMX)
```

### AI
```
POST /ai/suggest     # Generate task descriptions (draft) or daily plans (plan)
```

### Monitoring
```
GET /metrics         # Prometheus metrics
GET /health          # Health check
```

## Example Usage

### Create Task
```bash
curl -X POST "https://sprintsync-production-9d7f.up.railway.app/tasks/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement authentication",
    "description": "Add JWT auth",
    "status": "todo",
    "total_minutes": 120
  }'
```

### Generate Task Description (Draft Mode)
```bash
curl -X POST "https://sprintsync-production-9d7f.up.railway.app/ai/suggest" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build a chatbot",
    "mode": "draft"
  }'
```

### Generate Daily Plan (Plan Mode)
```bash
curl -X POST "https://sprintsync-production-9d7f.up.railway.app/ai/suggest" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "plan"
  }'
```

## Error Responses

All errors return:
```json
{
  "detail": "Error message"
}
```

Common status codes:
- `401` - Not authenticated
- `403` - Admin access required
- `404` - Resource not found
- `422` - Validation error

## Data Models

### Task
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Description",
  "status": "todo|in_progress|done",
  "total_minutes": 120,
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### User
```json
{
  "id": 1,
  "username": "admin",
  "is_admin": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Demo Access

- **Admin:** `admin` / `admin123`
- **Users:** `user1`, `user2`, `user3` / `password123`

## Rate Limiting

The `/ai/suggest` endpoint includes timeout handling and error recovery. For production use with high traffic, consider implementing rate limiting and request caching.

## OpenAPI Docs

Interactive Swagger UI available at: `https://sprintsync-production-9d7f.up.railway.app/docs` 
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_task(client):
    """Test task creation endpoint."""
    # First create a user and get token
    client.post(
        "/auth/signup",
        json={"username": "taskuser_unique", "password": "testpass123"}
    )
    
    login_response = client.post(
        "/auth/login",
        json={"username": "taskuser_unique", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Create task
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test task description",
            "status": "todo"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "todo"


def test_list_tasks(client):
    """Test task listing endpoint."""
    # Create user and get token
    client.post(
        "/auth/signup",
        json={"username": "listuser_unique", "password": "testpass123"}
    )
    
    login_response = client.post(
        "/auth/login",
        json={"username": "listuser_unique", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Create a task first
    client.post(
        "/tasks/",
        json={"title": "List Test Task", "description": "Test", "status": "todo"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # List tasks
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(task["title"] == "List Test Task" for task in data)


def test_update_task_status(client):
    """Test task status update endpoint."""
    # Create user and get token
    client.post(
        "/auth/signup",
        json={"username": "statususer_unique", "password": "testpass123"}
    )
    
    login_response = client.post(
        "/auth/login",
        json={"username": "statususer_unique", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={"title": "Status Test Task", "description": "Test", "status": "todo"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Update status
    response = client.post(
        f"/tasks/{task_id}/status",
        params={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress" 
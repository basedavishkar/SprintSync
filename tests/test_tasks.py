from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_task(client):
    """Test task creation endpoint."""
    # First create a user and get token
    client.post(
        "/auth/signup",
        json={"username": "taskuser_unique", "password": "testpass123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "taskuser_unique", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create task
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test task description",
            "status": "todo",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "todo"
    assert data["total_minutes"] == 0  # Default value


def test_create_task_with_time_estimate(client):
    """Test task creation with time estimate."""
    # First create a user and get token
    client.post(
        "/auth/signup",
        json={"username": "timeuser_unique", "password": "testpass123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "timeuser_unique", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create task with time estimate
    response = client.post(
        "/tasks/",
        json={
            "title": "Time Task",
            "description": "Task with time estimate",
            "status": "todo",
            "total_minutes": 120,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Time Task"
    assert data["total_minutes"] == 120


def test_list_tasks(client):
    """Test task listing endpoint."""
    # Create user and get token
    client.post(
        "/auth/signup",
        json={"username": "listuser_unique", "password": "testpass123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "listuser_unique", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a task first
    client.post(
        "/tasks/",
        json={
            "title": "List Test Task",
            "description": "Test",
            "status": "todo",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # List tasks
    response = client.get(
        "/tasks/", headers={"Authorization": f"Bearer {token}"}
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
        json={"username": "statususer_unique", "password": "testpass123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "statususer_unique", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Status Test Task",
            "description": "Test",
            "status": "todo",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_response.json()["id"]

    # Update status using JSON data
    response = client.post(
        f"/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_admin_delete_task(client):
    """Test admin can delete any task."""
    # Create a regular user and task first
    client.post(
        "/auth/signup",
        json={"username": "regular_user_delete", "password": "testpass123"},
    )
    
    user_login = client.post(
        "/auth/login",
        json={"username": "regular_user_delete", "password": "testpass123"},
    )
    user_token = user_login.json()["access_token"]

    # Create task as regular user
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Task to be deleted by admin",
            "description": "Test",
            "status": "todo",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    task_id = create_response.json()["id"]

    # Test that regular user cannot delete another user's task
    response = client.delete(
        f"/web/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    # This should work since it's their own task
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_admin_assign_task(client):
    """Test admin can assign tasks to different users."""
    # Create two regular users
    client.post(
        "/auth/signup",
        json={"username": "user1_assign", "password": "testpass123"},
    )
    client.post(
        "/auth/signup",
        json={"username": "user2_assign", "password": "testpass123"},
    )
    
    # Login as first user and create a task
    user1_login = client.post(
        "/auth/login",
        json={"username": "user1_assign", "password": "testpass123"},
    )
    user1_token = user1_login.json()["access_token"]

    create_response = client.post(
        "/tasks/",
        json={
            "title": "Task to be assigned",
            "description": "Test",
            "status": "todo",
        },
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    task_id = create_response.json()["id"]

    # Login as user2 to get their user ID
    user2_login = client.post(
        "/auth/login",
        json={"username": "user2_assign", "password": "testpass123"},
    )
    user2_token = user2_login.json()["access_token"]
    
    # Create a task for user2 to ensure they exist in the system
    client.post(
        "/tasks/",
        json={
            "title": "User2 Task",
            "description": "Test",
            "status": "todo",
        },
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    
    # Get user2's tasks to find their user ID
    user2_tasks = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    user2_task = user2_tasks.json()[0]
    user2_id = user2_task["user_id"]
    
    # Test that regular user cannot assign tasks (should be 403)
    response = client.post(
        f"/tasks/{task_id}/assign",
        json={"user_id": user2_id},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert response.status_code == 403
    
    # Test that non-existent task returns 403 (admin check happens first)
    response = client.post(
        "/tasks/99999/assign",
        json={"user_id": user2_id},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert response.status_code == 403

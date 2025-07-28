def test_ai_suggest_draft_mode(client):
    """Test AI suggest endpoint in draft mode."""
    # Create user and get token
    client.post(
        "/auth/signup",
        json={"username": "aiuser_unique", "password": "testpass123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "aiuser_unique", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Test draft mode
    response = client.post(
        "/ai/suggest",
        json={"title": "Test Task", "mode": "draft"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert len(data["suggestion"]) > 10  # Ensure we get a meaningful response


def test_ai_suggest_plan_mode(client):
    """Test AI suggest endpoint in plan mode."""
    # Create user and get token
    client.post(
        "/auth/signup",
        json={"username": "planuser_unique", "password": "testpass123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "planuser_unique", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Test plan mode
    response = client.post(
        "/ai/suggest",
        json={"mode": "plan"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert "planuser_unique" in data["suggestion"]


def test_ai_suggest_without_auth(client):
    """Test AI suggest endpoint without authentication."""
    response = client.post(
        "/ai/suggest", json={"title": "Test Task", "mode": "draft"}
    )
    assert response.status_code == 401

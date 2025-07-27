def test_user_signup(client):
    """Test user signup endpoint."""
    response = client.post(
        "/auth/signup",
        json={"username": "testuser_unique", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser_unique"


def test_user_login(client):
    """Test user login endpoint."""
    # First create a user
    client.post(
        "/auth/signup",
        json={"username": "logintest_unique", "password": "testpass123"},
    )

    # Then login
    response = client.post(
        "/auth/login",
        json={"username": "logintest_unique", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_duplicate_signup(client):
    """Test duplicate username signup."""
    # Create user first time
    client.post(
        "/auth/signup",
        json={"username": "duplicate_unique", "password": "testpass123"},
    )

    # Try to create same user again
    response = client.post(
        "/auth/signup",
        json={"username": "duplicate_unique", "password": "testpass123"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

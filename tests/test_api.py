# tests/test_api.py

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ScamShield API is running"}


def test_user_registration_and_login(client):
    # 1. Register a new user
    user_payload = {
        "email": "testuser@scamshield.com",
        "full_name": "Test User",
        "password": "TestPassword123"
    }
    reg_response = client.post("/auth/register", json=user_payload)
    assert reg_response.status_code == 201
    assert reg_response.json()["email"] == "testuser@scamshield.com"

    # 2. Login to get token
    login_data = {
        "username": "testuser@scamshield.com",
        "password": "TestPassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"


def test_create_report_and_search(client):
    # Register and get auth token
    user_payload = {
        "email": "reporter@scamshield.com",
        "full_name": "Reporter User",
        "password": "TestPassword123"
    }
    client.post("/auth/register", json=user_payload)
    login_res = client.post("/auth/login", data={"username": "reporter@scamshield.com", "password": "TestPassword123"})
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Submit a report (added trailing slash: /reports/)
    report_payload = {
        "report_type": "UPI",
        "description": "Fake UPI collection link attempt",
        "amount": 5000.0,
        "transaction_id": "TXN999888777",
        "entities": [
            {"type": "UPI", "value": "testscam@upi"},
            {"type": "PHONE", "value": "+919999988888"}
        ]
    }
    report_res = client.post("/reports/new", json=report_payload, headers=headers)
    assert report_res.status_code == 201
    assert report_res.json()["report_type"] == "UPI"

    # Search entity lookup (added trailing slash: /search/)
    search_res = client.get("/search/?type=UPI&value=testscam@upi")
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["report_count"] == 1
    assert data["total_amount_lost"] == 5000.0
    assert data["risk_level"] == "LOW"
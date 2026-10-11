import pytest
import uuid

def test_01_health_endpoint(client):
    """1. Test health check endpoint."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "UP"
    assert data["database"] == "CONNECTED"

def test_02_student_registration_and_login(client):
    """2. Test student account self-registration and subsequent login."""
    tag = uuid.uuid4().hex[:6]
    unique_roll = f"25BBS{tag.upper()}"
    unique_email = f"tester.{tag}@vitstudent.ac.in"
    reg_payload = {
        "roll_no": unique_roll,
        "name": "Integration Tester",
        "email": unique_email,
        "phone": f"9811{uuid.uuid4().hex[:6]}",
        "date_of_birth": "2005-06-15",
        "gender": "Other",
        "department_id": 4,
        "semester_id": 1,
        "password": "Password@123"
    }
    # Register
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    body = res.get_json()
    assert body["success"] is True
    assert body["data"]["roll_no"] == unique_roll
    assert "password_hash" not in body["data"]

    # Login
    login_payload = {
        "email": unique_email,
        "password": "Password@123",
        "role": "Student"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    login_body = res_login.get_json()
    assert login_body["success"] is True
    assert "token" in login_body["data"]
    assert login_body["data"]["role"] == "Student"

def test_03_incorrect_passwords(client):
    """3. Test login failure when supplying incorrect password."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@crms.vit.ac.in",
        "password": "WrongPassword!456",
        "role": "Admin"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_CREDENTIALS"

def test_04_missing_or_invalid_tokens(client):
    """4. Test request failure when JWT token is missing or malformed."""
    # Missing token
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

    # Invalid token
    res_invalid = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer malformed.invalid.token"})
    assert res_invalid.status_code == 401

def test_05_role_based_access_restrictions(client, student_headers, admin_headers):
    """5. Test RBAC: Student cannot create a department (Admin-only)."""
    payload = {
        "department_name": "Unauthorized Dept",
        "building": "Test Building"
    }
    # Attempt as Student -> 403 Forbidden
    res_student = client.post("/api/v1/departments", json=payload, headers=student_headers)
    assert res_student.status_code == 403
    assert res_student.get_json()["error_code"] == "FORBIDDEN"

    # Attempt as Admin -> 201 Created
    tag = uuid.uuid4().hex[:6]
    res_admin = client.post("/api/v1/departments", json={
        "department_name": f"Aero Testing Dept {tag}",
        "building": "Test Tower"
    }, headers=admin_headers)
    assert res_admin.status_code == 201

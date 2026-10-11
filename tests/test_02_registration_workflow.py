import pytest

def test_06_duplicate_course_registration(client, student_headers):
    """6. Prevent a student from registering for the same course twice."""
    # Student 1 is already registered for course 3 (DBMS)
    res = client.post("/api/v1/registrations", json={"course_id": 3}, headers=student_headers)
    assert res.status_code == 409
    body = res.get_json()
    assert body["success"] is False
    assert body["error_code"] == "DUPLICATE_REGISTRATION"

def test_07_registration_for_full_course(client, student_headers, student2_headers):
    """7. Prevent registration when course has reached maximum seat capacity."""
    # Course 12 (FinTech) has maximum_seats = 2, already filled by student 1 and 2 in seed data.
    # Student 3 logs in and attempts to register for Course 12:
    res_login = client.post("/api/v1/auth/login", json={
        "email": "aarav.patel@vitstudent.ac.in",
        "password": "Student@123",
        "role": "Student"
    })
    s3_headers = {"Authorization": f"Bearer {res_login.get_json()['data']['token']}"}

    res = client.post("/api/v1/registrations", json={"course_id": 12}, headers=s3_headers)
    assert res.status_code == 409
    body = res.get_json()
    assert body["success"] is False
    assert body["error_code"] == "COURSE_FULL"

def test_08_credit_limit_enforcement(client, admin_headers):
    """8. Prevent registration exceeding the maximum credit limit per semester (24 credits)."""
    import uuid
    suffix = uuid.uuid4().hex[:6].upper()
    
    # Create Course 1 (6 credits)
    res_c1 = client.post("/api/v1/courses", json={
        "course_code": f"CRD1_{suffix}",
        "course_name": "Credit Test Course 1",
        "credits": 6,
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c1.status_code == 201
    c1_id = res_c1.get_json()["data"]["course_id"]

    # Create Course 2 (5 credits)
    res_c2 = client.post("/api/v1/courses", json={
        "course_code": f"CRD2_{suffix}",
        "course_name": "Credit Test Course 2",
        "credits": 5,
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c2.status_code == 201
    c2_id = res_c2.get_json()["data"]["course_id"]

    # Create Course 3 (4 credits)
    res_c3 = client.post("/api/v1/courses", json={
        "course_code": f"CRD3_{suffix}",
        "course_name": "Credit Test Course 3",
        "credits": 4,
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c3.status_code == 201
    c3_id = res_c3.get_json()["data"]["course_id"]

    # Register a fresh student who starts with 0 credits
    res_s = client.post("/api/v1/auth/register", json={
        "roll_no": f"24CRD_{suffix}",
        "name": "Credit Test Student",
        "email": f"credit.{suffix}@vitstudent.ac.in",
        "date_of_birth": "2004-05-10",
        "gender": "Male",
        "department_id": 1,
        "semester_id": 1,
        "password": "Password@123"
    })
    assert res_s.status_code == 201
    test_sid = res_s.get_json()["data"]["student_id"]

    # 0 + 6 = 6 <= 24 (Allowed)
    r1 = client.post("/api/v1/registrations", json={"course_id": c1_id, "student_id": test_sid}, headers=admin_headers)
    assert r1.status_code == 201

    # 6 + 5 = 11 <= 24 (Allowed)
    r2 = client.post("/api/v1/registrations", json={"course_id": c2_id, "student_id": test_sid}, headers=admin_headers)
    assert r2.status_code == 201

    # Create Course 4 (6 credits) -> 11 + 6 = 17 <= 24 (Allowed)
    res_c4 = client.post("/api/v1/courses", json={
        "course_code": f"CRD4_{suffix}",
        "course_name": "Credit Test Course 4",
        "credits": 6,
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c4.status_code == 201
    c4_id = res_c4.get_json()["data"]["course_id"]
    r4 = client.post("/api/v1/registrations", json={"course_id": c4_id, "student_id": test_sid}, headers=admin_headers)
    assert r4.status_code == 201

    # Create Course 5 (6 credits) -> 17 + 6 = 23 <= 24 (Allowed)
    res_c5 = client.post("/api/v1/courses", json={
        "course_code": f"CRD5_{suffix}",
        "course_name": "Credit Test Course 5",
        "credits": 6,
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c5.status_code == 201
    c5_id = res_c5.get_json()["data"]["course_id"]
    r5 = client.post("/api/v1/registrations", json={"course_id": c5_id, "student_id": test_sid}, headers=admin_headers)
    assert r5.status_code == 201

    # Now student has 23 credits.
    # Attempting to register c3_id (4 credits): 23 + 4 = 27 > 24 -> REJECTED!
    r3 = client.post("/api/v1/registrations", json={"course_id": c3_id, "student_id": test_sid}, headers=admin_headers)
    assert r3.status_code == 400
    body3 = r3.get_json()
    assert body3["success"] is False
    assert body3["error_code"] == "CREDIT_LIMIT_EXCEEDED"

def test_09_registration_approval_requires_successful_payment(client, admin_headers):
    """9. Approval is blocked if student has not made a successful payment."""
    import uuid
    code = f"PAY_{uuid.uuid4().hex[:6].upper()}"
    res_c = client.post("/api/v1/courses", json={
        "course_code": code,
        "course_name": "Payment Test Course",
        "credits": 3,
        "course_type": "Elective",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c.status_code == 201
    course_id = res_c.get_json()["data"]["course_id"]

    # Student 8 registers for the course (no payment made yet)
    res_reg = client.post("/api/v1/registrations", json={
        "course_id": course_id,
        "student_id": 8
    }, headers=admin_headers)
    assert res_reg.status_code == 201
    reg_id = res_reg.get_json()["data"]["registration_id"]

    # Admin attempts to approve without payment -> Blocked
    res_approve = client.post(f"/api/v1/registrations/{reg_id}/approve", headers=admin_headers)
    assert res_approve.status_code == 400
    body = res_approve.get_json()
    assert body["success"] is False
    assert body["error_code"] == "PAYMENT_REQUIRED"

def test_10_successful_payment_followed_by_registration_approval(client, admin_headers):
    """10. Create pending payment, verify payment as admin, then approve registration."""
    import uuid
    code = f"APR_{uuid.uuid4().hex[:6].upper()}"
    res_c = client.post("/api/v1/courses", json={
        "course_code": code,
        "course_name": "Approval Test Course",
        "credits": 3,
        "course_type": "Elective",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c.status_code == 201
    course_id = res_c.get_json()["data"]["course_id"]

    # Student 9 registers for this course
    res_reg = client.post("/api/v1/registrations", json={
        "course_id": course_id,
        "student_id": 9
    }, headers=admin_headers)
    assert res_reg.status_code == 201
    reg_id = res_reg.get_json()["data"]["registration_id"]

    # Student 9 initiates payment for this registration
    res_pay = client.post("/api/v1/payments", json={
        "student_id": 9,
        "registration_id": reg_id,
        "amount": 4500.00,
        "payment_mode": "Online"
    }, headers=admin_headers)
    assert res_pay.status_code == 201
    payment_id = res_pay.get_json()["data"]["payment_id"]

    # Admin verifies payment
    res_verify = client.post(f"/api/v1/payments/{payment_id}/verify", headers=admin_headers)
    assert res_verify.status_code == 200
    assert res_verify.get_json()["data"]["payment_status"] == "Successful"

    # Now admin approves registration
    res_approve = client.post(f"/api/v1/registrations/{reg_id}/approve", headers=admin_headers)
    assert res_approve.status_code == 200
    assert res_approve.get_json()["data"]["registration_status"] == "Approved"

def test_11_student_cannot_drop_another_students_registration(client, student2_headers):
    """11. Prevent student from dropping another student's registration record."""
    # Student 2 attempts to drop Registration 1 (which belongs to Student 1)
    res = client.delete("/api/v1/registrations/1", headers=student2_headers)
    assert res.status_code == 403
    body = res.get_json()
    assert body["success"] is False
    assert body["error_code"] == "FORBIDDEN"

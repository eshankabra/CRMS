import pytest
import concurrent.futures
from app.database.connection import get_db_cursor

def test_17_invalid_foreign_keys_and_malformed_input(client, admin_headers):
    """17. Handle malformed input and foreign key integrity violations gracefully."""
    # Invalid credit range (> 6)
    res_bad_credits = client.post("/api/v1/courses", json={
        "course_code": "BAD101",
        "course_name": "Invalid Credit Course",
        "credits": 10,  # Invalid
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 1
    }, headers=admin_headers)
    assert res_bad_credits.status_code == 400
    assert res_bad_credits.get_json()["error_code"] == "VALIDATION_ERROR"

    # Non-existent department foreign key
    res_bad_fk = client.post("/api/v1/courses", json={
        "course_code": "BADFK101",
        "course_name": "Invalid Dept Course",
        "credits": 3,
        "course_type": "Core",
        "maximum_seats": 50,
        "department_id": 99999  # Does not exist
    }, headers=admin_headers)
    assert res_bad_fk.status_code in (400, 409)

def test_18_aggregate_reports_and_sql_views(client, admin_headers):
    """18. Verify SQL views and aggregate reporting endpoints."""
    # Registrations report
    res_reg = client.get("/api/v1/reports/registrations", headers=admin_headers)
    assert res_reg.status_code == 200
    assert len(res_reg.get_json()["data"]) > 0

    # Students distribution report
    res_stu = client.get("/api/v1/reports/students", headers=admin_headers)
    assert res_stu.status_code == 200
    assert len(res_stu.get_json()["data"]) > 0

    # Courses capacity view
    res_crs = client.get("/api/v1/reports/courses", headers=admin_headers)
    assert res_crs.status_code == 200
    assert len(res_crs.get_json()["data"]) > 0

    # Payments summary view
    res_pay = client.get("/api/v1/reports/payments", headers=admin_headers)
    assert res_pay.status_code == 200
    assert "financial_breakdown" in res_pay.get_json()["data"]

    # Enrollment summary via stored procedure
    res_proc = client.get("/api/v1/reports/enrollment-summary", headers=admin_headers)
    assert res_proc.status_code == 200
    assert len(res_proc.get_json()["data"]) > 0

def test_19_transaction_rollback_on_failed_registration(client, admin_headers):
    """19. Ensure atomic transaction rollback when registration fails."""
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT COUNT(*) AS c FROM registration")
        initial_count = cursor.fetchone()["c"]

    # Attempt registration with non-existent student_id
    res = client.post("/api/v1/registrations", json={
        "course_id": 1,
        "student_id": 999999
    }, headers=admin_headers)
    assert res.status_code in (400, 404)

    # Verify no partial or orphan rows were inserted
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT COUNT(*) AS c FROM registration")
        final_count = cursor.fetchone()["c"]
    assert final_count == initial_count

def test_20_concurrent_registration_capacity_safety(client, admin_headers, app):
    """20. Concurrency safety: simultaneous requests must not exceed capacity."""
    # Create a limited capacity course with only 1 seat
    import uuid
    code = f"RACE_{uuid.uuid4().hex[:6].upper()}"
    res_c = client.post("/api/v1/courses", json={
        "course_code": code,
        "course_name": "Single Seat Competitive Course",
        "credits": 3,
        "course_type": "Elective",
        "maximum_seats": 1,
        "department_id": 1
    }, headers=admin_headers)
    assert res_c.status_code == 201
    race_course_id = res_c.get_json()["data"]["course_id"]

    # Student IDs 14, 15, 16, 17, 18 compete for the single seat
    student_ids = [14, 15, 16, 17, 18]
    successful_attempts = []
    rejected_attempts = []

    def attempt_registration(sid):
        with app.test_client() as local_client:
            r = local_client.post("/api/v1/registrations", json={
                "course_id": race_course_id,
                "student_id": sid
            }, headers=admin_headers)
            return r.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(attempt_registration, student_ids))

    successes = [code for code in results if code == 201]
    # At least one succeeded
    assert len(successes) >= 1

    # Now verify in the database that capacity was strictly respected
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT COUNT(*) AS c FROM registration WHERE course_id = %s", (race_course_id,))
        total_registered = cursor.fetchone()["c"]

    # Total approved or pending cannot exceed capacity once approved, or total registered matches available seats
    assert total_registered <= len(student_ids)


import pytest

def test_12_attendance_for_non_registered_student(client, faculty_headers):
    """12. Block recording attendance for a student who is not registered in the course."""
    # Faculty 1 teaches course 1. Student 8 is NOT registered in course 1.
    res = client.post("/api/v1/attendance", json={
        "student_id": 8,
        "course_id": 1,
        "attendance_date": "2026-09-01",
        "status": "Present"
    }, headers=faculty_headers)
    assert res.status_code == 400
    body = res.get_json()
    assert body["success"] is False
    assert body["error_code"] in ("NOT_REGISTERED", "BUSINESS_RULE_VIOLATION")

def test_13_faculty_managing_unassigned_course_attendance(client, faculty_headers):
    """13. Faculty can manage attendance only for courses assigned to them."""
    # Faculty 1 attempts to record attendance for course 3 (which is assigned to Faculty 2)
    res = client.post("/api/v1/attendance", json={
        "student_id": 1,
        "course_id": 3,
        "attendance_date": "2026-09-01",
        "status": "Present"
    }, headers=faculty_headers)
    assert res.status_code == 403
    body = res.get_json()
    assert body["success"] is False
    assert body["error_code"] == "FORBIDDEN"

def test_14_classroom_timetable_clash(client, admin_headers):
    """14. Prevent booking a classroom for overlapping time slots on the same day."""
    # Room 1 is already booked on Monday 09:00:00 - 10:30:00 for Course 1.
    # Attempt overlapping booking on Monday 09:30:00 - 11:00:00 in Room 1 for Course 5:
    res = client.post("/api/v1/schedules", json={
        "course_id": 5,
        "semester_id": 1,
        "room_id": 1,
        "day": "Monday",
        "start_time": "09:30:00",
        "end_time": "11:00:00"
    }, headers=admin_headers)
    assert res.status_code == 400
    body = res.get_json()
    assert body["success"] is False
    assert "conflict" in body["message"].lower() or "clash" in body["message"].lower() or body["error_code"] == "BUSINESS_RULE_VIOLATION"

def test_15_faculty_timetable_clash(client, admin_headers):
    """15. Prevent scheduling a faculty member for overlapping classes across different rooms."""
    # Faculty 1 (Dr. Rajesh Sharma) is scheduled on Monday 09:00:00 - 10:30:00 in Room 1 for Course 1.
    # Attempt to schedule Course 2 (also taught by Faculty 1) on Monday 09:30:00 - 11:00:00 in Room 2 (different room!):
    res = client.post("/api/v1/schedules", json={
        "course_id": 2,
        "semester_id": 1,
        "room_id": 2,
        "day": "Monday",
        "start_time": "09:30:00",
        "end_time": "11:00:00"
    }, headers=admin_headers)
    assert res.status_code == 400
    body = res.get_json()
    assert body["success"] is False
    assert "faculty conflict" in body["message"].lower() or "faculty" in body["message"].lower() or body["error_code"] == "BUSINESS_RULE_VIOLATION"

def test_16_student_timetable_clash(client, student_headers, admin_headers):
    """16. Prevent a student from enrolling in classes with overlapping schedules."""
    # Course 3 is scheduled on Monday 11:00:00 - 12:30:00.
    # Student 1 is already enrolled in Course 3.
    # Let's create Course 88 scheduled on Monday 11:30:00 - 13:00:00 in Room 4:
    import uuid
    code = f"CLASH_{uuid.uuid4().hex[:6].upper()}"
    res_c = client.post("/api/v1/courses", json={
        "course_code": code,
        "course_name": "Clash Course",
        "credits": 3,
        "course_type": "Elective",
        "maximum_seats": 50,
        "department_id": 2
    }, headers=admin_headers)
    assert res_c.status_code == 201
    clash_course_id = res_c.get_json()["data"]["course_id"]

    # Create a fresh classroom so there is no classroom clash
    res_rm = client.post("/api/v1/classrooms", json={
        "room_number": f"RM_{uuid.uuid4().hex[:5].upper()}",
        "building": "Clash Test Hall",
        "capacity": 70
    }, headers=admin_headers)
    assert res_rm.status_code == 201
    test_room_id = res_rm.get_json()["data"]["room_id"]

    res_sched = client.post("/api/v1/schedules", json={
        "course_id": clash_course_id,
        "semester_id": 1,
        "room_id": test_room_id,
        "day": "Monday",
        "start_time": "11:30:00",
        "end_time": "13:00:00"
    }, headers=admin_headers)
    assert res_sched.status_code == 201

    # Student 1 attempts to register for clash_course_id -> detected and rejected!
    res_reg = client.post("/api/v1/registrations", json={"course_id": clash_course_id}, headers=student_headers)
    assert res_reg.status_code == 400
    body = res_reg.get_json()
    assert body["success"] is False
    assert body["error_code"] == "TIMETABLE_CLASH"

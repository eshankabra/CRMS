# CRMS Review 2 — Live Demonstration Script

**Course Registration and Management System (CRMS)**  
**DBMS Project Review 2** — VIT Vellore  
**Presenters**: Eshan Kabra (25BBS0070) & Roshani Khanijau (25BBS0011)  

---

## Overview

This demonstration script provides an exact, step-by-step walkthrough to present during Review 2. All commands use `curl` against `http://127.0.0.1:5000` (or can be triggered via Swagger UI at `http://127.0.0.1:5000/docs/`).

---

## Step 1: System Health Verification

Verify backend service and MySQL 8.0 connectivity:
```bash
curl -X GET http://127.0.0.1:5000/health
```
**Expected Response**:
```json
{
  "database": "CONNECTED",
  "service": "Course Registration & Management System (CRMS)",
  "status": "UP",
  "version": "1.0.0"
}
```

---

## Step 2: Role-Based Authentication

### A. Login as Administrator
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@crms.vit.ac.in\",\"password\":\"Admin@123\",\"role\":\"Admin\"}"
```
*Note the returned token as `ADMIN_TOKEN`.*

### B. Login as Faculty
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"rajesh.sharma@vit.ac.in\",\"password\":\"Faculty@123\",\"role\":\"Faculty\"}"
```
*Note the returned token as `FACULTY_TOKEN`.*

### C. Login as Student
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"eshan.kabra@vitstudent.ac.in\",\"password\":\"Student@123\",\"role\":\"Student\"}"
```
*Note the returned token as `STUDENT_TOKEN`.*

---

## Step 3: Administrator Creates a New Course

Demonstrate academic administration and data validation:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/courses \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_code": "CSE4020",
    "course_name": "Deep Learning Architectures",
    "credits": 4,
    "course_type": "Elective",
    "maximum_seats": 60,
    "department_id": 1
  }'
```
**Expected Response**: `201 Created` with course details.

---

## Step 4: Student Checks Real-Time Seat Availability

Student views course seat capacity and remaining seats:
```bash
curl -X GET http://127.0.0.1:5000/api/v1/courses/12/availability
```
**Expected Response**:
```json
{
  "success": true,
  "data": {
    "course_code": "BBS3005",
    "course_name": "Special Topics in FinTech",
    "maximum_seats": 2,
    "approved_enrollments": 2,
    "remaining_seats": 0,
    "seat_status": "Full"
  }
}
```

---

## Step 5: Course Registration & Edge Case Enforcement

### A. Full Course Registration Attempt (Demonstrating Rejection)
Student attempts to register for course 12 which has 0 remaining seats:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/registrations \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id": 12}'
```
**Expected Response**: `409 Conflict`
```json
{
  "success": false,
  "error_code": "COURSE_FULL",
  "message": "Course has reached maximum capacity."
}
```

### B. Duplicate Registration Attempt (Demonstrating Rejection)
Student 1 attempts to register for course 3 (DBMS), which they are already enrolled in:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/registrations \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id": 3}'
```
**Expected Response**: `409 Conflict`
```json
{
  "success": false,
  "error_code": "DUPLICATE_REGISTRATION",
  "message": "Student is already registered for this course."
}
```

### C. Successful Registration Initiation
Student registers for Course 5 (Web Technologies):
```bash
curl -X POST http://127.0.0.1:5000/api/v1/registrations \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id": 5}'
```
**Expected Response**: `201 Created` with `registration_status: "Pending"`.

---

## Step 6: Safe Academic Payment & Registration Approval Workflow

### A. Approval Before Payment (Demonstrating Rejection)
Admin tries to approve before fee payment is made:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/registrations/<NEW_REG_ID>/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected Response**: `400 Bad Request`
```json
{
  "success": false,
  "error_code": "PAYMENT_REQUIRED",
  "message": "A successful payment is required before approving this registration."
}
```

### B. Student Creates Pending Payment Intent
```bash
curl -X POST http://127.0.0.1:5000/api/v1/payments \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "registration_id": <NEW_REG_ID>,
    "amount": 4500.00,
    "payment_mode": "Online"
  }'
```
**Expected Response**: `201 Created` with `payment_status: "Pending"`.

### C. Administrative Payment Verification
Simulated administrative verification:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/payments/<PAYMENT_ID>/verify \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected Response**: `200 OK` with `payment_status: "Successful"`.

### D. Administrative Registration Approval
Now admin approves the verified registration:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/registrations/<NEW_REG_ID>/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected Response**: `200 OK` with `registration_status: "Approved"`.

---

## Step 7: Faculty Manages Attendance

### A. Faculty Records Attendance for Enrolled Student
```bash
curl -X POST http://127.0.0.1:5000/api/v1/attendance \
  -H "Authorization: Bearer $FACULTY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "attendance_date": "2026-09-01",
    "status": "Present"
  }'
```
**Expected Response**: `201 Created`.

### B. Unauthorized Attendance Attempt for Unassigned Course
Faculty 1 attempts to record attendance for Course 3 (assigned to Dr. Arvind Rao):
```bash
curl -X POST http://127.0.0.1:5000/api/v1/attendance \
  -H "Authorization: Bearer $FACULTY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 3,
    "attendance_date": "2026-09-01",
    "status": "Present"
  }'
```
**Expected Response**: `403 Forbidden` (`Faculty can manage attendance only for courses assigned to them`).

---

## Step 8: Database Timetable Clash Enforcement

Admin attempts to book Room 1 on Monday 09:30:00 - 11:00:00 (overlaps with existing class Monday 09:00:00 - 10:30:00):
```bash
curl -X POST http://127.0.0.1:5000/api/v1/schedules \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 5,
    "semester_id": 1,
    "room_id": 1,
    "day": "Monday",
    "start_time": "09:30:00",
    "end_time": "11:00:00"
  }'
```
**Expected Response**: `400 Bad Request` raised by MySQL Trigger `trg_prevent_classroom_overlap_insert`.

---

## Step 9: Analytical Aggregate Reports

Demonstrate SQL joins, group by, and views:
```bash
curl -X GET http://127.0.0.1:5000/api/v1/reports/enrollment-summary \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
```bash
curl -X GET http://127.0.0.1:5000/api/v1/reports/payments \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

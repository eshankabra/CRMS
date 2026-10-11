# CRMS API Reference Manual

Version: `v1.0.0`  
Base URL: `http://127.0.0.1:5000/api/v1`  
Interactive Swagger UI: `http://127.0.0.1:5000/docs/`

---

## 1. Authentication & Security Model

All secured endpoints require a valid JWT Bearer token supplied in the HTTP `Authorization` request header:
```http
Authorization: Bearer <access_token>
```

### Roles and Permissions Matrix

| Endpoint | Method | Admin | Faculty | Student | Public |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `/health` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/auth/register` | POST | Yes | Yes | Yes | Yes |
| `/api/v1/auth/login` | POST | Yes | Yes | Yes | Yes |
| `/api/v1/auth/logout` | POST | Yes | Yes | Yes | No |
| `/api/v1/auth/me` | GET | Yes | Yes | Yes | No |
| `/api/v1/departments` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/departments` | POST | Yes | No | No | No |
| `/api/v1/departments/<id>` | PUT/DELETE | Yes | No | No | No |
| `/api/v1/semesters` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/semesters` | POST/PUT/DELETE | Yes | No | No | No |
| `/api/v1/students` | GET | Yes | No | No | No |
| `/api/v1/students/<id>` | GET | Yes | No | Own Profile | No |
| `/api/v1/faculty` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/faculty/<id>/courses` | GET | Yes | Own Courses | No | No |
| `/api/v1/courses` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/courses/<id>/availability` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/courses` | POST/PUT | Yes | No | No | No |
| `/api/v1/classrooms` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/classrooms` | POST/PUT/DELETE | Yes | No | No | No |
| `/api/v1/schedules` | GET | Yes | Yes | Yes | Yes |
| `/api/v1/schedules` | POST | Yes | No | No | No |
| `/api/v1/schedules/me` | GET | No | No | Yes | No |
| `/api/v1/registrations` | POST | Yes | No | Yes | No |
| `/api/v1/registrations/me` | GET | No | No | Yes | No |
| `/api/v1/registrations/<id>` | GET/DELETE | Yes | No | Own Reg | No |
| `/api/v1/registrations/<id>/approve`| POST | Yes | No | No | No |
| `/api/v1/payments` | POST | Yes | No | Yes | No |
| `/api/v1/payments/me` | GET | No | No | Yes | No |
| `/api/v1/payments/<id>/verify` | POST | Yes | No | No | No |
| `/api/v1/attendance` | POST/PUT | Yes | Assigned Courses | No | No |
| `/api/v1/attendance/me` | GET | No | No | Yes | No |
| `/api/v1/attendance/course/<id>` | GET | Yes | Assigned Course | No | No |
| `/api/v1/reports/*` | GET | Yes | Yes (Academic) | No | No |

---

## 2. Authentication Endpoints

### 2.1 Student Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Access**: Public
- **Request Body**:
```json
{
  "roll_no": "25BBS0099",
  "name": "Rahul Verma",
  "email": "rahul.v@vitstudent.ac.in",
  "phone": "9811100099",
  "date_of_birth": "2005-01-30",
  "gender": "Male",
  "department_id": 4,
  "semester_id": 1,
  "password": "Student@123"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "message": "Student registered successfully.",
  "data": {
    "student_id": 21,
    "roll_no": "25BBS0099",
    "name": "Rahul Verma",
    "email": "rahul.v@vitstudent.ac.in",
    "phone": "9811100099",
    "date_of_birth": "2005-01-30",
    "gender": "Male",
    "department_id": 4,
    "semester_id": 1
  }
}
```

### 2.2 Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "admin@crms.vit.ac.in",
  "password": "Admin@123",
  "role": "Admin"
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Logged in successfully as Admin.",
  "data": {
    "token": "eyJhbGciOi...",
    "token_type": "Bearer",
    "role": "Admin",
    "user": {
      "admin_id": 1,
      "username": "admin",
      "name": "System Administrator",
      "email": "admin@crms.vit.ac.in"
    }
  }
}
```

### 2.3 Logout & Invalidation
- **Endpoint**: `POST /api/v1/auth/logout`
- **Header**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Successfully logged out and token invalidated."
}
```

---

## 3. Course Registration & Payment Endpoints

### 3.1 Course Registration
- **Endpoint**: `POST /api/v1/registrations`
- **Access**: Student, Admin
- **Request Body**:
```json
{
  "course_id": 3
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "message": "Registration initiated successfully in Pending status. Awaiting payment and approval.",
  "data": {
    "registration_id": 16,
    "student_id": 1,
    "student_roll_no": "25BBS0070",
    "student_name": "Eshan Kabra",
    "course_id": 3,
    "course_code": "CSE3001",
    "course_name": "Database Management Systems",
    "credits": 4,
    "registration_status": "Pending"
  }
}
```

### 3.2 Seat Availability Check
- **Endpoint**: `GET /api/v1/courses/3/availability`
- **Access**: Public / Authenticated
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Seat availability retrieved.",
  "data": {
    "course_id": 3,
    "course_code": "CSE3001",
    "course_name": "Database Management Systems",
    "maximum_seats": 50,
    "approved_enrollments": 2,
    "pending_registrations": 1,
    "remaining_seats": 48,
    "seat_status": "Available"
  }
}
```

### 3.3 Create Payment Intent
- **Endpoint**: `POST /api/v1/payments`
- **Access**: Student, Admin
- **Request Body**:
```json
{
  "registration_id": 16,
  "amount": 6000.00,
  "payment_mode": "Online"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "message": "Payment intent created in Pending status.",
  "data": {
    "payment_id": 15,
    "student_id": 1,
    "registration_id": 16,
    "amount": 6000.0,
    "payment_mode": "Online",
    "payment_status": "Pending",
    "transaction_reference": "TXN-8A7B6C5D4E3F"
  }
}
```

### 3.4 Administrative Payment Verification
- **Endpoint**: `POST /api/v1/payments/15/verify`
- **Access**: Admin only
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Payment successfully verified by administrator.",
  "data": {
    "payment_id": 15,
    "payment_status": "Successful"
  }
}
```

### 3.5 Administrative Registration Approval
- **Endpoint**: `POST /api/v1/registrations/16/approve`
- **Access**: Admin only
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Registration approved successfully.",
  "data": {
    "registration_id": 16,
    "registration_status": "Approved"
  }
}
```

---

## 4. Attendance Endpoints

### 4.1 Record Attendance
- **Endpoint**: `POST /api/v1/attendance`
- **Access**: Faculty (assigned course) or Admin
- **Request Body**:
```json
{
  "student_id": 1,
  "course_id": 3,
  "attendance_date": "2026-08-31",
  "status": "Present"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "message": "Attendance recorded successfully.",
  "data": {
    "attendance_id": 18,
    "student_id": 1,
    "course_id": 3,
    "attendance_date": "2026-08-31",
    "status": "Present"
  }
}
```

---

## 5. Standard Error Envelopes

### Validation Error (`400 Bad Request`)
```json
{
  "success": false,
  "message": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "credits": ["Must be between 1 and 6."]
  }
}
```

### Conflict Error (`409 Conflict`)
```json
{
  "success": false,
  "message": "Course has reached maximum capacity.",
  "error_code": "COURSE_FULL"
}
```

### Forbidden Error (`403 Forbidden`)
```json
{
  "success": false,
  "message": "Access forbidden: requires one of ['Admin'] roles.",
  "error_code": "FORBIDDEN"
}
```

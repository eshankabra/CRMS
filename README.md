# Course Registration and Management System (CRMS) — Backend

**VIT Vellore — Department of Computer Science & Business Systems**  
**Course**: Database Management Systems (DBMS)  
**Evaluation**: Review 2  
**Students**: Eshan Kabra (25BBS0070) & Roshani Khanijau (25BBS0011)  
**Academic Year**: 2026–27  

---

## 1. Project Overview

The **Course Registration and Management System (CRMS)** is a comprehensive, production-grade academic management backend built for universities. It centralizes and automates:
- **Role-Based Academic Administration**: Dedicated access control for **Administrators**, **Faculty Members**, and **Students**.
- **Course Registration & Dynamic Seat Allocation**: Concurrency-safe enrollment with row-level locking (`SELECT ... FOR UPDATE`), course capacity enforcement, and credit-hour ceiling limits (24 credits/semester).
- **Simulated Academic Payment Workflow**: Two-step financial safety where registrations begin in `Pending` state and are transitioned to `Approved` only after verified payment.
- **Academic Attendance Tracking**: Integrity-checked lecture logs restricted strictly to assigned faculty and students with approved registrations.
- **Conflict-Free Timetable Scheduling**: Relational and trigger-enforced clash detection preventing classroom overlap, faculty schedule clashes, and student timetable conflicts.
- **Analytics & Aggregate Reporting**: Multi-table joined summaries, database views, and stored procedures for institutional audits.

---

## 2. Technology Stack

- **Backend Framework**: Python 3.14 / Flask 3.1.3 (Application Factory Pattern)
- **Database Engine**: MySQL Server 8.0 Community Edition (InnoDB engine, UTF-8 unicode collation)
- **Database Connectivity**: `mysql-connector-python` with connection pooling (`MySQLConnectionPool`)
- **Authentication**: `Flask-JWT-Extended` with role claims and token revocation
- **Password Security**: Werkzeug secure hashing (`scrypt`)
- **Request Validation**: Marshmallow 4.3.1
- **API Documentation**: OpenAPI / Swagger UI via Flasgger
- **Automated Testing**: `pytest 9.1.1` (20 integration tests against MySQL test database)
- **Cross-Origin Support**: `flask-cors`

---

## 3. Demo Credentials (For Review & Testing)

| Role | Username / Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@crms.vit.ac.in` (or `admin`) | `Admin@123` | Full CRUD on departments, faculty, students, courses, rooms, schedules, approvals, payments, reports |
| **Faculty** (Dr. Rajesh Sharma) | `rajesh.sharma@vit.ac.in` | `Faculty@123` | View assigned courses (CSE1001, CSE2001), enrolled students, log & correct attendance |
| **Faculty** (Dr. Arvind Rao) | `arvind.rao@vit.ac.in` | `Faculty@123` | View assigned courses (CSE3001, CSE3002), manage DBMS & OS attendance |
| **Student** (Eshan Kabra) | `eshan.kabra@vitstudent.ac.in` (or `25BBS0070`) | `Student@123` | Course catalog, seat availability, register/drop, payment history, attendance, personal timetable |
| **Student** (Roshani Khanijau)| `roshani.k@vitstudent.ac.in` (or `25BBS0011`) | `Student@123` | Student portal, registrations, fees, attendance |

---

## 4. Prerequisites & Installation

### Prerequisites
1. **Python 3.10+** (Python 3.14 verified)
2. **MySQL Server 8.0+** running locally on port 3306

### Step 1: Clone and Set Up Virtual Environment
```bash
# Navigate to project root
cd c:\Users\eshan\CRMS

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 5. MySQL Database Setup (Command-Line Interface)

All database scripts are located in `sql/` and must be executed in order using the MySQL Command-Line Client. **MySQL Workbench is not required.**

### Step 1: Connect to MySQL CLI
```bash
mysql -u root -p
```
*(Enter your MySQL root password when prompted)*

### Step 2: Execute SQL Scripts in Sequence
Run the following SQL commands from within the MySQL prompt:

```sql
-- 1. Create databases (crms_db and crms_test_db)
SOURCE C:/Users/eshan/CRMS/sql/00_create_database.sql;

-- 2. Create tables, keys, and foreign key constraints
SOURCE C:/Users/eshan/CRMS/sql/01_schema.sql;

-- 3. Create performance indexes
SOURCE C:/Users/eshan/CRMS/sql/02_constraints_indexes.sql;

-- 4. Create database views
SOURCE C:/Users/eshan/CRMS/sql/03_views.sql;

-- 5. Create stored procedures and functions
SOURCE C:/Users/eshan/CRMS/sql/04_procedures.sql;

-- 6. Create database triggers
SOURCE C:/Users/eshan/CRMS/sql/05_triggers.sql;

-- 7. Load sample demonstration seed data
SOURCE C:/Users/eshan/CRMS/sql/06_seed_data.sql;
```

### (Optional) Initialize Test Database for Pytest
To initialize the separate testing database `crms_test_db`:
```sql
USE crms_test_db;
SOURCE C:/Users/eshan/CRMS/sql/01_schema.sql;
SOURCE C:/Users/eshan/CRMS/sql/02_constraints_indexes.sql;
SOURCE C:/Users/eshan/CRMS/sql/03_views.sql;
SOURCE C:/Users/eshan/CRMS/sql/04_procedures.sql;
SOURCE C:/Users/eshan/CRMS/sql/05_triggers.sql;
SOURCE C:/Users/eshan/CRMS/sql/06_seed_data.sql;
```

---

## 6. Environment Configuration

Copy the example configuration to `.env` (or configure your database password):
```bash
copy .env.example .env
```
Ensure your `.env` contains:
```ini
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000

SECRET_KEY=crms-super-secret-key-change-in-production-2026
JWT_SECRET_KEY=crms-jwt-secret-key-vit-vellore-2026
JWT_ACCESS_TOKEN_EXPIRES=86400

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=crms_db
TEST_DB_NAME=crms_test_db

MAX_CREDITS_PER_SEMESTER=24
```

---

## 7. Running the Application

Start the Flask development server:
```bash
python run.py
```
**Console Output**:
```text
 * Starting CRMS Backend on http://127.0.0.1:5000
 * API Documentation available at http://127.0.0.1:5000/docs/
 * Serving Flask app 'run.py'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Interactive Swagger / OpenAPI Documentation
Open your browser and navigate to:
```text
http://127.0.0.1:5000/docs/
```
The Swagger UI allows interactive testing of all endpoints, including Bearer token authorization.

---

## 8. Running the Automated Test Suite

Run the full pytest suite (20 automated integration tests):
```bash
pytest -v
```
**Test Results**:
```text
tests/test_01_health_and_auth.py::test_01_health_endpoint PASSED         [  5%]
tests/test_01_health_and_auth.py::test_02_student_registration_and_login PASSED [ 10%]
tests/test_01_health_and_auth.py::test_03_incorrect_passwords PASSED     [ 15%]
tests/test_01_health_and_auth.py::test_04_missing_or_invalid_tokens PASSED [ 20%]
tests/test_01_health_and_auth.py::test_05_role_based_access_restrictions PASSED [ 25%]
tests/test_02_registration_workflow.py::test_06_duplicate_course_registration PASSED [ 30%]
tests/test_02_registration_workflow.py::test_07_registration_for_full_course PASSED [ 35%]
tests/test_02_registration_workflow.py::test_08_credit_limit_enforcement PASSED [ 40%]
tests/test_02_registration_workflow.py::test_09_registration_approval_requires_successful_payment PASSED [ 45%]
tests/test_02_registration_workflow.py::test_10_successful_payment_followed_by_registration_approval PASSED [ 50%]
tests/test_02_registration_workflow.py::test_11_student_cannot_drop_another_students_registration PASSED [ 55%]
tests/test_03_attendance_and_conflicts.py::test_12_attendance_for_non_registered_student PASSED [ 60%]
tests/test_03_attendance_and_conflicts.py::test_13_faculty_managing_unassigned_course_attendance PASSED [ 65%]
tests/test_03_attendance_and_conflicts.py::test_14_classroom_timetable_clash PASSED [ 70%]
tests/test_03_attendance_and_conflicts.py::test_15_faculty_timetable_clash PASSED [ 75%]
tests/test_03_attendance_and_conflicts.py::test_16_student_timetable_clash PASSED [ 80%]
tests/test_04_system_integrity_and_reports.py::test_17_invalid_foreign_keys_and_malformed_input PASSED [ 85%]
tests/test_04_system_integrity_and_reports.py::test_18_aggregate_reports_and_sql_views PASSED [ 90%]
tests/test_04_system_integrity_and_reports.py::test_19_transaction_rollback_on_failed_registration PASSED [ 95%]
tests/test_04_system_integrity_and_reports.py::test_20_concurrent_registration_capacity_safety PASSED [100%]

============================= 20 passed in 2.40s ==============================
```

---

## 9. Demonstrating SQL Queries (22 Review Queries)

To execute the 22 demonstration queries demonstrating joins, subqueries, group by, having, exists, date/string functions, and window functions:
```bash
mysql -u root -p crms_db < sql/07_demo_queries.sql
```
Detailed explanations and breakdown of these queries can be found in [`docs/DBMS_QUERIES.md`](docs/DBMS_QUERIES.md).

---

## 10. Core Database Entities & Structure

```text
crms-backend/
├── app/
│   ├── __init__.py               # Flask application factory
│   ├── config.py                 # Environment configurations (Base, Dev, Test)
│   ├── extensions.py             # JWT, CORS, Flasgger extensions
│   ├── database/
│   │   └── connection.py         # MySQL connection pool & context managers
│   ├── schemas/
│   │   └── validators.py         # Marshmallow request schemas
│   ├── services/                 # Business logic and SQL execution
│   │   ├── auth_service.py
│   │   ├── academic_service.py
│   │   ├── registration_service.py
│   │   ├── payment_service.py
│   │   ├── attendance_service.py
│   │   └── report_service.py
│   ├── routes/                   # REST API Blueprints (/api/v1/*)
│   ├── middleware/
│   │   └── auth.py               # RBAC decorators & token revocation
│   ├── errors/
│   │   └── handlers.py           # Centralized exception & MySQL error handler
│   └── utils/
│       └── response.py           # Standardized JSON response envelope
├── sql/
│   ├── 00_create_database.sql
│   ├── 01_schema.sql
│   ├── 02_constraints_indexes.sql
│   ├── 03_views.sql
│   ├── 04_procedures.sql
│   ├── 05_triggers.sql
│   ├── 06_seed_data.sql
│   └── 07_demo_queries.sql
├── tests/                        # 20 pytest integration tests
├── docs/
│   ├── API_REFERENCE.md          # Full REST endpoints specification
│   ├── DATABASE_DESIGN.md        # Relational design, keys & normalization
│   ├── REVIEW2_DEMO.md           # Step-by-step Review 2 live demonstration guide
│   ├── TEST_REPORT.md            # Verified test execution results
│   ├── DBMS_QUERIES.md           # Review SQL queries documentation
│   └── CRMS_Postman_Collection.json # Importable Postman collection
├── requirements.txt
├── run.py
└── README.md
```

---

## 11. Implemented Business Rules Summary

1. **Duplicate Registration Prevention**: Unique candidate key constraint `(student_id, course_id)` and procedure checking prevent duplicate enrollment.
2. **Real-time Capacity Enforcement**: Course capacity is checked with pessimistic locking (`FOR UPDATE`); registrations are blocked once `approved_enrollments >= maximum_seats`.
3. **Credit Ceiling Enforcement**: A student cannot exceed 24 registered credits in a single semester.
4. **Two-Stage Payment & Approval Safety**: Course registrations start in `Pending` state. Administrative approval requires a `Successful` payment.
5. **Classroom Clash Prevention**: MySQL trigger `trg_prevent_classroom_overlap_insert` checks interval overlap (`start_time < end_time AND end_time > start_time`) to prevent double-booking.
6. **Faculty Double-Booking Prevention**: Trigger prevents assigning a faculty member to concurrent lectures.
7. **Student Timetable Conflict Check**: Registration validates that lecture times do not clash with student's enrolled courses.
8. **Classroom Capacity Validation**: Classroom capacity must be greater than or equal to planned course maximum seats.
9. **Attendance Enrolment Rule**: Trigger `trg_check_attendance_registration` blocks attendance records for non-enrolled students.
10. **Faculty Access Control**: Faculty members can manage attendance and courses only for sections assigned to them.

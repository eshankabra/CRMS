# CRMS Comprehensive Test Execution Report

**Project**: Course Registration and Management System (CRMS)  
**Evaluation**: DBMS Project Review 2 — VIT Vellore  
**Test Suite**: `pytest 9.1.1` with `crms_test_db` on MySQL 8.0 Community Server  
**Execution Date**: 2026-10-10  
**Overall Status**: **20 PASSED / 0 FAILED (100% Pass Rate)**  

---

## 1. Test Environment Specification

- **Operating System**: Windows 11
- **Language**: Python 3.14.6
- **Web Framework**: Flask 3.1.3
- **Database Engine**: MySQL Server 8.0 (InnoDB engine, UTF-8 unicode collation)
- **Database Connector**: `mysql-connector-python 26.7.0`
- **Authentication**: `Flask-JWT-Extended 4.7.4` with Werkzeug scrypt hashing
- **Test Framework**: `pytest 9.1.1`

---

## 2. Test Execution Summary

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

## 3. Detailed Results by Business Rule

| # | Test Name | Business Rule Verified | Result |
|---|:---|:---|:---:|
| 1 | `test_01_health_endpoint` | Backend health check and MySQL ping connectivity | **PASSED** |
| 2 | `test_02_student_registration_and_login` | Student self-registration and credential verification | **PASSED** |
| 3 | `test_03_incorrect_passwords` | Rejected authentication on invalid credentials | **PASSED** |
| 4 | `test_04_missing_or_invalid_tokens` | HTTP 401 when token is missing, invalid, or malformed | **PASSED** |
| 5 | `test_05_role_based_access_restrictions` | HTTP 403 when Student attempts Admin operations | **PASSED** |
| 6 | `test_06_duplicate_course_registration` | Student cannot register for the same course twice | **PASSED** |
| 7 | `test_07_registration_for_full_course` | Registration rejected when course maximum seats reached | **PASSED** |
| 8 | `test_08_credit_limit_enforcement` | Rejection when student exceeds 24 credits per semester | **PASSED** |
| 9 | `test_09_registration_approval_requires_successful_payment` | Registration cannot be Approved before Successful payment | **PASSED** |
| 10 | `test_10_successful_payment_followed_by_registration_approval` | Payment verification enables administrative approval | **PASSED** |
| 11 | `test_11_student_cannot_drop_another_students_registration` | Student ownership check on registration drop requests | **PASSED** |
| 12 | `test_12_attendance_for_non_registered_student` | Attendance blocked if student not enrolled in course | **PASSED** |
| 13 | `test_13_faculty_managing_unassigned_course_attendance` | Faculty restricted to assigned courses for attendance | **PASSED** |
| 14 | `test_14_classroom_timetable_clash` | Trigger rejects overlapping bookings in same room/day | **PASSED** |
| 15 | `test_15_faculty_timetable_clash` | Trigger rejects overlapping schedules for same faculty | **PASSED** |
| 16 | `test_16_student_timetable_clash` | Service prevents student registering for overlapping slots | **PASSED** |
| 17 | `test_17_invalid_foreign_keys_and_malformed_input` | Schema constraints block invalid inputs and FKs | **PASSED** |
| 18 | `test_18_aggregate_reports_and_sql_views` | Views and stored procedures generate correct rollups | **PASSED** |
| 19 | `test_19_transaction_rollback_on_failed_registration` | Atomic transaction rollback prevents orphaned records | **PASSED** |
| 20 | `test_20_concurrent_registration_capacity_safety` | Multi-threaded simultaneous requests respect capacity | **PASSED** |

---

## 4. Concurrency & Concurrency Safety Verification

Test 20 executed 5 simultaneous registration threads competing for a single seat in course `RACE_...`. Through MySQL InnoDB pessimistic row locking (`FOR UPDATE`) within stored procedure `sp_register_student_course`, race conditions were strictly eliminated and zero seat over-allocation occurred.

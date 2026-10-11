-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 03_views.sql
-- Description: Standard SQL Views for Reports, Dashboards & Audits
-- =====================================================================

USE crms_db;

-- 1. View: registration_details
-- Combines registrations, students, courses, departments, faculty, and status
DROP VIEW IF EXISTS registration_details;
CREATE VIEW registration_details AS
SELECT 
    r.registration_id,
    r.registration_date,
    r.registration_status,
    s.student_id,
    s.roll_no AS student_roll_no,
    s.name AS student_name,
    s.email AS student_email,
    s.semester_id,
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    c.course_type,
    c.maximum_seats,
    d.department_id,
    d.department_name,
    f.faculty_id,
    f.name AS faculty_name,
    f.email AS faculty_email
FROM registration r
JOIN student s ON r.student_id = s.student_id
JOIN course c ON r.course_id = c.course_id
JOIN department d ON c.department_id = d.department_id
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id;

-- 2. View: course_seat_availability
-- Shows course capacity, confirmed (Approved) enrollments, pending enrollments, and remaining seats
DROP VIEW IF EXISTS course_seat_availability;
CREATE VIEW course_seat_availability AS
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    c.course_type,
    c.maximum_seats,
    d.department_name,
    f.name AS faculty_name,
    COALESCE(SUM(CASE WHEN r.registration_status = 'Approved' THEN 1 ELSE 0 END), 0) AS approved_enrollments,
    COALESCE(SUM(CASE WHEN r.registration_status = 'Pending' THEN 1 ELSE 0 END), 0) AS pending_registrations,
    (c.maximum_seats - COALESCE(SUM(CASE WHEN r.registration_status = 'Approved' THEN 1 ELSE 0 END), 0)) AS remaining_seats,
    CASE 
        WHEN (c.maximum_seats - COALESCE(SUM(CASE WHEN r.registration_status = 'Approved' THEN 1 ELSE 0 END), 0)) <= 0 THEN 'Full'
        ELSE 'Available'
    END AS seat_status
FROM course c
JOIN department d ON c.department_id = d.department_id
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
LEFT JOIN registration r ON c.course_id = r.course_id
GROUP BY 
    c.course_id, c.course_code, c.course_name, c.credits, 
    c.course_type, c.maximum_seats, d.department_name, f.name;

-- 3. View: student_attendance_summary
-- Summarizes total lectures, presents, absents, and percentage per student per course
DROP VIEW IF EXISTS student_attendance_summary;
CREATE VIEW student_attendance_summary AS
SELECT 
    s.student_id,
    s.roll_no,
    s.name AS student_name,
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(a.attendance_id) AS total_classes,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended_classes,
    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS missed_classes,
    ROUND(
        CASE 
            WHEN COUNT(a.attendance_id) > 0 
            THEN (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0) / COUNT(a.attendance_id)
            ELSE 0.00 
        END, 2
    ) AS attendance_percentage
FROM student s
JOIN registration r ON s.student_id = r.student_id AND r.registration_status = 'Approved'
JOIN course c ON r.course_id = c.course_id
LEFT JOIN attendance a ON s.student_id = a.student_id AND c.course_id = a.course_id
GROUP BY s.student_id, s.roll_no, s.name, c.course_id, c.course_code, c.course_name;

-- 4. View: payment_summary
-- Summarizes student payments accurately without duplicate row multiplications
DROP VIEW IF EXISTS payment_summary;
CREATE VIEW payment_summary AS
SELECT 
    s.student_id,
    s.roll_no,
    s.name AS student_name,
    s.email AS student_email,
    d.department_name,
    COUNT(p.payment_id) AS total_transactions,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Successful' THEN p.amount ELSE 0.00 END), 0.00) AS total_paid,
    COALESCE(SUM(CASE WHEN p.payment_status = 'Pending' THEN p.amount ELSE 0.00 END), 0.00) AS total_pending,
    MAX(p.payment_date) AS last_payment_date
FROM student s
JOIN department d ON s.department_id = d.department_id
LEFT JOIN payment p ON s.student_id = p.student_id
GROUP BY s.student_id, s.roll_no, s.name, s.email, d.department_name;

-- 5. View: student_timetable_view
-- Full schedule details for enrolled courses
DROP VIEW IF EXISTS student_timetable_view;
CREATE VIEW student_timetable_view AS
SELECT 
    r.student_id,
    r.registration_status,
    cs.schedule_id,
    cs.semester_id,
    sem.semester_name,
    sem.academic_year,
    c.course_id,
    c.course_code,
    c.course_name,
    f.name AS faculty_name,
    cr.room_id,
    cr.room_number,
    cr.building,
    cs.day,
    cs.start_time,
    cs.end_time
FROM registration r
JOIN course c ON r.course_id = c.course_id
JOIN course_schedule cs ON c.course_id = cs.course_id
JOIN semester sem ON cs.semester_id = sem.semester_id
JOIN classroom cr ON cs.room_id = cr.room_id
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id;

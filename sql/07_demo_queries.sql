-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 07_demo_queries.sql
-- Description: Comprehensive SQL Demonstration Pack (22 Queries)
-- Covering: Joins, Aggregates, Grouping, Having, Subqueries, 
-- Correlated Subqueries, EXISTS/NOT EXISTS, Window Functions, Date/String Ops
-- =====================================================================

USE crms_db;

-- ---------------------------------------------------------------------
-- QUERY 1: Basic SELECT, Filtering, Sorting & Pattern Matching
-- Finds all students in CSE department whose name starts with 'A', sorted by name
-- ---------------------------------------------------------------------
SELECT 
    student_id, 
    roll_no, 
    name, 
    email, 
    gender
FROM student
WHERE department_id = 1 AND name LIKE 'A%'
ORDER BY name ASC;

-- ---------------------------------------------------------------------
-- QUERY 2: Inner Join Across Two Tables
-- Retrieves all courses along with their offering department name
-- ---------------------------------------------------------------------
SELECT 
    c.course_code, 
    c.course_name, 
    c.credits, 
    c.course_type, 
    d.department_name
FROM course c
INNER JOIN department d ON c.department_id = d.department_id
ORDER BY d.department_name, c.course_code;

-- ---------------------------------------------------------------------
-- QUERY 3: Multi-Table Join (4 Tables)
-- Combines Student, Course, Registration, and Department
-- ---------------------------------------------------------------------
SELECT 
    s.roll_no,
    s.name AS student_name,
    c.course_code,
    c.course_name,
    d.department_name,
    r.registration_status,
    r.registration_date
FROM registration r
JOIN student s ON r.student_id = s.student_id
JOIN course c ON r.course_id = c.course_id
JOIN department d ON c.department_id = d.department_id
WHERE r.registration_status = 'Approved'
ORDER BY s.roll_no;

-- ---------------------------------------------------------------------
-- QUERY 4: Left Outer Join for Unassigned Faculty
-- Identifies courses and shows faculty name, including courses where faculty is NULL
-- ---------------------------------------------------------------------
SELECT 
    c.course_code, 
    c.course_name, 
    COALESCE(f.name, 'Unassigned') AS faculty_name,
    COALESCE(f.email, 'N/A') AS faculty_email
FROM course c
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id;

-- ---------------------------------------------------------------------
-- QUERY 5: Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)
-- Calculates statistics on course credits offered across the institution
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_courses,
    SUM(credits) AS total_offered_credits,
    ROUND(AVG(credits), 2) AS average_course_credits,
    MIN(credits) AS min_credits,
    MAX(credits) AS max_credits
FROM course;

-- ---------------------------------------------------------------------
-- QUERY 6: GROUP BY with COUNT and HAVING Filter
-- Identifies departments offering more than 2 courses
-- ---------------------------------------------------------------------
SELECT 
    d.department_name, 
    COUNT(c.course_id) AS total_courses_offered
FROM department d
JOIN course c ON d.department_id = c.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(c.course_id) >= 2
ORDER BY total_courses_offered DESC;

-- ---------------------------------------------------------------------
-- QUERY 7: Subquery (Scalar Subquery in WHERE clause)
-- Finds all courses with credits strictly greater than average course credits
-- ---------------------------------------------------------------------
SELECT 
    course_code, 
    course_name, 
    credits
FROM course
WHERE credits > (SELECT AVG(credits) FROM course);

-- ---------------------------------------------------------------------
-- QUERY 8: Multi-Row Subquery (IN operator)
-- Finds students registered for any Core course
-- ---------------------------------------------------------------------
SELECT DISTINCT 
    s.roll_no, 
    s.name, 
    s.email
FROM student s
WHERE s.student_id IN (
    SELECT r.student_id 
    FROM registration r
    JOIN course c ON r.course_id = c.course_id
    WHERE c.course_type = 'Core'
);

-- ---------------------------------------------------------------------
-- QUERY 9: Correlated Subquery
-- Finds students who have registered for more than average courses per student
-- ---------------------------------------------------------------------
SELECT 
    s.student_id, 
    s.roll_no, 
    s.name,
    (SELECT COUNT(*) FROM registration r WHERE r.student_id = s.student_id) AS registration_count
FROM student s
WHERE (SELECT COUNT(*) FROM registration r WHERE r.student_id = s.student_id) > (
    SELECT AVG(reg_count)
    FROM (
        SELECT COUNT(*) AS reg_count 
        FROM registration 
        GROUP BY student_id
    ) AS student_reg_stats
);

-- ---------------------------------------------------------------------
-- QUERY 10: NOT EXISTS Query — Students with NO Registrations
-- Finds students who have never registered for any course
-- ---------------------------------------------------------------------
SELECT 
    s.student_id, 
    s.roll_no, 
    s.name, 
    s.email
FROM student s
WHERE NOT EXISTS (
    SELECT 1 
    FROM registration r 
    WHERE r.student_id = s.student_id
);

-- ---------------------------------------------------------------------
-- QUERY 11: NOT EXISTS Query — Courses with NO Enrollments
-- Finds offered courses with zero student registrations
-- ---------------------------------------------------------------------
SELECT 
    c.course_id, 
    c.course_code, 
    c.course_name
FROM course c
WHERE NOT EXISTS (
    SELECT 1 
    FROM registration r 
    WHERE r.course_id = c.course_id
);

-- ---------------------------------------------------------------------
-- QUERY 12: Courses that Have Reached Maximum Capacity
-- Identifies courses where approved enrollments equal or exceed maximum seats
-- ---------------------------------------------------------------------
SELECT 
    c.course_code,
    c.course_name,
    c.maximum_seats,
    COUNT(r.registration_id) AS enrolled_students,
    'FULL' AS seat_status
FROM course c
JOIN registration r ON c.course_id = r.course_id AND r.registration_status = 'Approved'
GROUP BY c.course_id, c.course_code, c.course_name, c.maximum_seats
HAVING COUNT(r.registration_id) >= c.maximum_seats;

-- ---------------------------------------------------------------------
-- QUERY 13: Department-Wise Total Approved Enrollments
-- Aggregates total confirmed registrations across departments
-- ---------------------------------------------------------------------
SELECT 
    d.department_name,
    COUNT(DISTINCT s.student_id) AS total_enrolled_students,
    COUNT(r.registration_id) AS total_course_registrations
FROM department d
JOIN student s ON d.department_id = s.department_id
LEFT JOIN registration r ON s.student_id = r.student_id AND r.registration_status = 'Approved'
GROUP BY d.department_id, d.department_name
ORDER BY total_course_registrations DESC;

-- ---------------------------------------------------------------------
-- QUERY 14: Faculty-Wise Teaching Assignment and Credit Load
-- Reports courses taught and total teaching credits for each faculty member
-- ---------------------------------------------------------------------
SELECT 
    f.faculty_id,
    f.name AS faculty_name,
    f.qualification,
    d.department_name,
    COUNT(c.course_id) AS courses_assigned,
    COALESCE(SUM(c.credits), 0) AS total_teaching_credits
FROM faculty f
JOIN department d ON f.department_id = d.department_id
LEFT JOIN course c ON f.faculty_id = c.faculty_id
GROUP BY f.faculty_id, f.name, f.qualification, d.department_name
ORDER BY total_teaching_credits DESC;

-- ---------------------------------------------------------------------
-- QUERY 15: Successful vs. Pending Payment Totals
-- Summarizes financial transactions grouped by status and payment mode
-- ---------------------------------------------------------------------
SELECT 
    payment_mode,
    payment_status,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount
FROM payment
GROUP BY payment_mode, payment_status
ORDER BY payment_mode, payment_status;

-- ---------------------------------------------------------------------
-- QUERY 16: Student-Wise Attendance Percentage (Conditional Aggregation)
-- Computes lecture attendance rate for every student in their approved courses
-- ---------------------------------------------------------------------
SELECT 
    s.roll_no,
    s.name AS student_name,
    c.course_code,
    c.course_name,
    COUNT(a.attendance_id) AS total_classes_held,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS classes_attended,
    ROUND((SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0) / COUNT(a.attendance_id), 2) AS attendance_percentage
FROM student s
JOIN registration r ON s.student_id = r.student_id AND r.registration_status = 'Approved'
JOIN course c ON r.course_id = c.course_id
JOIN attendance a ON s.student_id = a.student_id AND c.course_id = a.course_id
GROUP BY s.student_id, s.roll_no, s.name, c.course_id, c.course_code, c.course_name
ORDER BY attendance_percentage DESC;

-- ---------------------------------------------------------------------
-- QUERY 17: Date Functions
-- Calculates student age in years and days since registration
-- ---------------------------------------------------------------------
SELECT 
    s.roll_no,
    s.name,
    s.date_of_birth,
    TIMESTAMPDIFF(YEAR, s.date_of_birth, CURDATE()) AS age_in_years,
    r.registration_date,
    DATEDIFF(CURDATE(), r.registration_date) AS days_since_registration
FROM student s
JOIN registration r ON s.student_id = r.student_id
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 18: String Functions
-- Formats student profiles with upper casing, email domain extraction & name initials
-- ---------------------------------------------------------------------
SELECT 
    roll_no,
    UPPER(name) AS formatted_name,
    CONCAT('+91-', COALESCE(phone, 'N/A')) AS formatted_phone,
    SUBSTRING_INDEX(email, '@', -1) AS email_domain,
    LENGTH(name) AS name_character_length
FROM student
LIMIT 10;

-- ---------------------------------------------------------------------
-- QUERY 19: Set Operation (UNION)
-- Combines contacts of administrators and faculty for unified directory
-- ---------------------------------------------------------------------
SELECT 
    'Administrator' AS role_type,
    name,
    email
FROM admin
UNION ALL
SELECT 
    'Faculty' AS role_type,
    name,
    email
FROM faculty
ORDER BY role_type, name;

-- ---------------------------------------------------------------------
-- QUERY 20: Comprehensive Timetable Query
-- Shows room, course, faculty, day, and time slots
-- ---------------------------------------------------------------------
SELECT 
    cs.day,
    cs.start_time,
    cs.end_time,
    c.course_code,
    c.course_name,
    f.name AS instructor,
    cr.room_number,
    cr.building
FROM course_schedule cs
JOIN course c ON cs.course_id = c.course_id
JOIN classroom cr ON cs.room_id = cr.room_id
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
ORDER BY 
    FIELD(cs.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'),
    cs.start_time;

-- ---------------------------------------------------------------------
-- QUERY 21: Students Nearing Maximum Credit Limit (Credit Load Audit)
-- Identifies students with total registered credits >= 10
-- ---------------------------------------------------------------------
SELECT 
    s.roll_no,
    s.name,
    d.department_name,
    SUM(c.credits) AS total_enrolled_credits
FROM student s
JOIN department d ON s.department_id = d.department_id
JOIN registration r ON s.student_id = r.student_id
JOIN course c ON r.course_id = c.course_id
GROUP BY s.student_id, s.roll_no, s.name, d.department_name
HAVING SUM(c.credits) >= 10
ORDER BY total_enrolled_credits DESC;

-- ---------------------------------------------------------------------
-- QUERY 22: Window Function (DENSE_RANK)
-- Ranks courses by approved enrollment within each department
-- ---------------------------------------------------------------------
SELECT 
    d.department_name,
    c.course_code,
    c.course_name,
    COUNT(r.registration_id) AS approved_enrollment,
    DENSE_RANK() OVER (
        PARTITION BY d.department_id 
        ORDER BY COUNT(r.registration_id) DESC
    ) AS departmental_course_rank
FROM course c
JOIN department d ON c.department_id = d.department_id
LEFT JOIN registration r ON c.course_id = r.course_id AND r.registration_status = 'Approved'
GROUP BY d.department_id, d.department_name, c.course_id, c.course_code, c.course_name
ORDER BY d.department_name, departmental_course_rank;

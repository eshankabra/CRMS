-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 04_procedures.sql
-- Description: Stored Procedures & Functions for Concurrency-Safe Operations
-- =====================================================================

USE crms_db;

DELIMITER $$

-- ---------------------------------------------------------------------
-- FUNCTION: fn_course_available_seats
-- Calculates and returns remaining seats for a given course
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_course_available_seats$$
CREATE FUNCTION fn_course_available_seats(p_course_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_max_seats INT DEFAULT 0;
    DECLARE v_enrolled INT DEFAULT 0;

    SELECT maximum_seats INTO v_max_seats
    FROM course
    WHERE course_id = p_course_id;

    IF v_max_seats IS NULL THEN
        RETURN 0;
    END IF;

    SELECT COUNT(*) INTO v_enrolled
    FROM registration
    WHERE course_id = p_course_id AND registration_status = 'Approved';

    RETURN GREATEST(0, v_max_seats - v_enrolled);
END$$

-- ---------------------------------------------------------------------
-- FUNCTION: fn_student_attendance_percentage
-- Returns attendance percentage for a student in a course
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_student_attendance_percentage$$
CREATE FUNCTION fn_student_attendance_percentage(p_student_id INT, p_course_id INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total INT DEFAULT 0;
    DECLARE v_present INT DEFAULT 0;

    SELECT COUNT(*), COALESCE(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END), 0)
    INTO v_total, v_present
    FROM attendance
    WHERE student_id = p_student_id AND course_id = p_course_id;

    IF v_total = 0 THEN
        RETURN 0.00;
    END IF;

    RETURN ROUND((v_present * 100.0) / v_total, 2);
END$$

-- ---------------------------------------------------------------------
-- PROCEDURE: sp_register_student_course
-- Concurrency-safe student course registration with validation
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_register_student_course$$
CREATE PROCEDURE sp_register_student_course(
    IN p_student_id INT,
    IN p_course_id INT,
    IN p_max_credit_limit INT,
    OUT p_registration_id INT,
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_exists_student INT DEFAULT 0;
    DECLARE v_exists_course INT DEFAULT 0;
    DECLARE v_already_reg INT DEFAULT 0;
    DECLARE v_course_credits INT DEFAULT 0;
    DECLARE v_current_credits INT DEFAULT 0;
    DECLARE v_max_seats INT DEFAULT 0;
    DECLARE v_approved_seats INT DEFAULT 0;
    DECLARE v_student_sem_id INT DEFAULT 0;

    -- Error handler for unexpected SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_registration_id = NULL;
        SET p_status = 'ERROR';
        SET p_message = 'An unexpected database error occurred during registration.';
    END;

    START TRANSACTION;

    -- 1. Check student existence and get semester
    SELECT COUNT(*), COALESCE(MAX(semester_id), 0)
    INTO v_exists_student, v_student_sem_id
    FROM student
    WHERE student_id = p_student_id;

    IF v_exists_student = 0 THEN
        ROLLBACK;
        SET p_registration_id = NULL;
        SET p_status = 'STUDENT_NOT_FOUND';
        SET p_message = 'Student does not exist.';
        LEAVE proc_label;
    END IF;

    -- 2. Check course existence and lock course row for concurrency safety
    SELECT credits, maximum_seats
    INTO v_course_credits, v_max_seats
    FROM course
    WHERE course_id = p_course_id
    FOR UPDATE;

    IF v_max_seats IS NULL OR v_max_seats = 0 THEN
        ROLLBACK;
        SET p_registration_id = NULL;
        SET p_status = 'COURSE_NOT_FOUND';
        SET p_message = 'Course does not exist.';
        LEAVE proc_label;
    END IF;

    -- 3. Check duplicate registration
    SELECT COUNT(*) INTO v_already_reg
    FROM registration
    WHERE student_id = p_student_id AND course_id = p_course_id;

    IF v_already_reg > 0 THEN
        ROLLBACK;
        SET p_registration_id = NULL;
        SET p_status = 'DUPLICATE_REGISTRATION';
        SET p_message = 'Student is already registered for this course.';
        LEAVE proc_label;
    END IF;

    -- 4. Check available seats
    SELECT COUNT(*) INTO v_approved_seats
    FROM registration
    WHERE course_id = p_course_id AND registration_status = 'Approved';

    IF v_approved_seats >= v_max_seats THEN
        ROLLBACK;
        SET p_registration_id = NULL;
        SET p_status = 'COURSE_FULL';
        SET p_message = 'Course has reached maximum capacity.';
        LEAVE proc_label;
    END IF;

    -- 5. Check credit limit
    SELECT COALESCE(SUM(c.credits), 0) INTO v_current_credits
    FROM registration r
    JOIN course c ON r.course_id = c.course_id
    WHERE r.student_id = p_student_id;

    IF (v_current_credits + v_course_credits) > p_max_credit_limit THEN
        ROLLBACK;
        SET p_registration_id = NULL;
        SET p_status = 'CREDIT_LIMIT_EXCEEDED';
        SET p_message = CONCAT('Registration exceeds maximum credit limit of ', p_max_credit_limit, ' credits.');
        LEAVE proc_label;
    END IF;

    -- 6. Insert new registration in Pending status
    INSERT INTO registration (student_id, course_id, registration_date, registration_status)
    VALUES (p_student_id, p_course_id, CURDATE(), 'Pending');

    SET p_registration_id = LAST_INSERT_ID();
    SET p_status = 'SUCCESS';
    SET p_message = 'Registration initiated successfully in Pending status. Awaiting payment and approval.';

    COMMIT;
END$$

-- ---------------------------------------------------------------------
-- PROCEDURE: sp_approve_registration
-- Approves a pending registration after validating payment and capacity
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_approve_registration$$
CREATE PROCEDURE sp_approve_registration(
    IN p_registration_id INT,
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_reg_status VARCHAR(10);
    DECLARE v_course_id INT;
    DECLARE v_student_id INT;
    DECLARE v_max_seats INT;
    DECLARE v_approved_seats INT;
    DECLARE v_successful_payment INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'Database error occurred during registration approval.';
    END;

    START TRANSACTION;

    -- Lock registration row
    SELECT registration_status, course_id, student_id
    INTO v_reg_status, v_course_id, v_student_id
    FROM registration
    WHERE registration_id = p_registration_id
    FOR UPDATE;

    IF v_reg_status IS NULL THEN
        ROLLBACK;
        SET p_status = 'NOT_FOUND';
        SET p_message = 'Registration not found.';
        LEAVE proc_label;
    END IF;

    IF v_reg_status = 'Approved' THEN
        ROLLBACK;
        SET p_status = 'ALREADY_APPROVED';
        SET p_message = 'Registration is already approved.';
        LEAVE proc_label;
    END IF;

    -- Check if student has a Successful payment (either tied to this registration or general student payment)
    SELECT COUNT(*) INTO v_successful_payment
    FROM payment
    WHERE student_id = v_student_id 
      AND payment_status = 'Successful'
      AND (registration_id = p_registration_id OR registration_id IS NULL);

    IF v_successful_payment = 0 THEN
        ROLLBACK;
        SET p_status = 'PAYMENT_REQUIRED';
        SET p_message = 'A successful payment is required before approving this registration.';
        LEAVE proc_label;
    END IF;

    -- Lock course row and verify remaining seats
    SELECT maximum_seats INTO v_max_seats
    FROM course
    WHERE course_id = v_course_id
    FOR UPDATE;

    SELECT COUNT(*) INTO v_approved_seats
    FROM registration
    WHERE course_id = v_course_id AND registration_status = 'Approved';

    IF v_approved_seats >= v_max_seats THEN
        ROLLBACK;
        SET p_status = 'COURSE_FULL';
        SET p_message = 'Cannot approve: course capacity is full.';
        LEAVE proc_label;
    END IF;

    -- Update registration status
    UPDATE registration
    SET registration_status = 'Approved'
    WHERE registration_id = p_registration_id;

    SET p_status = 'SUCCESS';
    SET p_message = 'Registration approved successfully.';

    COMMIT;
END$$

-- ---------------------------------------------------------------------
-- PROCEDURE: sp_drop_registration
-- Concurrency-safe drop of registration with ownership validation
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_drop_registration$$
CREATE PROCEDURE sp_drop_registration(
    IN p_registration_id INT,
    IN p_requesting_student_id INT, -- NULL if requested by Admin
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_actual_student_id INT;
    DECLARE v_course_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'Database error occurred during registration drop.';
    END;

    START TRANSACTION;

    SELECT student_id, course_id
    INTO v_actual_student_id, v_course_id
    FROM registration
    WHERE registration_id = p_registration_id
    FOR UPDATE;

    IF v_actual_student_id IS NULL THEN
        ROLLBACK;
        SET p_status = 'NOT_FOUND';
        SET p_message = 'Registration record not found.';
        LEAVE proc_label;
    END IF;

    -- Verify ownership if initiated by a student
    IF p_requesting_student_id IS NOT NULL AND p_requesting_student_id <> v_actual_student_id THEN
        ROLLBACK;
        SET p_status = 'FORBIDDEN';
        SET p_message = 'Students cannot drop another student\'s registration.';
        LEAVE proc_label;
    END IF;

    -- Unlink or clear attendance/payment references before dropping
    UPDATE payment SET registration_id = NULL WHERE registration_id = p_registration_id;
    DELETE FROM attendance WHERE student_id = v_actual_student_id AND course_id = v_course_id;
    DELETE FROM registration WHERE registration_id = p_registration_id;

    SET p_status = 'SUCCESS';
    SET p_message = 'Registration dropped successfully.';

    COMMIT;
END$$

-- ---------------------------------------------------------------------
-- PROCEDURE: sp_generate_enrollment_report
-- Generates enrollment report by course
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_generate_enrollment_report$$
CREATE PROCEDURE sp_generate_enrollment_report(
    IN p_department_id INT
)
BEGIN
    SELECT 
        c.course_id,
        c.course_code,
        c.course_name,
        c.credits,
        c.course_type,
        c.maximum_seats,
        d.department_name,
        COALESCE(f.name, 'Unassigned') AS faculty_name,
        COALESCE(SUM(CASE WHEN r.registration_status = 'Approved' THEN 1 ELSE 0 END), 0) AS approved_count,
        COALESCE(SUM(CASE WHEN r.registration_status = 'Pending' THEN 1 ELSE 0 END), 0) AS pending_count,
        (c.maximum_seats - COALESCE(SUM(CASE WHEN r.registration_status = 'Approved' THEN 1 ELSE 0 END), 0)) AS available_seats
    FROM course c
    JOIN department d ON c.department_id = d.department_id
    LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
    LEFT JOIN registration r ON c.course_id = r.course_id
    WHERE (p_department_id IS NULL OR c.department_id = p_department_id)
    GROUP BY c.course_id, c.course_code, c.course_name, c.credits, c.course_type, c.maximum_seats, d.department_name, f.name
    ORDER BY d.department_name, c.course_code;
END$$

DELIMITER ;

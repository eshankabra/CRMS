-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 05_triggers.sql
-- Description: Triggers for Database-Level Relational Integrity Rules
-- =====================================================================

USE crms_db;

DELIMITER $$

-- ---------------------------------------------------------------------
-- TRIGGER 1: trg_check_attendance_registration
-- Rule 9: Attendance can be recorded only for students registered for the course (Approved)
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_check_attendance_registration$$
CREATE TRIGGER trg_check_attendance_registration
BEFORE INSERT ON attendance
FOR EACH ROW
BEGIN
    DECLARE v_is_registered INT DEFAULT 0;

    SELECT COUNT(*) INTO v_is_registered
    FROM registration
    WHERE student_id = NEW.student_id 
      AND course_id = NEW.course_id 
      AND registration_status = 'Approved';

    IF v_is_registered = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Attendance can only be recorded for students with an Approved course registration.';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- TRIGGER 2: trg_prevent_classroom_overlap_insert
-- Rule 12: Prevent overlapping classroom bookings in the same semester and day
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_classroom_overlap_insert$$
CREATE TRIGGER trg_prevent_classroom_overlap_insert
BEFORE INSERT ON course_schedule
FOR EACH ROW
BEGIN
    DECLARE v_clash_count INT DEFAULT 0;
    DECLARE v_faculty_clash_count INT DEFAULT 0;
    DECLARE v_faculty_id INT DEFAULT NULL;
    DECLARE v_room_capacity INT DEFAULT 0;
    DECLARE v_course_max_seats INT DEFAULT 0;

    -- A. Validate classroom capacity >= course maximum seats (Rule 11)
    SELECT capacity INTO v_room_capacity FROM classroom WHERE room_id = NEW.room_id;
    SELECT maximum_seats, faculty_id INTO v_course_max_seats, v_faculty_id FROM course WHERE course_id = NEW.course_id;

    IF v_room_capacity < v_course_max_seats THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Classroom capacity cannot be less than course maximum enrollment capacity.';
    END IF;

    -- B. Prevent classroom conflict (same room, semester, day, overlapping time)
    SELECT COUNT(*) INTO v_clash_count
    FROM course_schedule
    WHERE room_id = NEW.room_id
      AND semester_id = NEW.semester_id
      AND day = NEW.day
      AND (NEW.start_time < end_time AND NEW.end_time > start_time);

    IF v_clash_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Classroom conflict: this room is already booked for an overlapping time slot on this day.';
    END IF;

    -- C. Prevent faculty conflict (same faculty, semester, day, overlapping time)
    IF v_faculty_id IS NOT NULL THEN
        SELECT COUNT(*) INTO v_faculty_clash_count
        FROM course_schedule cs
        JOIN course c ON cs.course_id = c.course_id
        WHERE c.faculty_id = v_faculty_id
          AND cs.semester_id = NEW.semester_id
          AND cs.day = NEW.day
          AND (NEW.start_time < cs.end_time AND NEW.end_time > cs.start_time);

        IF v_faculty_clash_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Faculty conflict: the assigned faculty member already has a scheduled class in an overlapping time slot.';
        END IF;
    END IF;
END$$

-- ---------------------------------------------------------------------
-- TRIGGER 3: trg_prevent_classroom_overlap_update
-- Prevents schedule clashes during schedule updates
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_classroom_overlap_update$$
CREATE TRIGGER trg_prevent_classroom_overlap_update
BEFORE UPDATE ON course_schedule
FOR EACH ROW
BEGIN
    DECLARE v_clash_count INT DEFAULT 0;
    DECLARE v_faculty_clash_count INT DEFAULT 0;
    DECLARE v_faculty_id INT DEFAULT NULL;
    DECLARE v_room_capacity INT DEFAULT 0;
    DECLARE v_course_max_seats INT DEFAULT 0;

    -- Validate capacity
    SELECT capacity INTO v_room_capacity FROM classroom WHERE room_id = NEW.room_id;
    SELECT maximum_seats, faculty_id INTO v_course_max_seats, v_faculty_id FROM course WHERE course_id = NEW.course_id;

    IF v_room_capacity < v_course_max_seats THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Classroom capacity cannot be less than course maximum enrollment capacity.';
    END IF;

    -- Classroom conflict check (excluding current row)
    SELECT COUNT(*) INTO v_clash_count
    FROM course_schedule
    WHERE room_id = NEW.room_id
      AND semester_id = NEW.semester_id
      AND day = NEW.day
      AND schedule_id <> NEW.schedule_id
      AND (NEW.start_time < end_time AND NEW.end_time > start_time);

    IF v_clash_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Classroom conflict: this room is already booked for an overlapping time slot on this day.';
    END IF;

    -- Faculty conflict check
    IF v_faculty_id IS NOT NULL THEN
        SELECT COUNT(*) INTO v_faculty_clash_count
        FROM course_schedule cs
        JOIN course c ON cs.course_id = c.course_id
        WHERE c.faculty_id = v_faculty_id
          AND cs.semester_id = NEW.semester_id
          AND cs.day = NEW.day
          AND cs.schedule_id <> NEW.schedule_id
          AND (NEW.start_time < cs.end_time AND NEW.end_time > cs.start_time);

        IF v_faculty_clash_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Faculty conflict: the assigned faculty member already has a scheduled class in an overlapping time slot.';
        END IF;
    END IF;
END$$

DELIMITER ;

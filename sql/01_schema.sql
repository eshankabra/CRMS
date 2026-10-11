-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 01_schema.sql
-- Description: Core 10 entities from Review 1 + admin entity for RBAC
-- Engine: InnoDB with full relational integrity and UTF-8 support
-- =====================================================================

USE crms_db;

-- Disable foreign key checks for clean recreation if needed
SET FOREIGN_KEY_CHECKS = 0;

-- 1. DEPARTMENT
DROP TABLE IF EXISTS department;
CREATE TABLE department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    building VARCHAR(100) NULL,
    hod_name VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. SEMESTER
DROP TABLE IF EXISTS semester;
CREATE TABLE semester (
    semester_id INT AUTO_INCREMENT PRIMARY KEY,
    semester_name VARCHAR(20) NOT NULL,
    academic_year VARCHAR(9) NOT NULL, -- e.g. '2026-27'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_semester_name CHECK (semester_name IN ('Spring', 'Summer', 'Fall')),
    CONSTRAINT chk_semester_dates CHECK (end_date > start_date),
    CONSTRAINT uq_semester_year UNIQUE (semester_name, academic_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. ADMINISTRATOR (For Role-Based Access Control)
DROP TABLE IF EXISTS admin;
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. FACULTY
DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15) NULL,
    qualification VARCHAR(100) NULL,
    department_id INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_faculty_dept FOREIGN KEY (department_id) 
        REFERENCES department(department_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. STUDENT
DROP TABLE IF EXISTS student;
CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15) NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    department_id INT NOT NULL,
    semester_id INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_student_gender CHECK (gender IN ('Male', 'Female', 'Other')),
    CONSTRAINT fk_student_dept FOREIGN KEY (department_id) 
        REFERENCES department(department_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_student_sem FOREIGN KEY (semester_id) 
        REFERENCES semester(semester_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. CLASSROOM
DROP TABLE IF EXISTS classroom;
CREATE TABLE classroom (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL,
    building VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_room_capacity CHECK (capacity > 0),
    CONSTRAINT uq_room_building UNIQUE (room_number, building)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. COURSE
DROP TABLE IF EXISTS course;
CREATE TABLE course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    course_type VARCHAR(10) NOT NULL,
    maximum_seats INT NOT NULL,
    department_id INT NOT NULL,
    faculty_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_course_credits CHECK (credits BETWEEN 1 AND 6),
    CONSTRAINT chk_course_type CHECK (course_type IN ('Core', 'Elective')),
    CONSTRAINT chk_course_seats CHECK (maximum_seats > 0),
    CONSTRAINT fk_course_dept FOREIGN KEY (department_id) 
        REFERENCES department(department_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_course_faculty FOREIGN KEY (faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. REGISTRATION
DROP TABLE IF EXISTS registration;
CREATE TABLE registration (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    registration_date DATE NOT NULL,
    registration_status VARCHAR(10) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_reg_status CHECK (registration_status IN ('Pending', 'Approved')),
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id),
    CONSTRAINT fk_reg_student FOREIGN KEY (student_id) 
        REFERENCES student(student_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reg_course FOREIGN KEY (course_id) 
        REFERENCES course(course_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. COURSE_SCHEDULE
DROP TABLE IF EXISTS course_schedule;
CREATE TABLE course_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    semester_id INT NOT NULL,
    room_id INT NOT NULL,
    day VARCHAR(15) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_schedule_day CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
    CONSTRAINT chk_schedule_time CHECK (end_time > start_time),
    CONSTRAINT fk_sched_course FOREIGN KEY (course_id) 
        REFERENCES course(course_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_sched_sem FOREIGN KEY (semester_id) 
        REFERENCES semester(semester_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_sched_room FOREIGN KEY (room_id) 
        REFERENCES classroom(room_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. ATTENDANCE
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_attendance_status CHECK (status IN ('Present', 'Absent')),
    CONSTRAINT uq_student_course_date UNIQUE (student_id, course_id, attendance_date),
    CONSTRAINT fk_att_student FOREIGN KEY (student_id) 
        REFERENCES student(student_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_att_course FOREIGN KEY (course_id) 
        REFERENCES course(course_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. PAYMENT
DROP TABLE IF EXISTS payment;
CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    registration_id INT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_mode VARCHAR(10) NOT NULL,
    payment_status VARCHAR(10) NOT NULL DEFAULT 'Pending',
    transaction_reference VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_payment_amount CHECK (amount > 0),
    CONSTRAINT chk_payment_mode CHECK (payment_mode IN ('Online', 'Offline')),
    CONSTRAINT chk_payment_status CHECK (payment_status IN ('Successful', 'Pending')),
    CONSTRAINT fk_pay_student FOREIGN KEY (student_id) 
        REFERENCES student(student_id) 
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pay_reg FOREIGN KEY (registration_id) 
        REFERENCES registration(registration_id) 
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Restore foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

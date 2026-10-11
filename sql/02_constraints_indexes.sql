-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 02_constraints_indexes.sql
-- Description: Indexes for performance optimization and query lookup
-- =====================================================================

USE crms_db;

-- Indexes on Student
CREATE INDEX idx_student_dept ON student(department_id);
CREATE INDEX idx_student_sem ON student(semester_id);
CREATE INDEX idx_student_roll ON student(roll_no);
CREATE INDEX idx_student_name ON student(name);

-- Indexes on Faculty
CREATE INDEX idx_faculty_dept ON faculty(department_id);
CREATE INDEX idx_faculty_name ON faculty(name);

-- Indexes on Course
CREATE INDEX idx_course_dept ON course(department_id);
CREATE INDEX idx_course_faculty ON course(faculty_id);
CREATE INDEX idx_course_type ON course(course_type);

-- Indexes on Registration
CREATE INDEX idx_reg_student ON registration(student_id);
CREATE INDEX idx_reg_course ON registration(course_id);
CREATE INDEX idx_reg_status ON registration(registration_status);
CREATE INDEX idx_reg_date ON registration(registration_date);

-- Indexes on Course Schedule (for timetable and conflict checks)
CREATE INDEX idx_sched_course ON course_schedule(course_id);
CREATE INDEX idx_sched_sem ON course_schedule(semester_id);
CREATE INDEX idx_sched_room ON course_schedule(room_id);
CREATE INDEX idx_sched_room_day_time ON course_schedule(room_id, semester_id, day, start_time, end_time);

-- Indexes on Attendance
CREATE INDEX idx_att_student_course ON attendance(student_id, course_id);
CREATE INDEX idx_att_date ON attendance(attendance_date);
CREATE INDEX idx_att_status ON attendance(status);

-- Indexes on Payment
CREATE INDEX idx_pay_student ON payment(student_id);
CREATE INDEX idx_pay_status ON payment(payment_status);
CREATE INDEX idx_pay_reg ON payment(registration_id);
CREATE INDEX idx_pay_date ON payment(payment_date);

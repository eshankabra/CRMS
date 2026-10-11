-- =====================================================================
-- CRMS: Course Registration and Management System
-- Script: 06_seed_data.sql
-- Description: Realistic, normalized seed dataset for demonstration & testing
-- Default Passwords:
--   Admin:   Admin@123
--   Faculty: Faculty@123
--   Student: Student@123
-- =====================================================================

USE crms_db;

-- Temporarily disable triggers/foreign checks for deterministic seeding
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, @@FOREIGN_KEY_CHECKS = 0;

-- 1. SEED DEPARTMENTS (4 departments)
INSERT INTO department (department_id, department_name, building, hod_name) VALUES
(1, 'Computer Science and Engineering', 'Technology Tower', 'Dr. K. Ramesh'),
(2, 'Information Technology', 'Silver Jubilee Tower', 'Dr. P. Swaminathan'),
(3, 'Electronics and Communication Engineering', 'Main Building', 'Dr. S. Anitha'),
(4, 'Computer Science and Business Systems', 'Technology Tower', 'Dr. M. Priya')
ON DUPLICATE KEY UPDATE 
    department_name=VALUES(department_name), 
    building=VALUES(building), 
    hod_name=VALUES(hod_name);

-- 2. SEED SEMESTERS (3 semesters)
INSERT INTO semester (semester_id, semester_name, academic_year, start_date, end_date, is_active) VALUES
(1, 'Fall', '2026-27', '2026-07-15', '2026-11-30', TRUE),
(2, 'Spring', '2026-27', '2026-12-15', '2027-04-30', FALSE),
(3, 'Summer', '2026-27', '2027-05-10', '2027-06-30', FALSE)
ON DUPLICATE KEY UPDATE 
    start_date=VALUES(start_date), 
    end_date=VALUES(end_date), 
    is_active=VALUES(is_active);

-- 3. SEED ADMINISTRATOR
-- Password: Admin@123
INSERT INTO admin (admin_id, username, name, email, password_hash) VALUES
(1, 'admin', 'System Administrator', 'admin@crms.vit.ac.in', 'scrypt:32768:8:1$qVQEf0bac2OWMjba$a58d4f349fc51d340627dccc46903bf3ae2d880828301f323d0e45cb4ef90602095af2eca0403fadb5b2c0acab861e1fb56200fd75d152c6a909b4bc521868a4')
ON DUPLICATE KEY UPDATE 
    name=VALUES(name), 
    password_hash=VALUES(password_hash);

-- 4. SEED FACULTY (8 faculty members)
-- Password: Faculty@123
INSERT INTO faculty (faculty_id, name, email, phone, qualification, department_id, password_hash) VALUES
(1, 'Dr. Rajesh Sharma', 'rajesh.sharma@vit.ac.in', '9876543210', 'Ph.D. in Computer Science', 1, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(2, 'Dr. Arvind Rao', 'arvind.rao@vit.ac.in', '9876543211', 'Ph.D. in Information Systems', 1, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(3, 'Dr. Meenakshi Sundaram', 'meenakshi.s@vit.ac.in', '9876543212', 'Ph.D. in Data Engineering', 2, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(4, 'Prof. Kavitha Nair', 'kavitha.nair@vit.ac.in', '9876543213', 'M.Tech in Cloud Computing', 2, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(5, 'Dr. Suresh Kumar', 'suresh.kumar@vit.ac.in', '9876543214', 'Ph.D. in VLSI Design', 3, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(6, 'Prof. Deepa Venkat', 'deepa.venkat@vit.ac.in', '9876543215', 'M.Tech in Embedded Systems', 3, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(7, 'Dr. Alok Verma', 'alok.verma@vit.ac.in', '9876543216', 'Ph.D. in Business Analytics', 4, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326'),
(8, 'Prof. Sneha Gupta', 'sneha.gupta@vit.ac.in', '9876543217', 'MBA, M.Tech in Financial Tech', 4, 'scrypt:32768:8:1$EMSjYfv9nixq5S3O$5265f6d5f08d5fdaa326603f745fb9e4907c641c7d81e547790712d78f4e0811d8d49db375f4035a04d14f484da5d9078d8b84671adab2b8168971180cdd2326')
ON DUPLICATE KEY UPDATE 
    name=VALUES(name), 
    password_hash=VALUES(password_hash);

-- 5. SEED STUDENTS (20 students)
-- Password: Student@123
INSERT INTO student (student_id, roll_no, name, email, phone, date_of_birth, gender, department_id, semester_id, password_hash) VALUES
(1, '25BBS0070', 'Eshan Kabra', 'eshan.kabra@vitstudent.ac.in', '9811100001', '2005-04-12', 'Male', 4, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(2, '25BBS0011', 'Roshani Khanijau', 'roshani.k@vitstudent.ac.in', '9811100002', '2005-08-23', 'Female', 4, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(3, '24BCE1001', 'Aarav Patel', 'aarav.patel@vitstudent.ac.in', '9811100003', '2004-01-15', 'Male', 1, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(4, '24BCE1002', 'Ananya Iyer', 'ananya.iyer@vitstudent.ac.in', '9811100004', '2004-05-19', 'Female', 1, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(5, '24BCE1003', 'Rohan Sengupta', 'rohan.s@vitstudent.ac.in', '9811100005', '2004-11-30', 'Male', 1, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(6, '24BIT2001', 'Diya Nambiar', 'diya.n@vitstudent.ac.in', '9811100006', '2004-03-25', 'Female', 2, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(7, '24BIT2002', 'Karthik Raja', 'karthik.r@vitstudent.ac.in', '9811100007', '2004-07-14', 'Male', 2, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(8, '24BIT2003', 'Meera Pillai', 'meera.p@vitstudent.ac.in', '9811100008', '2004-09-09', 'Female', 2, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(9, '24BEC3001', 'Aditya Joshi', 'aditya.j@vitstudent.ac.in', '9811100009', '2004-12-04', 'Male', 3, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(10, '24BEC3002', 'Pooja Hegde', 'pooja.h@vitstudent.ac.in', '9811100010', '2004-06-18', 'Female', 3, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(11, '24BBS4001', 'Vikram Malhotra', 'vikram.m@vitstudent.ac.in', '9811100011', '2004-10-22', 'Male', 4, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(12, '24BBS4002', 'Tanvi Deshmukh', 'tanvi.d@vitstudent.ac.in', '9811100012', '2004-02-17', 'Female', 4, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(13, '23BCE0501', 'Siddharth Roy', 'siddharth.r@vitstudent.ac.in', '9811100013', '2003-05-11', 'Male', 1, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(14, '23BCE0502', 'Neha Kulkarni', 'neha.k@vitstudent.ac.in', '9811100014', '2003-09-03', 'Female', 1, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(15, '23BIT0601', 'Arjun Menon', 'arjun.m@vitstudent.ac.in', '9811100015', '2003-08-16', 'Male', 2, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(16, '23BIT0602', 'Shreya Banerjee', 'shreya.b@vitstudent.ac.in', '9811100016', '2003-12-28', 'Female', 2, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(17, '23BEC0701', 'Manish Reddy', 'manish.r@vitstudent.ac.in', '9811100017', '2003-03-07', 'Male', 3, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(18, '23BEC0702', 'Kavya Sridhar', 'kavya.s@vitstudent.ac.in', '9811100018', '2003-07-21', 'Female', 3, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(19, '25BBS0099', 'Rahul Verma', 'rahul.v@vitstudent.ac.in', '9811100019', '2005-01-30', 'Male', 4, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced'),
(20, '25BBS0100', 'Ishita Ghosh', 'ishita.g@vitstudent.ac.in', '9811100020', '2005-11-14', 'Female', 4, 1, 'scrypt:32768:8:1$LUduncVTXbb92S6H$23abfbc595c51e96e3c7337c2335e78988e495dedda8d96c5beb0bbfee81bfd57eab76663bcb0e4356c328486e5b7a101e6d8204e2bf6a3593c89de94f4e7ced')
ON DUPLICATE KEY UPDATE 
    name=VALUES(name), 
    password_hash=VALUES(password_hash);

-- 6. SEED CLASSROOMS (8 classrooms)
INSERT INTO classroom (room_id, room_number, building, capacity) VALUES
(1, 'TT-101', 'Technology Tower', 60),
(2, 'TT-201', 'Technology Tower', 80),
(3, 'TT-301', 'Technology Tower', 50),
(4, 'SJT-101', 'Silver Jubilee Tower', 70),
(5, 'SJT-201', 'Silver Jubilee Tower', 65),
(6, 'SJT-301', 'Silver Jubilee Tower', 90),
(7, 'MB-101', 'Main Building', 45),
(8, 'MB-201', 'Main Building', 60)
ON DUPLICATE KEY UPDATE 
    capacity=VALUES(capacity);

-- 7. SEED COURSES (12 courses, course 12 has capacity=2 for edge-case demonstrations)
INSERT INTO course (course_id, course_code, course_name, credits, course_type, maximum_seats, department_id, faculty_id) VALUES
(1, 'CSE1001', 'Problem Solving and Programming', 3, 'Core', 60, 1, 1),
(2, 'CSE2001', 'Data Structures and Algorithms', 4, 'Core', 60, 1, 1),
(3, 'CSE3001', 'Database Management Systems', 4, 'Core', 50, 1, 2),
(4, 'CSE3002', 'Operating Systems', 4, 'Core', 50, 1, 2),
(5, 'ITE2001', 'Web Technologies and Frameworks', 3, 'Core', 45, 2, 3),
(6, 'ITE3002', 'Software Engineering & Agile Methods', 3, 'Core', 50, 2, 4),
(7, 'ECE1001', 'Digital Logic and Systems', 4, 'Core', 45, 3, 5),
(8, 'ECE2002', 'Microprocessors & Interfacing', 4, 'Core', 40, 3, 6),
(9, 'BBS1001', 'Business Organization and Management', 3, 'Core', 50, 4, 7),
(10, 'BBS2002', 'Financial Accounting and Reporting', 3, 'Core', 45, 4, 8),
(11, 'CSE4001', 'Cloud Computing Architecture', 3, 'Elective', 40, 1, 4),
(12, 'BBS3005', 'Special Topics in FinTech', 3, 'Elective', 2, 4, 8) -- Capacity 2 to test Course Full
ON DUPLICATE KEY UPDATE 
    course_name=VALUES(course_name), 
    credits=VALUES(credits), 
    maximum_seats=VALUES(maximum_seats), 
    faculty_id=VALUES(faculty_id);

-- 8. SEED COURSE SCHEDULES
INSERT INTO course_schedule (schedule_id, course_id, semester_id, room_id, day, start_time, end_time) VALUES
(1, 1, 1, 1, 'Monday', '09:00:00', '10:30:00'),
(2, 2, 1, 1, 'Tuesday', '09:00:00', '10:30:00'),
(3, 3, 1, 2, 'Monday', '11:00:00', '12:30:00'),
(4, 4, 1, 2, 'Wednesday', '11:00:00', '12:30:00'),
(5, 5, 1, 4, 'Monday', '14:00:00', '15:30:00'),
(6, 6, 1, 5, 'Thursday', '14:00:00', '15:30:00'),
(7, 7, 1, 7, 'Tuesday', '10:00:00', '11:30:00'),
(8, 8, 1, 8, 'Friday', '10:00:00', '11:30:00'),
(9, 9, 1, 3, 'Wednesday', '09:00:00', '10:30:00'),
(10, 10, 1, 3, 'Friday', '09:00:00', '10:30:00'),
(11, 11, 1, 6, 'Thursday', '09:00:00', '10:30:00'),
(12, 12, 1, 3, 'Saturday', '10:00:00', '11:30:00')
ON DUPLICATE KEY UPDATE 
    day=VALUES(day), 
    start_time=VALUES(start_time), 
    end_time=VALUES(end_time);

-- 9. SEED REGISTRATIONS (Approved and Pending)
INSERT INTO registration (registration_id, student_id, course_id, registration_date, registration_status) VALUES
-- Student 1 (Eshan Kabra): Enrolled in DBMS (3), OS (4), FinTech (12 - fills seat 1 of 2)
(1, 1, 3, '2026-08-01', 'Approved'),
(2, 1, 4, '2026-08-01', 'Approved'),
(3, 1, 12, '2026-08-02', 'Approved'),
-- Student 2 (Roshani): Enrolled in DBMS (3), OS (4), FinTech (12 - fills seat 2 of 2 -> FULL)
(4, 2, 3, '2026-08-01', 'Approved'),
(5, 2, 4, '2026-08-01', 'Approved'),
(6, 2, 12, '2026-08-02', 'Approved'),
-- Student 3: Enrolled in CSE1001, CSE2001
(7, 3, 1, '2026-08-01', 'Approved'),
(8, 3, 2, '2026-08-01', 'Approved'),
-- Student 4: Enrolled in CSE1001, CSE2001
(9, 4, 1, '2026-08-01', 'Approved'),
(10, 4, 2, '2026-08-01', 'Approved'),
-- Student 5: Enrolled in CSE1001
(11, 5, 1, '2026-08-01', 'Approved'),
-- Pending Registrations for Student 6 & Student 7
(12, 6, 5, '2026-08-05', 'Pending'),
(13, 7, 5, '2026-08-05', 'Pending'),
-- Approved Registrations for ECE Students
(14, 9, 7, '2026-08-01', 'Approved'),
(15, 10, 7, '2026-08-01', 'Approved')
ON DUPLICATE KEY UPDATE 
    registration_status=VALUES(registration_status);

-- 10. SEED PAYMENTS (Successful and Pending)
INSERT INTO payment (payment_id, student_id, registration_id, amount, payment_date, payment_mode, payment_status, transaction_reference) VALUES
(1, 1, 1, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-001'),
(2, 1, 2, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-002'),
(3, 1, 3, 4500.00, '2026-08-02', 'Online', 'Successful', 'TXN-VIT-2026-003'),
(4, 2, 4, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-004'),
(5, 2, 5, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-005'),
(6, 2, 6, 4500.00, '2026-08-02', 'Online', 'Successful', 'TXN-VIT-2026-006'),
(7, 3, 7, 4500.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-007'),
(8, 3, 8, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-008'),
(9, 4, 9, 4500.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-009'),
(10, 4, 10, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-010'),
(11, 5, 11, 4500.00, '2026-08-01', 'Offline', 'Successful', 'CHQ-SBI-2026-011'),
-- Pending payment for student 6
(12, 6, 12, 4500.00, '2026-08-05', 'Online', 'Pending', 'TXN-PENDING-001'),
-- Student 7 has not yet initiated payment
(13, 9, 14, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-013'),
(14, 10, 15, 6000.00, '2026-08-01', 'Online', 'Successful', 'TXN-VIT-2026-014')
ON DUPLICATE KEY UPDATE 
    payment_status=VALUES(payment_status), 
    amount=VALUES(amount);

-- 11. SEED ATTENDANCE (Present and Absent across lectures)
INSERT INTO attendance (attendance_id, student_id, course_id, attendance_date, status) VALUES
(1, 1, 3, '2026-08-03', 'Present'),
(2, 1, 3, '2026-08-10', 'Present'),
(3, 1, 3, '2026-08-17', 'Absent'),
(4, 1, 3, '2026-08-24', 'Present'),
(5, 2, 3, '2026-08-03', 'Present'),
(6, 2, 3, '2026-08-10', 'Present'),
(7, 2, 3, '2026-08-17', 'Present'),
(8, 2, 3, '2026-08-24', 'Present'),
(9, 1, 4, '2026-08-05', 'Present'),
(10, 1, 4, '2026-08-12', 'Present'),
(11, 1, 4, '2026-08-19', 'Absent'),
(12, 2, 4, '2026-08-05', 'Present'),
(13, 2, 4, '2026-08-12', 'Absent'),
(14, 3, 1, '2026-08-03', 'Present'),
(15, 3, 1, '2026-08-10', 'Present'),
(16, 4, 1, '2026-08-03', 'Absent'),
(17, 4, 1, '2026-08-10', 'Present')
ON DUPLICATE KEY UPDATE 
    status=VALUES(status);

-- Restore foreign key checks
SET @@FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;

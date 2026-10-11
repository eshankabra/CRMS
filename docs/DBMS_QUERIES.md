# CRMS DBMS Demonstration Queries Reference

**Course Registration and Management System (CRMS)**  
**DBMS Project Review 2 — SQL Demonstration Pack**  
File Reference: `sql/07_demo_queries.sql`  

---

## Query Index & Concepts Demonstrated

| Query # | Purpose / Topic | DBMS Concepts Demonstrated |
| :---: | :--- | :--- |
| **Q1** | Filtered Student Listing | `SELECT`, `WHERE`, `AND`, `LIKE`, `ORDER BY` |
| **Q2** | Departmental Course Offerings | `INNER JOIN`, Table Aliasing, Sorting |
| **Q3** | Detailed Approved Registrations | Multi-Table Join (4 Tables), Relational Integrity |
| **Q4** | Unassigned Faculty Identification | `LEFT OUTER JOIN`, `COALESCE` null handling |
| **Q5** | Credit Statistics Summary | Aggregate Functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`) |
| **Q6** | High-Volume Offering Departments | `GROUP BY`, Aggregate `COUNT`, `HAVING` threshold filter |
| **Q7** | Above-Average Credit Courses | Scalar Subquery in `WHERE` Clause |
| **Q8** | Core Course Enrolled Students | Multi-Row Subquery with `IN` Operator |
| **Q9** | Heavy Course Registrants | Correlated Subquery referencing outer table |
| **Q10** | Students with Zero Registrations | `NOT EXISTS` Subquery |
| **Q11** | Courses with Zero Registrations | `NOT EXISTS` Subquery |
| **Q12** | Courses at 100% Full Capacity | `GROUP BY`, `HAVING COUNT() >= maximum_seats` |
| **Q13** | Department-Wise Enrollment Summary | Aggregations across 3 tables with `DISTINCT` |
| **Q14** | Faculty Teaching & Credit Load | `LEFT JOIN`, `GROUP BY`, `COALESCE` with Aggregates |
| **Q15** | Financial Breakdown by Status/Mode | Multi-column `GROUP BY`, Financial Aggregation |
| **Q16** | Lecture Attendance Percentage | Conditional Aggregation (`SUM(CASE ...)`), Rounding |
| **Q17** | Student Age & Enrollment Age | Date Functions (`TIMESTAMPDIFF`, `CURDATE`, `DATEDIFF`) |
| **Q18** | Student Profile String Formatting | String Functions (`UPPER`, `CONCAT`, `SUBSTRING_INDEX`, `LENGTH`) |
| **Q19** | Combined Academic Directory | Set Operation: `UNION ALL` |
| **Q20** | Master Weekly Timetable | Multi-Table Join, Custom Sorting using `FIELD()` |
| **Q21** | Heavy Credit Auditing | `GROUP BY`, `HAVING SUM(credits) >= threshold` |
| **Q22** | Departmental Enrollment Course Rank | SQL Window Functions (`DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)`) |

---

## Detailed Explanations of Selected Key Queries

### Query 6: GROUP BY with HAVING
```sql
SELECT 
    d.department_name, 
    COUNT(c.course_id) AS total_courses_offered
FROM department d
JOIN course c ON d.department_id = c.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(c.course_id) >= 2
ORDER BY total_courses_offered DESC;
```
*Concept*: Demonstrates grouping rows by department and filtering grouped result sets using `HAVING` (which operates on post-aggregate values, unlike `WHERE`).

### Query 10 & 11: NOT EXISTS Subquery
```sql
SELECT s.student_id, s.roll_no, s.name, s.email
FROM student s
WHERE NOT EXISTS (
    SELECT 1 
    FROM registration r 
    WHERE r.student_id = s.student_id
);
```
*Concept*: Correlated existence test. Returns students for whom the subquery finds zero associated registration rows. Far more efficient than `NOT IN` when handling potential null values.

### Query 16: Conditional Aggregation for Attendance
```sql
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
GROUP BY s.student_id, s.roll_no, s.name, c.course_id, c.course_code, c.course_name;
```
*Concept*: Calculates ratios and percentages within a single query pass without requiring temporary tables or multiple joins.

### Query 22: Window Function (DENSE_RANK)
```sql
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
```
*Concept*: Uses modern MySQL 8.0 window functions (`PARTITION BY`) to rank courses within each departmental partition without collapsing the individual rows.

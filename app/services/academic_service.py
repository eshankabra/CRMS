from werkzeug.security import generate_password_hash
from app.database.connection import get_db_cursor, serialize_row, serialize_rows
import mysql.connector

class AcademicService:

    # ---------------- DEPARTMENTS ----------------
    @staticmethod
    def list_departments():
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM department ORDER BY department_name")
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_department(department_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM department WHERE department_id = %s", (department_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def create_department(data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                INSERT INTO department (department_name, building, hod_name)
                VALUES (%s, %s, %s)
            """, (data["department_name"], data.get("building"), data.get("hod_name")))
            dept_id = cursor.lastrowid
            cursor.execute("SELECT * FROM department WHERE department_id = %s", (dept_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def update_department(department_id, data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                UPDATE department 
                SET department_name = COALESCE(%s, department_name),
                    building = COALESCE(%s, building),
                    hod_name = COALESCE(%s, hod_name)
                WHERE department_id = %s
            """, (data.get("department_name"), data.get("building"), data.get("hod_name"), department_id))
            cursor.execute("SELECT * FROM department WHERE department_id = %s", (department_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def delete_department(department_id):
        with get_db_cursor(commit=True) as (cursor, conn):
            # Check for referencing students, courses, or faculty
            cursor.execute("SELECT COUNT(*) AS c FROM course WHERE department_id = %s", (department_id,))
            if cursor.fetchone()["c"] > 0:
                return False, "Cannot delete department with associated courses."
            cursor.execute("SELECT COUNT(*) AS c FROM faculty WHERE department_id = %s", (department_id,))
            if cursor.fetchone()["c"] > 0:
                return False, "Cannot delete department with associated faculty members."
            cursor.execute("SELECT COUNT(*) AS c FROM student WHERE department_id = %s", (department_id,))
            if cursor.fetchone()["c"] > 0:
                return False, "Cannot delete department with enrolled students."
            
            cursor.execute("DELETE FROM department WHERE department_id = %s", (department_id,))
            return True, None

    # ---------------- SEMESTERS ----------------
    @staticmethod
    def list_semesters(active_only=False):
        with get_db_cursor() as (cursor, conn):
            if active_only:
                cursor.execute("SELECT * FROM semester WHERE is_active = TRUE ORDER BY start_date DESC")
            else:
                cursor.execute("SELECT * FROM semester ORDER BY start_date DESC")
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_semester(semester_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM semester WHERE semester_id = %s", (semester_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def create_semester(data):
        if data["end_date"] <= data["start_date"]:
            raise ValueError("End date must be later than start date.")
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                INSERT INTO semester (semester_name, academic_year, start_date, end_date, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """, (data["semester_name"], data["academic_year"], data["start_date"], data["end_date"], data.get("is_active", False)))
            sem_id = cursor.lastrowid
            cursor.execute("SELECT * FROM semester WHERE semester_id = %s", (sem_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def update_semester(semester_id, data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                UPDATE semester 
                SET semester_name = COALESCE(%s, semester_name),
                    academic_year = COALESCE(%s, academic_year),
                    start_date = COALESCE(%s, start_date),
                    end_date = COALESCE(%s, end_date),
                    is_active = COALESCE(%s, is_active)
                WHERE semester_id = %s
            """, (data.get("semester_name"), data.get("academic_year"), data.get("start_date"), data.get("end_date"), data.get("is_active"), semester_id))
            cursor.execute("SELECT * FROM semester WHERE semester_id = %s", (semester_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def delete_semester(semester_id):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("SELECT COUNT(*) AS c FROM student WHERE semester_id = %s", (semester_id,))
            if cursor.fetchone()["c"] > 0:
                return False, "Cannot delete semester with enrolled students."
            cursor.execute("SELECT COUNT(*) AS c FROM course_schedule WHERE semester_id = %s", (semester_id,))
            if cursor.fetchone()["c"] > 0:
                return False, "Cannot delete semester with scheduled classes."
            cursor.execute("DELETE FROM semester WHERE semester_id = %s", (semester_id,))
            return True, None

    # ---------------- CLASSROOMS ----------------
    @staticmethod
    def list_classrooms(min_capacity=None):
        with get_db_cursor() as (cursor, conn):
            if min_capacity:
                cursor.execute("SELECT * FROM classroom WHERE capacity >= %s ORDER BY building, room_number", (min_capacity,))
            else:
                cursor.execute("SELECT * FROM classroom ORDER BY building, room_number")
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_classroom(room_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM classroom WHERE room_id = %s", (room_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def create_classroom(data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                INSERT INTO classroom (room_number, building, capacity)
                VALUES (%s, %s, %s)
            """, (data["room_number"], data["building"], data["capacity"]))
            room_id = cursor.lastrowid
            cursor.execute("SELECT * FROM classroom WHERE room_id = %s", (room_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def update_classroom(room_id, data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                UPDATE classroom 
                SET room_number = COALESCE(%s, room_number),
                    building = COALESCE(%s, building),
                    capacity = COALESCE(%s, capacity)
                WHERE room_id = %s
            """, (data.get("room_number"), data.get("building"), data.get("capacity"), room_id))
            cursor.execute("SELECT * FROM classroom WHERE room_id = %s", (room_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def delete_classroom(room_id):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("SELECT COUNT(*) AS c FROM course_schedule WHERE room_id = %s", (room_id,))
            if cursor.fetchone()["c"] > 0:
                return False, "Cannot delete classroom assigned to existing course schedules."
            cursor.execute("DELETE FROM classroom WHERE room_id = %s", (room_id,))
            return True, None

    # ---------------- FACULTY ----------------
    @staticmethod
    def list_faculty(department_id=None):
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT f.faculty_id, f.name, f.email, f.phone, f.qualification, f.department_id, d.department_name, f.created_at
                FROM faculty f
                JOIN department d ON f.department_id = d.department_id
            """
            params = []
            if department_id:
                query += " WHERE f.department_id = %s"
                params.append(department_id)
            query += " ORDER BY f.name"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_faculty(faculty_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT f.faculty_id, f.name, f.email, f.phone, f.qualification, f.department_id, d.department_name, f.created_at
                FROM faculty f
                JOIN department d ON f.department_id = d.department_id
                WHERE f.faculty_id = %s
            """, (faculty_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def create_faculty(data):
        password_hash = generate_password_hash(data["password"])
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                INSERT INTO faculty (name, email, phone, qualification, department_id, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data["name"], data["email"], data.get("phone"), data.get("qualification"), data["department_id"], password_hash))
            fac_id = cursor.lastrowid
            cursor.execute("""
                SELECT f.faculty_id, f.name, f.email, f.phone, f.qualification, f.department_id, d.department_name, f.created_at
                FROM faculty f
                JOIN department d ON f.department_id = d.department_id
                WHERE f.faculty_id = %s
            """, (fac_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def get_faculty_courses(faculty_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT c.*, d.department_name,
                       (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved') AS enrolled_students
                FROM course c
                JOIN department d ON c.department_id = d.department_id
                WHERE c.faculty_id = %s
                ORDER BY c.course_code
            """, (faculty_id,))
            return serialize_rows(cursor.fetchall())

    # ---------------- STUDENTS ----------------
    @staticmethod
    def list_students(page=1, per_page=10, search=None, department_id=None, semester_id=None):
        offset = (page - 1) * per_page
        with get_db_cursor() as (cursor, conn):
            where_clauses = ["1=1"]
            params = []
            if search:
                where_clauses.append("(s.name LIKE %s OR s.roll_no LIKE %s OR s.email LIKE %s)")
                term = f"%{search}%"
                params.extend([term, term, term])
            if department_id:
                where_clauses.append("s.department_id = %s")
                params.append(department_id)
            if semester_id:
                where_clauses.append("s.semester_id = %s")
                params.append(semester_id)

            where_str = " AND ".join(where_clauses)
            
            # Count total
            cursor.execute(f"SELECT COUNT(*) AS total FROM student s WHERE {where_str}", tuple(params))
            total = cursor.fetchone()["total"]

            # Fetch page
            query = f"""
                SELECT s.student_id, s.roll_no, s.name, s.email, s.phone, s.date_of_birth, s.gender,
                       s.department_id, d.department_name, s.semester_id, sem.semester_name, sem.academic_year, s.created_at
                FROM student s
                JOIN department d ON s.department_id = d.department_id
                JOIN semester sem ON s.semester_id = sem.semester_id
                WHERE {where_str}
                ORDER BY s.roll_no
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, tuple(params + [per_page, offset]))
            items = serialize_rows(cursor.fetchall())
            return {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }

    @staticmethod
    def get_student(student_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT s.student_id, s.roll_no, s.name, s.email, s.phone, s.date_of_birth, s.gender,
                       s.department_id, d.department_name, s.semester_id, sem.semester_name, sem.academic_year, s.created_at
                FROM student s
                JOIN department d ON s.department_id = d.department_id
                JOIN semester sem ON s.semester_id = sem.semester_id
                WHERE s.student_id = %s
            """, (student_id,))
            return serialize_row(cursor.fetchone())

    # ---------------- COURSES ----------------
    @staticmethod
    def list_courses(department_id=None, faculty_id=None, course_type=None, search=None):
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT c.course_id, c.course_code, c.course_name, c.credits, c.course_type, c.maximum_seats,
                       c.department_id, d.department_name, c.faculty_id, f.name AS faculty_name,
                       (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved') AS approved_enrollments,
                       (c.maximum_seats - (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved')) AS available_seats
                FROM course c
                JOIN department d ON c.department_id = d.department_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE 1=1
            """
            params = []
            if department_id:
                query += " AND c.department_id = %s"
                params.append(department_id)
            if faculty_id:
                query += " AND c.faculty_id = %s"
                params.append(faculty_id)
            if course_type:
                query += " AND c.course_type = %s"
                params.append(course_type)
            if search:
                query += " AND (c.course_code LIKE %s OR c.course_name LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            query += " ORDER BY c.course_code"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_course(course_id):
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT c.course_id, c.course_code, c.course_name, c.credits, c.course_type, c.maximum_seats,
                       c.department_id, d.department_name, c.faculty_id, f.name AS faculty_name,
                       (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved') AS approved_enrollments,
                       (c.maximum_seats - (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved')) AS available_seats
                FROM course c
                JOIN department d ON c.department_id = d.department_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE c.course_id = %s
            """, (course_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def create_course(data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                INSERT INTO course (course_code, course_name, credits, course_type, maximum_seats, department_id, faculty_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data["course_code"], data["course_name"], data["credits"], data["course_type"], data["maximum_seats"], data["department_id"], data.get("faculty_id")))
            course_id = cursor.lastrowid
            cursor.execute("""
                SELECT c.course_id, c.course_code, c.course_name, c.credits, c.course_type, c.maximum_seats,
                       c.department_id, d.department_name, c.faculty_id, f.name AS faculty_name,
                       0 AS approved_enrollments, c.maximum_seats AS available_seats
                FROM course c
                JOIN department d ON c.department_id = d.department_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE c.course_id = %s
            """, (course_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def update_course(course_id, data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                UPDATE course 
                SET course_name = COALESCE(%s, course_name),
                    credits = COALESCE(%s, credits),
                    course_type = COALESCE(%s, course_type),
                    maximum_seats = COALESCE(%s, maximum_seats),
                    faculty_id = %s
                WHERE course_id = %s
            """, (data.get("course_name"), data.get("credits"), data.get("course_type"), data.get("maximum_seats"), data.get("faculty_id"), course_id))
            cursor.execute("""
                SELECT c.course_id, c.course_code, c.course_name, c.credits, c.course_type, c.maximum_seats,
                       c.department_id, d.department_name, c.faculty_id, f.name AS faculty_name,
                       (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved') AS approved_enrollments,
                       (c.maximum_seats - (SELECT COUNT(*) FROM registration r WHERE r.course_id = c.course_id AND r.registration_status = 'Approved')) AS available_seats
                FROM course c
                JOIN department d ON c.department_id = d.department_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE c.course_id = %s
            """, (course_id,))
            return serialize_row(cursor.fetchone())

    # ---------------- SCHEDULES & TIMETABLE ----------------
    @staticmethod
    def list_schedules(semester_id=None, day=None):
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT cs.schedule_id, cs.course_id, c.course_code, c.course_name,
                       cs.semester_id, sem.semester_name, sem.academic_year,
                       cs.room_id, cr.room_number, cr.building, cr.capacity,
                       f.faculty_id, f.name AS faculty_name,
                       cs.day, cs.start_time, cs.end_time
                FROM course_schedule cs
                JOIN course c ON cs.course_id = c.course_id
                JOIN semester sem ON cs.semester_id = sem.semester_id
                JOIN classroom cr ON cs.room_id = cr.room_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE 1=1
            """
            params = []
            if semester_id:
                query += " AND cs.semester_id = %s"
                params.append(semester_id)
            if day:
                query += " AND cs.day = %s"
                params.append(day)
            query += " ORDER BY FIELD(cs.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), cs.start_time"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def create_schedule(data):
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                INSERT INTO course_schedule (course_id, semester_id, room_id, day, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data["course_id"], data["semester_id"], data["room_id"], data["day"], data["start_time"], data["end_time"]))
            sched_id = cursor.lastrowid
            cursor.execute("""
                SELECT cs.*, c.course_code, c.course_name, cr.room_number, cr.building
                FROM course_schedule cs
                JOIN course c ON cs.course_id = c.course_id
                JOIN classroom cr ON cs.room_id = cr.room_id
                WHERE cs.schedule_id = %s
            """, (sched_id,))
            return serialize_row(cursor.fetchone())

    @staticmethod
    def get_student_timetable(student_id):
        """Returns timetable for courses student is enrolled in, checking for time overlaps."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT 
                    cs.schedule_id,
                    c.course_id,
                    c.course_code,
                    c.course_name,
                    c.credits,
                    f.name AS instructor,
                    cr.room_number,
                    cr.building,
                    cs.day,
                    cs.start_time,
                    cs.end_time,
                    r.registration_status
                FROM registration r
                JOIN course c ON r.course_id = c.course_id
                JOIN course_schedule cs ON c.course_id = cs.course_id
                JOIN classroom cr ON cs.room_id = cr.room_id
                LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
                WHERE r.student_id = %s
                ORDER BY FIELD(cs.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), cs.start_time
            """, (student_id,))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def check_student_schedule_conflict(student_id, new_course_id):
        """
        Rule 12: Prevents a student from enrolling in a course with overlapping timetable
        against already registered courses.
        """
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT cs_new.day, cs_new.start_time AS new_start, cs_new.end_time AS new_end,
                       c_exist.course_code AS conflicting_course_code, c_exist.course_name AS conflicting_course_name
                FROM course_schedule cs_new
                JOIN course_schedule cs_exist ON cs_new.day = cs_exist.day 
                    AND cs_new.semester_id = cs_exist.semester_id
                    AND (cs_new.start_time < cs_exist.end_time AND cs_new.end_time > cs_exist.start_time)
                JOIN registration r ON cs_exist.course_id = r.course_id
                JOIN course c_exist ON r.course_id = c_exist.course_id
                WHERE cs_new.course_id = %s AND r.student_id = %s AND cs_exist.course_id <> %s
            """, (new_course_id, student_id, new_course_id))
            conflict = cursor.fetchone()
            if conflict:
                return serialize_row(conflict)
            return None

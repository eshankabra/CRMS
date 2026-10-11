from app.database.connection import get_db_cursor, serialize_row, serialize_rows

class AttendanceService:

    @staticmethod
    def record_attendance(data, requesting_user):
        """
        Records attendance for a student in a course.
        Enforces:
        - Faculty can only mark attendance for courses assigned to them.
        - Student must have an Approved registration (enforced in code and by DB trigger).
        """
        course_id = data["course_id"]
        student_id = data["student_id"]
        attendance_date = data["attendance_date"]
        status = data["status"]

        with get_db_cursor(commit=True) as (cursor, conn):
            # Check faculty assignment
            if requesting_user["role"] == "Faculty":
                cursor.execute("SELECT faculty_id FROM course WHERE course_id = %s", (course_id,))
                course = cursor.fetchone()
                if not course or course["faculty_id"] != requesting_user["id"]:
                    return None, "FORBIDDEN", "Faculty can manage attendance only for courses assigned to them."

            # Check registration status
            cursor.execute("""
                SELECT registration_status FROM registration 
                WHERE student_id = %s AND course_id = %s
            """, (student_id, course_id))
            reg = cursor.fetchone()
            if not reg or reg["registration_status"] != "Approved":
                return None, "NOT_REGISTERED", "Attendance can only be recorded for students with an Approved course registration."

            cursor.execute("""
                INSERT INTO attendance (student_id, course_id, attendance_date, status)
                VALUES (%s, %s, %s, %s)
            """, (student_id, course_id, attendance_date, status))
            att_id = cursor.lastrowid
            
            cursor.execute("""
                SELECT a.*, s.roll_no, s.name AS student_name, c.course_code, c.course_name
                FROM attendance a
                JOIN student s ON a.student_id = s.student_id
                JOIN course c ON a.course_id = c.course_id
                WHERE a.attendance_id = %s
            """, (att_id,))
            return serialize_row(cursor.fetchone()), None, "Attendance recorded successfully."

    @staticmethod
    def update_attendance(attendance_id, status, requesting_user):
        """Updates/corrects an attendance record."""
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("SELECT a.*, c.faculty_id FROM attendance a JOIN course c ON a.course_id = c.course_id WHERE a.attendance_id = %s", (attendance_id,))
            att = cursor.fetchone()
            if not att:
                return None, "NOT_FOUND", "Attendance record not found."

            if requesting_user["role"] == "Faculty" and att["faculty_id"] != requesting_user["id"]:
                return None, "FORBIDDEN", "Unauthorized: faculty can only update attendance for their assigned course."

            cursor.execute("UPDATE attendance SET status = %s WHERE attendance_id = %s", (status, attendance_id))
            cursor.execute("""
                SELECT a.*, s.roll_no, s.name AS student_name, c.course_code, c.course_name
                FROM attendance a
                JOIN student s ON a.student_id = s.student_id
                JOIN course c ON a.course_id = c.course_id
                WHERE a.attendance_id = %s
            """, (attendance_id,))
            return serialize_row(cursor.fetchone()), None, "Attendance updated successfully."

    @staticmethod
    def get_my_attendance(student_id):
        """Returns student's complete attendance record and summary."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT * FROM student_attendance_summary 
                WHERE student_id = %s
                ORDER BY course_code
            """, (student_id,))
            summary = serialize_rows(cursor.fetchall())

            cursor.execute("""
                SELECT a.attendance_id, a.attendance_date, a.status, c.course_id, c.course_code, c.course_name
                FROM attendance a
                JOIN course c ON a.course_id = c.course_id
                WHERE a.student_id = %s
                ORDER BY a.attendance_date DESC
            """, (student_id,))
            logs = serialize_rows(cursor.fetchall())

            return {
                "summary": summary,
                "history": logs
            }

    @staticmethod
    def get_course_attendance(course_id, requesting_user):
        """Returns course attendance logs."""
        with get_db_cursor() as (cursor, conn):
            if requesting_user["role"] == "Faculty":
                cursor.execute("SELECT faculty_id FROM course WHERE course_id = %s", (course_id,))
                course = cursor.fetchone()
                if not course or course["faculty_id"] != requesting_user["id"]:
                    return None, "FORBIDDEN", "Unauthorized to view attendance for unassigned course."

            cursor.execute("""
                SELECT a.attendance_id, a.attendance_date, a.status, s.student_id, s.roll_no, s.name AS student_name
                FROM attendance a
                JOIN student s ON a.student_id = s.student_id
                WHERE a.course_id = %s
                ORDER BY a.attendance_date DESC, s.roll_no
            """, (course_id,))
            return serialize_rows(cursor.fetchall()), None, None

    @staticmethod
    def get_course_attendance_summary(course_id, requesting_user):
        """Returns attendance percentage breakdown by student for a given course."""
        with get_db_cursor() as (cursor, conn):
            if requesting_user["role"] == "Faculty":
                cursor.execute("SELECT faculty_id FROM course WHERE course_id = %s", (course_id,))
                course = cursor.fetchone()
                if not course or course["faculty_id"] != requesting_user["id"]:
                    return None, "FORBIDDEN", "Unauthorized to view attendance for unassigned course."

            cursor.execute("""
                SELECT 
                    s.student_id,
                    s.roll_no,
                    s.name AS student_name,
                    COUNT(a.attendance_id) AS total_classes,
                    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended_classes,
                    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS missed_classes,
                    fn_student_attendance_percentage(s.student_id, %s) AS attendance_percentage
                FROM registration r
                JOIN student s ON r.student_id = s.student_id
                LEFT JOIN attendance a ON s.student_id = a.student_id AND a.course_id = %s
                WHERE r.course_id = %s AND r.registration_status = 'Approved'
                GROUP BY s.student_id, s.roll_no, s.name
                ORDER BY s.roll_no
            """, (course_id, course_id, course_id))
            return serialize_rows(cursor.fetchall()), None, None

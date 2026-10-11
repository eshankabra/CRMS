from app.database.connection import get_db_cursor, serialize_rows, serialize_row

class ReportService:

    @staticmethod
    def get_registrations_report(department_id=None, status=None):
        """Aggregate report of registrations grouped by course and department."""
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT 
                    d.department_name,
                    c.course_code,
                    c.course_name,
                    c.credits,
                    COUNT(r.registration_id) AS total_registrations,
                    SUM(CASE WHEN r.registration_status = 'Approved' THEN 1 ELSE 0 END) AS approved_count,
                    SUM(CASE WHEN r.registration_status = 'Pending' THEN 1 ELSE 0 END) AS pending_count
                FROM course c
                JOIN department d ON c.department_id = d.department_id
                LEFT JOIN registration r ON c.course_id = r.course_id
                WHERE 1=1
            """
            params = []
            if department_id:
                query += " AND c.department_id = %s"
                params.append(department_id)
            if status:
                query += " AND r.registration_status = %s"
                params.append(status)
            query += " GROUP BY d.department_name, c.course_code, c.course_name, c.credits ORDER BY d.department_name, c.course_code"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_students_report(department_id=None, semester_id=None):
        """Aggregate report of student distribution and credit enrollment."""
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT 
                    d.department_name,
                    sem.semester_name,
                    sem.academic_year,
                    COUNT(DISTINCT s.student_id) AS total_students,
                    COUNT(r.registration_id) AS total_registered_courses,
                    COALESCE(SUM(c.credits), 0) AS total_enrolled_credits,
                    ROUND(COALESCE(AVG(c.credits), 0), 2) AS avg_credits_per_course
                FROM department d
                JOIN student s ON d.department_id = s.department_id
                JOIN semester sem ON s.semester_id = sem.semester_id
                LEFT JOIN registration r ON s.student_id = r.student_id AND r.registration_status = 'Approved'
                LEFT JOIN course c ON r.course_id = c.course_id
                WHERE 1=1
            """
            params = []
            if department_id:
                query += " AND s.department_id = %s"
                params.append(department_id)
            if semester_id:
                query += " AND s.semester_id = %s"
                params.append(semester_id)
            query += " GROUP BY d.department_name, sem.semester_name, sem.academic_year ORDER BY d.department_name"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_courses_report(department_id=None):
        """Course capacity utilization and enrollment statistics."""
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT * FROM course_seat_availability
            """
            params = []
            if department_id:
                query += " WHERE department_name = (SELECT department_name FROM department WHERE department_id = %s)"
                params.append(department_id)
            query += " ORDER BY department_name, course_code"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_payments_report():
        """Financial report showing revenue by payment status and mode."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT 
                    payment_status,
                    payment_mode,
                    COUNT(payment_id) AS total_transactions,
                    SUM(amount) AS total_amount,
                    ROUND(AVG(amount), 2) AS avg_transaction_amount
                FROM payment
                GROUP BY payment_status, payment_mode
                ORDER BY payment_status, payment_mode
            """)
            breakdown = serialize_rows(cursor.fetchall())

            cursor.execute("SELECT * FROM payment_summary ORDER BY total_paid DESC")
            student_summaries = serialize_rows(cursor.fetchall())

            return {
                "financial_breakdown": breakdown,
                "student_payment_summary": student_summaries
            }

    @staticmethod
    def get_attendance_report(course_id=None):
        """Attendance statistics across courses."""
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT 
                    c.course_id,
                    c.course_code,
                    c.course_name,
                    COUNT(DISTINCT a.attendance_date) AS total_lecture_days,
                    COUNT(a.attendance_id) AS total_records_logged,
                    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS total_present,
                    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS total_absent,
                    ROUND(
                        CASE 
                            WHEN COUNT(a.attendance_id) > 0 
                            THEN (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0) / COUNT(a.attendance_id)
                            ELSE 0.00 
                        END, 2
                    ) AS overall_attendance_rate
                FROM course c
                LEFT JOIN attendance a ON c.course_id = a.course_id
                WHERE 1=1
            """
            params = []
            if course_id:
                query += " AND c.course_id = %s"
                params.append(course_id)
            query += " GROUP BY c.course_id, c.course_code, c.course_name ORDER BY c.course_code"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_enrollment_summary(department_id=None):
        """Invokes stored procedure sp_generate_enrollment_report."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("CALL sp_generate_enrollment_report(%s);", (department_id,))
            return serialize_rows(cursor.fetchall())

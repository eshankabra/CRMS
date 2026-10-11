from app.database.connection import get_db_cursor, serialize_row, serialize_rows
from app.services.academic_service import AcademicService

class RegistrationService:

    @staticmethod
    def register_course(student_id, course_id, max_credits=24):
        """
        Registers student for a course in Pending status.
        Performs clash detection and invokes sp_register_student_course with row locking.
        """
        # Step 1: Check timetable conflict with already registered courses
        conflict = AcademicService.check_student_schedule_conflict(student_id, course_id)
        if conflict:
            return None, "TIMETABLE_CLASH", f"Timetable clash on {conflict.get('day')} with enrolled course {conflict.get('conflicting_course_code')} ({conflict.get('conflicting_course_name')})."

        # Step 2: Invoke stored procedure
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("""
                CALL sp_register_student_course(%s, %s, %s, @p_reg_id, @p_status, @p_msg);
            """, (student_id, course_id, max_credits))
            
            cursor.execute("SELECT @p_reg_id AS reg_id, @p_status AS status, @p_msg AS message;")
            result = cursor.fetchone()
            
            reg_id = result.get("reg_id")
            status = result.get("status")
            message = result.get("message")
            
            if status != "SUCCESS":
                return None, status, message
                
            # Fetch registration details from view
            cursor.execute("SELECT * FROM registration_details WHERE registration_id = %s", (reg_id,))
            reg = cursor.fetchone()
            return serialize_row(reg), None, message

    @staticmethod
    def approve_registration(registration_id):
        """
        Admin-only operation to approve a registration after verifying payment and seat capacity.
        Invokes stored procedure sp_approve_registration.
        """
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("CALL sp_approve_registration(%s, @p_status, @p_msg);", (registration_id,))
            cursor.execute("SELECT @p_status AS status, @p_msg AS message;")
            result = cursor.fetchone()
            
            status = result.get("status")
            message = result.get("message")
            
            if status != "SUCCESS":
                return None, status, message
                
            cursor.execute("SELECT * FROM registration_details WHERE registration_id = %s", (registration_id,))
            reg = cursor.fetchone()
            return serialize_row(reg), None, message

    @staticmethod
    def drop_registration(registration_id, requesting_user):
        """
        Drops a course registration safely.
        Validates ownership if initiated by student.
        """
        student_param = None
        if requesting_user["role"] == "Student":
            student_param = requesting_user["id"]

        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("CALL sp_drop_registration(%s, %s, @p_status, @p_msg);", (registration_id, student_param))
            cursor.execute("SELECT @p_status AS status, @p_msg AS message;")
            result = cursor.fetchone()
            
            status = result.get("status")
            message = result.get("message")
            
            if status != "SUCCESS":
                return False, status, message
            return True, None, message

    @staticmethod
    def get_my_registrations(student_id):
        """Returns registration history and status for authenticated student."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT * FROM registration_details 
                WHERE student_id = %s 
                ORDER BY registration_date DESC
            """, (student_id,))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_registration(registration_id, requesting_user):
        """Fetches a specific registration with role ownership check."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM registration_details WHERE registration_id = %s", (registration_id,))
            reg = cursor.fetchone()
            if not reg:
                return None, "NOT_FOUND", "Registration not found."
                
            if requesting_user["role"] == "Student" and reg["student_id"] != requesting_user["id"]:
                return None, "FORBIDDEN", "Unauthorized to view another student's registration."
                
            return serialize_row(reg), None, None

    @staticmethod
    def list_registrations(status=None, course_id=None, student_id=None):
        """Admin listing of registrations with filters."""
        with get_db_cursor() as (cursor, conn):
            query = "SELECT * FROM registration_details WHERE 1=1"
            params = []
            if status:
                query += " AND registration_status = %s"
                params.append(status)
            if course_id:
                query += " AND course_id = %s"
                params.append(course_id)
            if student_id:
                query += " AND student_id = %s"
                params.append(student_id)
            query += " ORDER BY registration_date DESC, registration_id DESC"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_course_availability(course_id):
        """Fetches seat capacity, approved count, pending count, and remaining seats from view."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM course_seat_availability WHERE course_id = %s", (course_id,))
            avail = cursor.fetchone()
            return serialize_row(avail) if avail else None

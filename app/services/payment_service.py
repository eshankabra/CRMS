from app.database.connection import get_db_cursor, serialize_row, serialize_rows
import uuid

class PaymentService:

    @staticmethod
    def create_payment(data, requesting_user):
        """
        Creates a Pending payment record.
        Students can only initiate payments for themselves.
        """
        student_id = data.get("student_id")
        if requesting_user["role"] == "Student":
            student_id = requesting_user["id"]
        elif not student_id:
            return None, "BAD_REQUEST", "student_id is required."

        registration_id = data.get("registration_id")
        amount = data["amount"]
        payment_mode = data["payment_mode"]
        txn_ref = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        with get_db_cursor(commit=True) as (cursor, conn):
            # If registration_id provided, verify it belongs to this student
            if registration_id:
                cursor.execute("SELECT student_id FROM registration WHERE registration_id = %s", (registration_id,))
                reg = cursor.fetchone()
                if not reg or reg["student_id"] != student_id:
                    return None, "BAD_REQUEST", "Invalid registration_id for this student."

            cursor.execute("""
                INSERT INTO payment (student_id, registration_id, amount, payment_date, payment_mode, payment_status, transaction_reference)
                VALUES (%s, %s, %s, CURDATE(), %s, 'Pending', %s)
            """, (student_id, registration_id, amount, payment_mode, txn_ref))
            payment_id = cursor.lastrowid
            
            cursor.execute("""
                SELECT p.*, s.roll_no, s.name AS student_name, c.course_code, c.course_name
                FROM payment p
                JOIN student s ON p.student_id = s.student_id
                LEFT JOIN registration r ON p.registration_id = r.registration_id
                LEFT JOIN course c ON r.course_id = c.course_id
                WHERE p.payment_id = %s
            """, (payment_id,))
            return serialize_row(cursor.fetchone()), None, "Payment intent created in Pending status."

    @staticmethod
    def verify_payment(payment_id):
        """
        Simulated Administrative operation: marks a Pending payment as Successful.
        """
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("SELECT * FROM payment WHERE payment_id = %s FOR UPDATE", (payment_id,))
            payment = cursor.fetchone()
            if not payment:
                return None, "NOT_FOUND", "Payment record not found."

            if payment["payment_status"] == "Successful":
                return None, "ALREADY_SUCCESSFUL", "Payment has already been marked as Successful."

            cursor.execute("""
                UPDATE payment 
                SET payment_status = 'Successful' 
                WHERE payment_id = %s
            """, (payment_id,))

            cursor.execute("""
                SELECT p.*, s.roll_no, s.name AS student_name, c.course_code, c.course_name
                FROM payment p
                JOIN student s ON p.student_id = s.student_id
                LEFT JOIN registration r ON p.registration_id = r.registration_id
                LEFT JOIN course c ON r.course_id = c.course_id
                WHERE p.payment_id = %s
            """, (payment_id,))
            return serialize_row(cursor.fetchone()), None, "Payment successfully verified by administrator."

    @staticmethod
    def get_my_payments(student_id):
        """Returns payments made by authenticated student."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT p.*, c.course_code, c.course_name
                FROM payment p
                LEFT JOIN registration r ON p.registration_id = r.registration_id
                LEFT JOIN course c ON r.course_id = c.course_id
                WHERE p.student_id = %s
                ORDER BY p.payment_date DESC, p.payment_id DESC
            """, (student_id,))
            return serialize_rows(cursor.fetchall())

    @staticmethod
    def get_payment(payment_id, requesting_user):
        """Fetches payment details with ownership check."""
        with get_db_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT p.*, s.roll_no, s.name AS student_name, c.course_code, c.course_name
                FROM payment p
                JOIN student s ON p.student_id = s.student_id
                LEFT JOIN registration r ON p.registration_id = r.registration_id
                LEFT JOIN course c ON r.course_id = c.course_id
                WHERE p.payment_id = %s
            """, (payment_id,))
            payment = cursor.fetchone()
            if not payment:
                return None, "NOT_FOUND", "Payment not found."
            if requesting_user["role"] == "Student" and payment["student_id"] != requesting_user["id"]:
                return None, "FORBIDDEN", "Unauthorized to view another student's payment."
            return serialize_row(payment), None, None

    @staticmethod
    def list_payments(status=None, student_id=None):
        """Admin listing of payments."""
        with get_db_cursor() as (cursor, conn):
            query = """
                SELECT p.*, s.roll_no, s.name AS student_name, c.course_code, c.course_name
                FROM payment p
                JOIN student s ON p.student_id = s.student_id
                LEFT JOIN registration r ON p.registration_id = r.registration_id
                LEFT JOIN course c ON r.course_id = c.course_id
                WHERE 1=1
            """
            params = []
            if status:
                query += " AND p.payment_status = %s"
                params.append(status)
            if student_id:
                query += " AND p.student_id = %s"
                params.append(student_id)
            query += " ORDER BY p.payment_date DESC, p.payment_id DESC"
            cursor.execute(query, tuple(params))
            return serialize_rows(cursor.fetchall())

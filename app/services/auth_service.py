from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.database.connection import get_db_cursor, serialize_row
import mysql.connector

class AuthService:

    @staticmethod
    def register_student(data):
        """Registers a new student account securely."""
        password_hash = generate_password_hash(data["password"])
        sql = """
            INSERT INTO student (
                roll_no, name, email, phone, date_of_birth, gender,
                department_id, semester_id, password_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data["roll_no"],
            data["name"],
            data["email"],
            data.get("phone"),
            data["date_of_birth"],
            data["gender"],
            data["department_id"],
            data["semester_id"],
            password_hash
        )
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(sql, params)
            student_id = cursor.lastrowid
            
            # Fetch created student without password hash
            cursor.execute("""
                SELECT student_id, roll_no, name, email, phone, date_of_birth, gender, department_id, semester_id, created_at
                FROM student WHERE student_id = %s
            """, (student_id,))
            student = cursor.fetchone()
            return serialize_row(student)

    @staticmethod
    def login(identifier, password, role):
        """
        Authenticates user based on role ('Admin', 'Faculty', 'Student')
        and returns JWT access token and profile info without password hash.
        """
        table_map = {
            "Admin": ("admin", "username = %s OR email = %s", "admin_id"),
            "Faculty": ("faculty", "email = %s", "faculty_id"),
            "Student": ("student", "email = %s OR roll_no = %s", "student_id")
        }
        
        if role not in table_map:
            return None, "Invalid role specified."
            
        table, where_clause, id_col = table_map[role]
        
        with get_db_cursor() as (cursor, conn):
            if role == "Admin" or role == "Student":
                query = f"SELECT * FROM {table} WHERE {where_clause}"
                cursor.execute(query, (identifier, identifier))
            else:
                query = f"SELECT * FROM {table} WHERE {where_clause}"
                cursor.execute(query, (identifier,))
                
            user = cursor.fetchone()
            
            if not user:
                return None, "Invalid credentials."
                
            stored_hash = user.get("password_hash")
            if not check_password_hash(stored_hash, password):
                return None, "Invalid credentials."
                
            user_id = user[id_col]
            user_name = user.get("name")
            user_email = user.get("email")
            
            # Prepare JWT claims
            additional_claims = {
                "user_id": user_id,
                "role": role,
                "email": user_email,
                "name": user_name
            }
            if role == "Student":
                additional_claims["roll_no"] = user.get("roll_no")
                additional_claims["semester_id"] = user.get("semester_id")
            elif role == "Faculty":
                additional_claims["department_id"] = user.get("department_id")
                
            access_token = create_access_token(
                identity=str(user_id),
                additional_claims=additional_claims
            )
            
            # Clean sensitive password hash from user response
            user_safe = serialize_row({k: v for k, v in user.items() if k != "password_hash"})
            
            return {
                "token": access_token,
                "token_type": "Bearer",
                "user": user_safe,
                "role": role
            }, None

    @staticmethod
    def get_profile(user_id, role):
        """Fetches profile of currently logged-in user."""
        with get_db_cursor() as (cursor, conn):
            if role == "Admin":
                cursor.execute("SELECT admin_id, username, name, email, created_at FROM admin WHERE admin_id = %s", (user_id,))
            elif role == "Faculty":
                cursor.execute("""
                    SELECT f.faculty_id, f.name, f.email, f.phone, f.qualification, f.department_id, d.department_name, f.created_at
                    FROM faculty f
                    JOIN department d ON f.department_id = d.department_id
                    WHERE f.faculty_id = %s
                """, (user_id,))
            elif role == "Student":
                cursor.execute("""
                    SELECT s.student_id, s.roll_no, s.name, s.email, s.phone, s.date_of_birth, s.gender,
                           s.department_id, d.department_name, s.semester_id, sem.semester_name, sem.academic_year, s.created_at
                    FROM student s
                    JOIN department d ON s.department_id = d.department_id
                    JOIN semester sem ON s.semester_id = sem.semester_id
                    WHERE s.student_id = %s
                """, (user_id,))
            else:
                return None
            row = cursor.fetchone()
            return serialize_row(row) if row else None

from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.services.auth_service import AuthService
from app.schemas.validators import StudentRegisterSchema
from app.middleware.auth import role_required, get_current_user
from app.utils.response import api_response

students_bp = Blueprint("students", __name__)

@students_bp.route("", methods=["GET"])
@role_required("Admin")
def list_students():
    """
    List students with search, filters, and pagination (Admin only)
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 10
      - in: query
        name: search
        type: string
        description: Search by name, roll number, or email
      - in: query
        name: department_id
        type: integer
      - in: query
        name: semester_id
        type: integer
    responses:
      200:
        description: Paginated student list
    """
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    search = request.args.get("search")
    dept_id = request.args.get("department_id", type=int)
    sem_id = request.args.get("semester_id", type=int)

    result = AcademicService.list_students(page, per_page, search, dept_id, sem_id)
    return api_response(
        success=True,
        message="Students retrieved successfully.",
        data=result["items"],
        pagination={
            "page": result["page"],
            "per_page": result["per_page"],
            "total": result["total"],
            "pages": result["pages"]
        }
    )

@students_bp.route("/<int:student_id>", methods=["GET"])
@role_required("Admin", "Student")
def get_student(student_id):
    """
    Get student profile by ID (Admin or the student themselves)
    ---
    tags:
      - Students
    security:
      - Bearer: []
    responses:
      200:
        description: Student profile details
      403:
        description: Access forbidden
    """
    current_user = get_current_user()
    if current_user["role"] == "Student" and current_user["id"] != student_id:
        return api_response(success=False, message="Unauthorized to view another student's profile.", status_code=403, error_code="FORBIDDEN")

    student = AcademicService.get_student(student_id)
    if not student:
        return api_response(success=False, message="Student not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Student retrieved successfully.", data=student)

@students_bp.route("", methods=["POST"])
@role_required("Admin")
def create_student():
    """
    Admin creates a student account
    ---
    tags:
      - Students
    security:
      - Bearer: []
    responses:
      201:
        description: Student account created
    """
    json_data = request.get_json() or {}
    errors = StudentRegisterSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    student = AuthService.register_student(json_data)
    return api_response(success=True, message="Student created successfully.", data=student, status_code=201)

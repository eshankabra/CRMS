from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.schemas.validators import FacultyCreateSchema
from app.middleware.auth import role_required, get_current_user
from app.utils.response import api_response

faculty_bp = Blueprint("faculty", __name__)

@faculty_bp.route("", methods=["GET"])
def list_faculty():
    """
    List faculty members
    ---
    tags:
      - Faculty
    parameters:
      - in: query
        name: department_id
        type: integer
    responses:
      200:
        description: List of faculty
    """
    dept_id = request.args.get("department_id", type=int)
    faculty_list = AcademicService.list_faculty(department_id=dept_id)
    return api_response(success=True, message="Faculty retrieved successfully.", data=faculty_list)

@faculty_bp.route("/<int:fac_id>", methods=["GET"])
def get_faculty(fac_id):
    """
    Get faculty profile by ID
    ---
    tags:
      - Faculty
    responses:
      200:
        description: Faculty details
    """
    faculty = AcademicService.get_faculty(fac_id)
    if not faculty:
        return api_response(success=False, message="Faculty member not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Faculty retrieved successfully.", data=faculty)

@faculty_bp.route("/<int:fac_id>/courses", methods=["GET"])
@role_required("Admin", "Faculty")
def get_faculty_courses(fac_id):
    """
    View courses assigned to a faculty member
    ---
    tags:
      - Faculty
    security:
      - Bearer: []
    responses:
      200:
        description: Courses assigned to faculty
    """
    current_user = get_current_user()
    if current_user["role"] == "Faculty" and current_user["id"] != fac_id:
        return api_response(success=False, message="Unauthorized to view another instructor's course list.", status_code=403, error_code="FORBIDDEN")
    
    courses = AcademicService.get_faculty_courses(fac_id)
    return api_response(success=True, message="Assigned courses retrieved.", data=courses)

@faculty_bp.route("", methods=["POST"])
@role_required("Admin")
def create_faculty():
    """
    Create a new faculty member (Admin only)
    ---
    tags:
      - Faculty
    security:
      - Bearer: []
    responses:
      201:
        description: Faculty created
    """
    json_data = request.get_json() or {}
    errors = FacultyCreateSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    fac = AcademicService.create_faculty(json_data)
    return api_response(success=True, message="Faculty member created successfully.", data=fac, status_code=201)

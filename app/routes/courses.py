from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.services.registration_service import RegistrationService
from app.schemas.validators import CourseCreateSchema
from app.middleware.auth import role_required
from app.utils.response import api_response

courses_bp = Blueprint("courses", __name__)

@courses_bp.route("", methods=["GET"])
def list_courses():
    """
    List courses with filters for department, faculty, course type, and search
    ---
    tags:
      - Courses
    parameters:
      - in: query
        name: department_id
        type: integer
      - in: query
        name: faculty_id
        type: integer
      - in: query
        name: course_type
        type: string
        enum: [Core, Elective]
      - in: query
        name: search
        type: string
    responses:
      200:
        description: List of courses with seats and faculty info
    """
    dept_id = request.args.get("department_id", type=int)
    fac_id = request.args.get("faculty_id", type=int)
    c_type = request.args.get("course_type")
    search = request.args.get("search")

    courses = AcademicService.list_courses(dept_id, fac_id, c_type, search)
    return api_response(success=True, message="Courses retrieved successfully.", data=courses)

@courses_bp.route("/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """
    Get course details by ID
    ---
    tags:
      - Courses
    responses:
      200:
        description: Course details
    """
    course = AcademicService.get_course(course_id)
    if not course:
        return api_response(success=False, message="Course not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Course retrieved successfully.", data=course)

@courses_bp.route("/<int:course_id>/availability", methods=["GET"])
def get_course_availability(course_id):
    """
    Get remaining seats and capacity status for a course
    ---
    tags:
      - Courses
    responses:
      200:
        description: Course seat availability status
    """
    avail = RegistrationService.get_course_availability(course_id)
    if not avail:
        return api_response(success=False, message="Course not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Seat availability retrieved.", data=avail)

@courses_bp.route("", methods=["POST"])
@role_required("Admin")
def create_course():
    """
    Create a new course (Admin only)
    ---
    tags:
      - Courses
    security:
      - Bearer: []
    responses:
      201:
        description: Course created
    """
    json_data = request.get_json() or {}
    errors = CourseCreateSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    course = AcademicService.create_course(json_data)
    return api_response(success=True, message="Course created successfully.", data=course, status_code=201)

@courses_bp.route("/<int:course_id>", methods=["PUT"])
@role_required("Admin")
def update_course(course_id):
    """
    Update course details or assign/change faculty (Admin only)
    ---
    tags:
      - Courses
    security:
      - Bearer: []
    responses:
      200:
        description: Course updated
    """
    json_data = request.get_json() or {}
    course = AcademicService.update_course(course_id, json_data)
    if not course:
        return api_response(success=False, message="Course not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Course updated successfully.", data=course)

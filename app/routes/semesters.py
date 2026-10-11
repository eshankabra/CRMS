from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.schemas.validators import SemesterSchema
from app.middleware.auth import role_required
from app.utils.response import api_response

semesters_bp = Blueprint("semesters", __name__)

@semesters_bp.route("", methods=["GET"])
def list_semesters():
    """
    List all semesters (supports ?active=true)
    ---
    tags:
      - Semesters
    parameters:
      - in: query
        name: active
        type: boolean
        required: false
    responses:
      200:
        description: List of semesters
    """
    active_param = request.args.get("active", "").lower() in ("true", "1")
    semesters = AcademicService.list_semesters(active_only=active_param)
    return api_response(success=True, message="Semesters retrieved successfully.", data=semesters)

@semesters_bp.route("/active", methods=["GET"])
def get_active_semesters():
    """
    Get currently active academic semesters
    ---
    tags:
      - Semesters
    responses:
      200:
        description: Active semesters
    """
    semesters = AcademicService.list_semesters(active_only=True)
    return api_response(success=True, message="Active semesters retrieved.", data=semesters)

@semesters_bp.route("/<int:sem_id>", methods=["GET"])
def get_semester(sem_id):
    """
    Get semester details by ID
    ---
    tags:
      - Semesters
    responses:
      200:
        description: Semester details
    """
    sem = AcademicService.get_semester(sem_id)
    if not sem:
        return api_response(success=False, message="Semester not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Semester retrieved successfully.", data=sem)

@semesters_bp.route("", methods=["POST"])
@role_required("Admin")
def create_semester():
    """
    Create a new semester with date checks (Admin only)
    ---
    tags:
      - Semesters
    security:
      - Bearer: []
    responses:
      201:
        description: Semester created
    """
    json_data = request.get_json() or {}
    errors = SemesterSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    try:
        sem = AcademicService.create_semester(json_data)
        return api_response(success=True, message="Semester created successfully.", data=sem, status_code=201)
    except ValueError as ve:
        return api_response(success=False, message=str(ve), status_code=400, error_code="BAD_REQUEST")

@semesters_bp.route("/<int:sem_id>", methods=["PUT"])
@role_required("Admin")
def update_semester(sem_id):
    """
    Update semester (Admin only)
    ---
    tags:
      - Semesters
    security:
      - Bearer: []
    responses:
      200:
        description: Semester updated
    """
    json_data = request.get_json() or {}
    sem = AcademicService.update_semester(sem_id, json_data)
    if not sem:
        return api_response(success=False, message="Semester not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Semester updated successfully.", data=sem)

@semesters_bp.route("/<int:sem_id>", methods=["DELETE"])
@role_required("Admin")
def delete_semester(sem_id):
    """
    Delete semester with safe integrity checks (Admin only)
    ---
    tags:
      - Semesters
    security:
      - Bearer: []
    responses:
      200:
        description: Semester deleted
    """
    ok, err = AcademicService.delete_semester(sem_id)
    if not ok:
        return api_response(success=False, message=err, status_code=409, error_code="CONFLICT")
    return api_response(success=True, message="Semester deleted successfully.")

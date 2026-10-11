from flask import Blueprint, request, current_app
from app.services.registration_service import RegistrationService
from app.schemas.validators import RegistrationCreateSchema
from app.middleware.auth import role_required, get_current_user
from app.utils.response import api_response

registrations_bp = Blueprint("registrations", __name__)

@registrations_bp.route("", methods=["POST"])
@role_required("Student", "Admin")
def register_course():
    """
    Register for a course (creates registration in Pending status)
    ---
    tags:
      - Registrations
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - course_id
          properties:
            course_id:
              type: integer
              example: 1
            student_id:
              type: integer
              description: Required only if Admin is registering on behalf of student
    responses:
      201:
        description: Registration initiated in Pending status
      400:
        description: Course full, duplicate registration, or credit limit exceeded
    """
    json_data = request.get_json() or {}
    errors = RegistrationCreateSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")

    current_user = get_current_user()
    student_id = current_user["id"] if current_user["role"] == "Student" else json_data.get("student_id")
    if not student_id:
        return api_response(success=False, message="student_id is required for administrative registration.", status_code=400, error_code="BAD_REQUEST")

    max_credits = current_app.config.get("MAX_CREDITS_PER_SEMESTER", 24)
    reg, err_code, msg = RegistrationService.register_course(student_id, json_data["course_id"], max_credits)
    if err_code:
        status_code = 409 if err_code in ("DUPLICATE_REGISTRATION", "COURSE_FULL") else 400
        return api_response(success=False, message=msg, status_code=status_code, error_code=err_code)

    return api_response(success=True, message=msg, data=reg, status_code=201)

@registrations_bp.route("/me", methods=["GET"])
@role_required("Student")
def get_my_registrations():
    """
    Get own course registration history
    ---
    tags:
      - Registrations
    security:
      - Bearer: []
    responses:
      200:
        description: List of registrations for authenticated student
    """
    current_user = get_current_user()
    registrations = RegistrationService.get_my_registrations(current_user["id"])
    return api_response(success=True, message="Registrations retrieved successfully.", data=registrations)

@registrations_bp.route("/<int:reg_id>", methods=["GET"])
@role_required("Admin", "Student")
def get_registration(reg_id):
    """
    Get registration details (Authorized access only)
    ---
    tags:
      - Registrations
    security:
      - Bearer: []
    responses:
      200:
        description: Registration details
      403:
        description: Forbidden
      404:
        description: Not found
    """
    current_user = get_current_user()
    reg, err_code, msg = RegistrationService.get_registration(reg_id, current_user)
    if err_code:
        status_code = 403 if err_code == "FORBIDDEN" else 404
        return api_response(success=False, message=msg, status_code=status_code, error_code=err_code)
    return api_response(success=True, message="Registration retrieved successfully.", data=reg)

@registrations_bp.route("/<int:reg_id>", methods=["DELETE"])
@role_required("Admin", "Student")
def drop_registration(reg_id):
    """
    Drop / cancel a course registration
    ---
    tags:
      - Registrations
    security:
      - Bearer: []
    responses:
      200:
        description: Registration dropped successfully
      403:
        description: Students cannot drop another student's registration
    """
    current_user = get_current_user()
    ok, err_code, msg = RegistrationService.drop_registration(reg_id, current_user)
    if not ok:
        status_code = 403 if err_code == "FORBIDDEN" else 400
        return api_response(success=False, message=msg, status_code=status_code, error_code=err_code)
    return api_response(success=True, message=msg)

@registrations_bp.route("", methods=["GET"])
@role_required("Admin")
def list_registrations():
    """
    List all registrations with filters (Admin only)
    ---
    tags:
      - Registrations
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [Pending, Approved]
      - in: query
        name: course_id
        type: integer
      - in: query
        name: student_id
        type: integer
    responses:
      200:
        description: List of registrations
    """
    status = request.args.get("status")
    course_id = request.args.get("course_id", type=int)
    student_id = request.args.get("student_id", type=int)

    registrations = RegistrationService.list_registrations(status, course_id, student_id)
    return api_response(success=True, message="Registrations retrieved successfully.", data=registrations)

@registrations_bp.route("/<int:reg_id>/approve", methods=["POST"])
@role_required("Admin")
def approve_registration(reg_id):
    """
    Approve registration after verifying payment and course capacity (Admin only)
    ---
    tags:
      - Registrations
    security:
      - Bearer: []
    responses:
      200:
        description: Registration approved
      400:
        description: Payment required or course full
    """
    reg, err_code, msg = RegistrationService.approve_registration(reg_id)
    if err_code:
        return api_response(success=False, message=msg, status_code=400, error_code=err_code)
    return api_response(success=True, message=msg, data=reg)

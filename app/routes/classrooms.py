from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.schemas.validators import ClassroomSchema
from app.middleware.auth import role_required
from app.utils.response import api_response

classrooms_bp = Blueprint("classrooms", __name__)

@classrooms_bp.route("", methods=["GET"])
def list_classrooms():
    """
    List all classrooms (supports ?min_capacity=...)
    ---
    tags:
      - Classrooms
    parameters:
      - in: query
        name: min_capacity
        type: integer
    responses:
      200:
        description: List of classrooms
    """
    min_cap = request.args.get("min_capacity", type=int)
    rooms = AcademicService.list_classrooms(min_capacity=min_cap)
    return api_response(success=True, message="Classrooms retrieved successfully.", data=rooms)

@classrooms_bp.route("/<int:room_id>", methods=["GET"])
def get_classroom(room_id):
    """
    Get classroom by ID
    ---
    tags:
      - Classrooms
    responses:
      200:
        description: Classroom details
    """
    room = AcademicService.get_classroom(room_id)
    if not room:
        return api_response(success=False, message="Classroom not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Classroom retrieved successfully.", data=room)

@classrooms_bp.route("", methods=["POST"])
@role_required("Admin")
def create_classroom():
    """
    Create a new classroom (Admin only)
    ---
    tags:
      - Classrooms
    security:
      - Bearer: []
    responses:
      201:
        description: Classroom created
    """
    json_data = request.get_json() or {}
    errors = ClassroomSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    room = AcademicService.create_classroom(json_data)
    return api_response(success=True, message="Classroom created successfully.", data=room, status_code=201)

@classrooms_bp.route("/<int:room_id>", methods=["PUT"])
@role_required("Admin")
def update_classroom(room_id):
    """
    Update classroom (Admin only)
    ---
    tags:
      - Classrooms
    security:
      - Bearer: []
    responses:
      200:
        description: Classroom updated
    """
    json_data = request.get_json() or {}
    room = AcademicService.update_classroom(room_id, json_data)
    if not room:
        return api_response(success=False, message="Classroom not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Classroom updated successfully.", data=room)

@classrooms_bp.route("/<int:room_id>", methods=["DELETE"])
@role_required("Admin")
def delete_classroom(room_id):
    """
    Delete classroom (Admin only)
    ---
    tags:
      - Classrooms
    security:
      - Bearer: []
    responses:
      200:
        description: Classroom deleted
    """
    ok, err = AcademicService.delete_classroom(room_id)
    if not ok:
        return api_response(success=False, message=err, status_code=409, error_code="CONFLICT")
    return api_response(success=True, message="Classroom deleted successfully.")

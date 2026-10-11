from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.schemas.validators import DepartmentSchema
from app.middleware.auth import role_required
from app.utils.response import api_response

departments_bp = Blueprint("departments", __name__)

@departments_bp.route("", methods=["GET"])
def list_departments():
    """
    List all departments
    ---
    tags:
      - Departments
    responses:
      200:
        description: List of academic departments
    """
    departments = AcademicService.list_departments()
    return api_response(success=True, message="Departments retrieved successfully.", data=departments)

@departments_bp.route("/<int:dept_id>", methods=["GET"])
def get_department(dept_id):
    """
    Get department by ID
    ---
    tags:
      - Departments
    parameters:
      - in: path
        name: dept_id
        type: integer
        required: true
    responses:
      200:
        description: Department details
      404:
        description: Department not found
    """
    dept = AcademicService.get_department(dept_id)
    if not dept:
        return api_response(success=False, message="Department not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Department retrieved successfully.", data=dept)

@departments_bp.route("", methods=["POST"])
@role_required("Admin")
def create_department():
    """
    Create a new department (Admin only)
    ---
    tags:
      - Departments
    security:
      - Bearer: []
    responses:
      201:
        description: Department created
    """
    json_data = request.get_json() or {}
    errors = DepartmentSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    dept = AcademicService.create_department(json_data)
    return api_response(success=True, message="Department created successfully.", data=dept, status_code=201)

@departments_bp.route("/<int:dept_id>", methods=["PUT"])
@role_required("Admin")
def update_department(dept_id):
    """
    Update department (Admin only)
    ---
    tags:
      - Departments
    security:
      - Bearer: []
    responses:
      200:
        description: Department updated
    """
    json_data = request.get_json() or {}
    dept = AcademicService.update_department(dept_id, json_data)
    if not dept:
        return api_response(success=False, message="Department not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Department updated successfully.", data=dept)

@departments_bp.route("/<int:dept_id>", methods=["DELETE"])
@role_required("Admin")
def delete_department(dept_id):
    """
    Delete department with safe foreign key handling (Admin only)
    ---
    tags:
      - Departments
    security:
      - Bearer: []
    responses:
      200:
        description: Department deleted
      409:
        description: Cannot delete department with active dependencies
    """
    ok, err = AcademicService.delete_department(dept_id)
    if not ok:
        return api_response(success=False, message=err, status_code=409, error_code="CONFLICT")
    return api_response(success=True, message="Department deleted successfully.")

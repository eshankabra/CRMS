from flask import Blueprint, request
from app.services.attendance_service import AttendanceService
from app.schemas.validators import AttendanceRecordSchema
from app.middleware.auth import role_required, get_current_user
from app.utils.response import api_response

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("", methods=["POST"])
@role_required("Faculty", "Admin")
def record_attendance():
    """
    Record attendance for a student (Faculty or Admin)
    Faculty can only record attendance for courses assigned to them.
    Student must have an Approved registration.
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - student_id
            - course_id
            - attendance_date
            - status
          properties:
            student_id:
              type: integer
              example: 1
            course_id:
              type: integer
              example: 3
            attendance_date:
              type: string
              format: date
              example: "2026-08-31"
            status:
              type: string
              enum: [Present, Absent]
              example: "Present"
    responses:
      201:
        description: Attendance logged
      400:
        description: Student not enrolled or invalid data
      403:
        description: Faculty not assigned to this course
    """
    json_data = request.get_json() or {}
    errors = AttendanceRecordSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")

    current_user = get_current_user()
    att, err_code, msg = AttendanceService.record_attendance(json_data, current_user)
    if err_code:
        status_code = 403 if err_code == "FORBIDDEN" else 400
        return api_response(success=False, message=msg, status_code=status_code, error_code=err_code)

    return api_response(success=True, message=msg, data=att, status_code=201)

@attendance_bp.route("/<int:att_id>", methods=["PUT"])
@role_required("Faculty", "Admin")
def update_attendance(att_id):
    """
    Correct an attendance record with authorization
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [Present, Absent]
    responses:
      200:
        description: Attendance record corrected
    """
    json_data = request.get_json() or {}
    status = json_data.get("status")
    if status not in ("Present", "Absent"):
        return api_response(success=False, message="Status must be either 'Present' or 'Absent'.", status_code=400, error_code="BAD_REQUEST")

    current_user = get_current_user()
    att, err_code, msg = AttendanceService.update_attendance(att_id, status, current_user)
    if err_code:
        status_code = 403 if err_code == "FORBIDDEN" else 404
        return api_response(success=False, message=msg, status_code=status_code, error_code=err_code)

    return api_response(success=True, message=msg, data=att)

@attendance_bp.route("/me", methods=["GET"])
@role_required("Student")
def get_my_attendance():
    """
    Get student's own attendance history and course percentages
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    responses:
      200:
        description: Attendance records and course summaries
    """
    current_user = get_current_user()
    result = AttendanceService.get_my_attendance(current_user["id"])
    return api_response(success=True, message="Attendance history retrieved.", data=result)

@attendance_bp.route("/course/<int:course_id>", methods=["GET"])
@role_required("Faculty", "Admin")
def get_course_attendance(course_id):
    """
    View attendance records for a specific course
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    responses:
      200:
        description: Attendance logs
    """
    current_user = get_current_user()
    logs, err_code, msg = AttendanceService.get_course_attendance(course_id, current_user)
    if err_code:
        return api_response(success=False, message=msg, status_code=403, error_code=err_code)
    return api_response(success=True, message="Course attendance logs retrieved.", data=logs)

@attendance_bp.route("/course/<int:course_id>/summary", methods=["GET"])
@role_required("Faculty", "Admin")
def get_course_attendance_summary(course_id):
    """
    View summary statistics and attendance percentage per student for a course
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    responses:
      200:
        description: Course attendance summary
    """
    current_user = get_current_user()
    summary, err_code, msg = AttendanceService.get_course_attendance_summary(course_id, current_user)
    if err_code:
        return api_response(success=False, message=msg, status_code=403, error_code=err_code)
    return api_response(success=True, message="Course attendance summary retrieved.", data=summary)

from flask import Blueprint, request
from app.services.academic_service import AcademicService
from app.schemas.validators import ScheduleCreateSchema
from app.middleware.auth import role_required, get_current_user
from app.utils.response import api_response

schedules_bp = Blueprint("schedules", __name__)

@schedules_bp.route("", methods=["GET"])
def list_schedules():
    """
    List course schedules
    ---
    tags:
      - Course Schedules
    parameters:
      - in: query
        name: semester_id
        type: integer
      - in: query
        name: day
        type: string
        enum: [Monday, Tuesday, Wednesday, Thursday, Friday, Saturday]
    responses:
      200:
        description: List of scheduled classes
    """
    sem_id = request.args.get("semester_id", type=int)
    day = request.args.get("day")
    schedules = AcademicService.list_schedules(semester_id=sem_id, day=day)
    return api_response(success=True, message="Course schedules retrieved.", data=schedules)

@schedules_bp.route("", methods=["POST"])
@role_required("Admin")
def create_schedule():
    """
    Schedule a course class (Admin only)
    Enforces room conflict, faculty clash, and capacity rules via triggers.
    ---
    tags:
      - Course Schedules
    security:
      - Bearer: []
    responses:
      201:
        description: Schedule created
      400:
        description: Timetable clash or capacity conflict
    """
    json_data = request.get_json() or {}
    errors = ScheduleCreateSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    sched = AcademicService.create_schedule(json_data)
    return api_response(success=True, message="Course scheduled successfully.", data=sched, status_code=201)

@schedules_bp.route("/me", methods=["GET"])
@role_required("Student")
def get_my_timetable():
    """
    Get weekly timetable for authenticated student
    ---
    tags:
      - Course Schedules
    security:
      - Bearer: []
    responses:
      200:
        description: Weekly timetable
    """
    current_user = get_current_user()
    timetable = AcademicService.get_student_timetable(current_user["id"])
    return api_response(success=True, message="Timetable retrieved successfully.", data=timetable)

@schedules_bp.route("/student/<int:student_id>", methods=["GET"])
@role_required("Admin", "Student")
def get_student_timetable(student_id):
    """
    Get timetable for a student (Admin or the student themselves)
    ---
    tags:
      - Course Schedules
    security:
      - Bearer: []
    responses:
      200:
        description: Student timetable
    """
    current_user = get_current_user()
    if current_user["role"] == "Student" and current_user["id"] != student_id:
        return api_response(success=False, message="Unauthorized to view another student's timetable.", status_code=403, error_code="FORBIDDEN")
    
    timetable = AcademicService.get_student_timetable(student_id)
    return api_response(success=True, message="Student timetable retrieved.", data=timetable)

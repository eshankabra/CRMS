from flask import Blueprint, request
from app.services.report_service import ReportService
from app.middleware.auth import role_required
from app.utils.response import api_response

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/registrations", methods=["GET"])
@role_required("Admin", "Faculty")
def report_registrations():
    """
    Registrations report by department and course
    ---
    tags:
      - Reports
    security:
      - Bearer: []
    parameters:
      - in: query
        name: department_id
        type: integer
      - in: query
        name: status
        type: string
        enum: [Approved, Pending]
    responses:
      200:
        description: Aggregate registration report
    """
    dept_id = request.args.get("department_id", type=int)
    status = request.args.get("status")
    data = ReportService.get_registrations_report(dept_id, status)
    return api_response(success=True, message="Registrations report generated.", data=data)

@reports_bp.route("/students", methods=["GET"])
@role_required("Admin", "Faculty")
def report_students():
    """
    Student distribution and credit load report
    ---
    tags:
      - Reports
    security:
      - Bearer: []
    parameters:
      - in: query
        name: department_id
        type: integer
      - in: query
        name: semester_id
        type: integer
    responses:
      200:
        description: Aggregate student report
    """
    dept_id = request.args.get("department_id", type=int)
    sem_id = request.args.get("semester_id", type=int)
    data = ReportService.get_students_report(dept_id, sem_id)
    return api_response(success=True, message="Student distribution report generated.", data=data)

@reports_bp.route("/courses", methods=["GET"])
@role_required("Admin", "Faculty")
def report_courses():
    """
    Course seat capacity and utilization report
    ---
    tags:
      - Reports
    security:
      - Bearer: []
    parameters:
      - in: query
        name: department_id
        type: integer
    responses:
      200:
        description: Course capacity and utilization data
    """
    dept_id = request.args.get("department_id", type=int)
    data = ReportService.get_courses_report(dept_id)
    return api_response(success=True, message="Courses report generated.", data=data)

@reports_bp.route("/payments", methods=["GET"])
@role_required("Admin")
def report_payments():
    """
    Financial revenue and transaction status report (Admin only)
    ---
    tags:
      - Reports
    security:
      - Bearer: []
    responses:
      200:
        description: Financial audit report
    """
    data = ReportService.get_payments_report()
    return api_response(success=True, message="Financial report generated.", data=data)

@reports_bp.route("/attendance", methods=["GET"])
@role_required("Admin", "Faculty")
def report_attendance():
    """
    Overall attendance rates by course
    ---
    tags:
      - Reports
    security:
      - Bearer: []
    parameters:
      - in: query
        name: course_id
        type: integer
    responses:
      200:
        description: Attendance aggregate report
    """
    course_id = request.args.get("course_id", type=int)
    data = ReportService.get_attendance_report(course_id)
    return api_response(success=True, message="Attendance report generated.", data=data)

@reports_bp.route("/enrollment-summary", methods=["GET"])
@role_required("Admin", "Faculty")
def report_enrollment_summary():
    """
    Course enrollment summary report (invokes stored procedure sp_generate_enrollment_report)
    ---
    tags:
      - Reports
    security:
      - Bearer: []
    parameters:
      - in: query
        name: department_id
        type: integer
    responses:
      200:
        description: Enrollment summary generated via database stored procedure
    """
    dept_id = request.args.get("department_id", type=int)
    data = ReportService.get_enrollment_summary(dept_id)
    return api_response(success=True, message="Enrollment summary generated via stored procedure.", data=data)

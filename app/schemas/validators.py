from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class StudentRegisterSchema(Schema):
    roll_no = fields.String(required=True, validate=validate.Length(min=3, max=20))
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=15))
    date_of_birth = fields.Date(required=True)
    gender = fields.String(required=True, validate=validate.OneOf(["Male", "Female", "Other"]))
    department_id = fields.Integer(required=True)
    semester_id = fields.Integer(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=100))

class LoginSchema(Schema):
    email = fields.String(required=True) # or username for admin
    password = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(["Admin", "Faculty", "Student"]))

class DepartmentSchema(Schema):
    department_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    building = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    hod_name = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))

class SemesterSchema(Schema):
    semester_name = fields.String(required=True, validate=validate.OneOf(["Spring", "Summer", "Fall"]))
    academic_year = fields.String(required=True, validate=validate.Regexp(r'^\d{4}-\d{2}$', error="Academic year must be formatted as YYYY-YY (e.g., 2026-27)"))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    is_active = fields.Boolean(required=False, load_default=False)

    @validates('end_date')
    def validate_dates(self, value, **kwargs):
        # Comparison with start_date is handled in service
        pass

class FacultyCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=15))
    qualification = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    department_id = fields.Integer(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=100))

class CourseCreateSchema(Schema):
    course_code = fields.String(required=True, validate=validate.Length(min=3, max=20))
    course_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    credits = fields.Integer(required=True, validate=validate.Range(min=1, max=6))
    course_type = fields.String(required=True, validate=validate.OneOf(["Core", "Elective"]))
    maximum_seats = fields.Integer(required=True, validate=validate.Range(min=1))
    department_id = fields.Integer(required=True)
    faculty_id = fields.Integer(required=False, allow_none=True)

class ClassroomSchema(Schema):
    room_number = fields.String(required=True, validate=validate.Length(min=1, max=20))
    building = fields.String(required=True, validate=validate.Length(min=1, max=100))
    capacity = fields.Integer(required=True, validate=validate.Range(min=1))

class ScheduleCreateSchema(Schema):
    course_id = fields.Integer(required=True)
    semester_id = fields.Integer(required=True)
    room_id = fields.Integer(required=True)
    day = fields.String(required=True, validate=validate.OneOf(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]))
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)

class RegistrationCreateSchema(Schema):
    course_id = fields.Integer(required=True)
    student_id = fields.Integer(required=False, allow_none=True) # Optional for student role, required if Admin registers

class PaymentCreateSchema(Schema):
    student_id = fields.Integer(required=False, allow_none=True)
    registration_id = fields.Integer(required=False, allow_none=True)
    amount = fields.Decimal(required=True, as_string=False)
    payment_mode = fields.String(required=True, validate=validate.OneOf(["Online", "Offline"]))

class AttendanceRecordSchema(Schema):
    student_id = fields.Integer(required=True)
    course_id = fields.Integer(required=True)
    attendance_date = fields.Date(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["Present", "Absent"]))

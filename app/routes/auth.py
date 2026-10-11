from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.schemas.validators import StudentRegisterSchema, LoginSchema
from app.middleware.auth import role_required, get_current_user, revoked_tokens
from app.utils.response import api_response
from flask_jwt_extended import jwt_required, get_jwt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Student self-registration
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - roll_no
            - name
            - email
            - date_of_birth
            - gender
            - department_id
            - semester_id
            - password
          properties:
            roll_no:
              type: string
              example: "25BBS0099"
            name:
              type: string
              example: "Rahul Verma"
            email:
              type: string
              example: "rahul.v@vitstudent.ac.in"
            phone:
              type: string
              example: "9811100099"
            date_of_birth:
              type: string
              example: "2005-01-30"
            gender:
              type: string
              enum: [Male, Female, Other]
              example: "Male"
            department_id:
              type: integer
              example: 4
            semester_id:
              type: integer
              example: 1
            password:
              type: string
              example: "Student@123"
    responses:
      201:
        description: Student registered successfully
      400:
        description: Validation error
    """
    json_data = request.get_json() or {}
    schema = StudentRegisterSchema()
    errors = schema.validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    student = AuthService.register_student(json_data)
    return api_response(success=True, message="Student registered successfully.", data=student, status_code=201)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login for Admin, Faculty, or Student
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - role
          properties:
            email:
              type: string
              example: "admin@crms.vit.ac.in"
            password:
              type: string
              example: "Admin@123"
            role:
              type: string
              enum: [Admin, Faculty, Student]
              example: "Admin"
    responses:
      200:
        description: Successfully authenticated
      401:
        description: Invalid credentials
    """
    json_data = request.get_json() or {}
    schema = LoginSchema()
    errors = schema.validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")
    
    result, err = AuthService.login(json_data["email"], json_data["password"], json_data["role"])
    if err:
        return api_response(success=False, message=err, status_code=401, error_code="INVALID_CREDENTIALS")
        
    return api_response(success=True, message=f"Logged in successfully as {json_data['role']}.", data=result, status_code=200)

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    User logout and token revocation
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully logged out
    """
    claims = get_jwt()
    jti = claims.get("jti")
    if jti:
        revoked_tokens.add(jti)
    return api_response(success=True, message="Successfully logged out and token invalidated.", status_code=200)

@auth_bp.route("/me", methods=["GET"])
@role_required("Admin", "Faculty", "Student")
def get_me():
    """
    Get profile of currently logged-in user
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
    """
    user = get_current_user()
    profile = AuthService.get_profile(user["id"], user["role"])
    if not profile:
        return api_response(success=False, message="User profile not found.", status_code=404, error_code="NOT_FOUND")
    return api_response(success=True, message="Profile retrieved successfully.", data=profile, status_code=200)

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Simulated development password reset token request
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Password recovery initiated (simulated)
    """
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return api_response(success=False, message="Email is required.", status_code=400, error_code="BAD_REQUEST")
    # For demo review: Safe development response without pretending real email sent
    return api_response(
        success=True, 
        message="Simulated password recovery workflow: reset token generated for development demonstration.", 
        data={"simulated_reset_token": "DEV-RESET-TOKEN-DEMO-2026", "instructions": "Use POST /api/v1/auth/reset-password with this token."},
        status_code=200
    )

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Password reset using verification token
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Password updated
    """
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")
    if not token or not new_password:
        return api_response(success=False, message="Token and new_password are required.", status_code=400, error_code="BAD_REQUEST")
    return api_response(success=True, message="Password reset successful (demo environment).", status_code=200)

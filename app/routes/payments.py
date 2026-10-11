from flask import Blueprint, request
from app.services.payment_service import PaymentService
from app.schemas.validators import PaymentCreateSchema
from app.middleware.auth import role_required, get_current_user
from app.utils.response import api_response

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("", methods=["POST"])
@role_required("Student", "Admin")
def create_payment():
    """
    Initiate a Pending fee payment / payment intent
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
            - payment_mode
          properties:
            registration_id:
              type: integer
              example: 1
            amount:
              type: number
              format: float
              example: 6000.00
            payment_mode:
              type: string
              enum: [Online, Offline]
              example: "Online"
    responses:
      201:
        description: Pending payment created
    """
    json_data = request.get_json() or {}
    errors = PaymentCreateSchema().validate(json_data)
    if errors:
        return api_response(success=False, message="Validation error", data=errors, status_code=400, error_code="VALIDATION_ERROR")

    current_user = get_current_user()
    payment, err_code, msg = PaymentService.create_payment(json_data, current_user)
    if err_code:
        return api_response(success=False, message=msg, status_code=400, error_code=err_code)

    return api_response(success=True, message=msg, data=payment, status_code=201)

@payments_bp.route("/me", methods=["GET"])
@role_required("Student")
def get_my_payments():
    """
    Get payment history for authenticated student
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    responses:
      200:
        description: List of payments made by the student
    """
    current_user = get_current_user()
    payments = PaymentService.get_my_payments(current_user["id"])
    return api_response(success=True, message="Payment history retrieved.", data=payments)

@payments_bp.route("/<int:payment_id>", methods=["GET"])
@role_required("Admin", "Student")
def get_payment(payment_id):
    """
    Get payment details (Authorized access only)
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    responses:
      200:
        description: Payment details
      403:
        description: Forbidden
      404:
        description: Not found
    """
    current_user = get_current_user()
    payment, err_code, msg = PaymentService.get_payment(payment_id, current_user)
    if err_code:
        status_code = 403 if err_code == "FORBIDDEN" else 404
        return api_response(success=False, message=msg, status_code=status_code, error_code=err_code)
    return api_response(success=True, message="Payment retrieved successfully.", data=payment)

@payments_bp.route("", methods=["GET"])
@role_required("Admin")
def list_payments():
    """
    List all payments with filters (Admin only)
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [Pending, Successful]
      - in: query
        name: student_id
        type: integer
    responses:
      200:
        description: List of payments
    """
    status = request.args.get("status")
    student_id = request.args.get("student_id", type=int)
    payments = PaymentService.list_payments(status, student_id)
    return api_response(success=True, message="Payments retrieved successfully.", data=payments)

@payments_bp.route("/<int:payment_id>/verify", methods=["POST"])
@role_required("Admin")
def verify_payment(payment_id):
    """
    Simulated Administrator-only payment verification operation.
    Marks a Pending payment as Successful.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    responses:
      200:
        description: Payment verified successfully
      400:
        description: Payment already verified or invalid
    """
    payment, err_code, msg = PaymentService.verify_payment(payment_id)
    if err_code:
        return api_response(success=False, message=msg, status_code=400, error_code=err_code)
    return api_response(success=True, message=msg, data=payment)

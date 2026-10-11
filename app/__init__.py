from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import jwt, cors, swagger
from app.database.connection import init_db_pool, get_db_cursor
from app.errors.handlers import register_error_handlers

def create_app(config_name="default"):
    """
    Application Factory Pattern for CRMS Backend
    """
    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Initialize MySQL Connection Pool
    init_db_pool(config_class)

    # Initialize Extensions
    jwt.init_app(app)
    cors.init_app(app)
    swagger.init_app(app)

    # Register Centralized Error Handlers
    register_error_handlers(app)

    # Health Check Endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        db_status = "UNKNOWN"
        try:
            with get_db_cursor() as (cursor, conn):
                cursor.execute("SELECT 1 AS ok")
                if cursor.fetchone()["ok"] == 1:
                    db_status = "CONNECTED"
        except Exception as e:
            db_status = f"ERROR: {str(e)}"

        return jsonify({
            "status": "UP",
            "service": "Course Registration & Management System (CRMS)",
            "version": "1.0.0",
            "database": db_status
        }), 200

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.departments import departments_bp
    from app.routes.semesters import semesters_bp
    from app.routes.students import students_bp
    from app.routes.faculty import faculty_bp
    from app.routes.courses import courses_bp
    from app.routes.classrooms import classrooms_bp
    from app.routes.schedules import schedules_bp
    from app.routes.registrations import registrations_bp
    from app.routes.payments import payments_bp
    from app.routes.attendance import attendance_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(departments_bp, url_prefix="/api/v1/departments")
    app.register_blueprint(semesters_bp, url_prefix="/api/v1/semesters")
    app.register_blueprint(students_bp, url_prefix="/api/v1/students")
    app.register_blueprint(faculty_bp, url_prefix="/api/v1/faculty")
    app.register_blueprint(courses_bp, url_prefix="/api/v1/courses")
    app.register_blueprint(classrooms_bp, url_prefix="/api/v1/classrooms")
    app.register_blueprint(schedules_bp, url_prefix="/api/v1/schedules")
    app.register_blueprint(registrations_bp, url_prefix="/api/v1/registrations")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments")
    app.register_blueprint(attendance_bp, url_prefix="/api/v1/attendance")
    app.register_blueprint(reports_bp, url_prefix="/api/v1/reports")

    return app

from flask import jsonify
from mysql.connector import Error as MySQLError
from app.utils.response import api_response

def register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(error):
        return api_response(
            success=False,
            message=getattr(error, "description", "Bad Request"),
            status_code=400,
            error_code="BAD_REQUEST"
        )
        
    @app.errorhandler(401)
    def unauthorized(error):
        return api_response(
            success=False,
            message=getattr(error, "description", "Authentication required"),
            status_code=401,
            error_code="UNAUTHORIZED"
        )
        
    @app.errorhandler(403)
    def forbidden(error):
        return api_response(
            success=False,
            message=getattr(error, "description", "You do not have permission to access this resource"),
            status_code=403,
            error_code="FORBIDDEN"
        )
        
    @app.errorhandler(404)
    def not_found(error):
        return api_response(
            success=False,
            message=getattr(error, "description", "Requested resource not found"),
            status_code=404,
            error_code="NOT_FOUND"
        )
        
    @app.errorhandler(405)
    def method_not_allowed(error):
        return api_response(
            success=False,
            message="HTTP method not allowed for this endpoint",
            status_code=405,
            error_code="METHOD_NOT_ALLOWED"
        )

    @app.errorhandler(MySQLError)
    def handle_mysql_error(error):
        # Handle MySQL custom signals from triggers / procedures or integrity violations
        msg = str(error)
        errno = getattr(error, 'errno', None)
        
        # Foreign key failure
        if errno == 1451 or errno == 1452:
            return api_response(
                success=False,
                message="Integrity constraint violation: referenced record does not exist or has dependent records.",
                status_code=409,
                error_code="FOREIGN_KEY_VIOLATION"
            )
        # Duplicate entry
        elif errno == 1062:
            return api_response(
                success=False,
                message="Duplicate record: a record with these unique details already exists.",
                status_code=409,
                error_code="DUPLICATE_ENTRY"
            )
        # Custom trigger / signal (1644)
        elif errno == 1644:
            return api_response(
                success=False,
                message=msg,
                status_code=400,
                error_code="BUSINESS_RULE_VIOLATION"
            )
            
        return api_response(
            success=False,
            message=f"Database error: {msg}",
            status_code=500,
            error_code="DATABASE_ERROR"
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        return api_response(
            success=False,
            message=str(error),
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR"
        )

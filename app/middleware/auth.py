from functools import wraps
from flask import request
from flask_jwt_extended import (
    verify_jwt_in_request, 
    get_jwt, 
    get_jwt_identity
)
from app.utils.response import api_response

# In-memory blocklist for revoked JWTs (logout)
revoked_tokens = set()

def role_required(*allowed_roles):
    """
    Decorator to restrict endpoint access by user role ('Admin', 'Faculty', 'Student').
    Returns 401 if token is missing/invalid, 403 if role is not authorized.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                return api_response(
                    success=False,
                    message=str(e),
                    status_code=401,
                    error_code="UNAUTHORIZED"
                )
            
            claims = get_jwt()
            jti = claims.get("jti")
            if jti in revoked_tokens:
                return api_response(
                    success=False,
                    message="Token has been revoked. Please log in again.",
                    status_code=401,
                    error_code="TOKEN_REVOKED"
                )
                
            user_role = claims.get("role")
            if allowed_roles and user_role not in allowed_roles:
                return api_response(
                    success=False,
                    message=f"Access forbidden: requires one of {list(allowed_roles)} roles.",
                    status_code=403,
                    error_code="FORBIDDEN"
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """Retrieve identity and custom claims of currently authenticated JWT."""
    claims = get_jwt()
    return {
        "id": claims.get("user_id", get_jwt_identity()),
        "role": claims.get("role"),
        "email": claims.get("email"),
        "name": claims.get("name"),
        "jti": claims.get("jti")
    }

from flask import jsonify

def api_response(success=True, message="", data=None, status_code=200, error_code=None, pagination=None):
    """
    Standard unified API response structure across CRMS.
    """
    payload = {
        "success": success,
        "message": message
    }
    
    if success:
        if data is not None:
            payload["data"] = data
        if pagination is not None:
            payload["pagination"] = pagination
    else:
        if error_code:
            payload["error_code"] = error_code
        if data is not None:
            payload["details"] = data
            
    return jsonify(payload), status_code

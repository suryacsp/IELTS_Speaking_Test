import os
import jwt
import logging
from functools import wraps
from flask import request, jsonify, g

# Ensure logger is initialized elsewhere
logger = logging.getLogger(__name__)

#User authentication and routes protection
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"AUTH FAILURE: Missing or malformed Authorization header | Path: {request.path} | IP: {request.remote_addr}")
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(
                token,
                os.getenv("JWT_SECRET_KEY"),
                algorithms=["HS256"]
            )
            g.user_id = decoded["user_id"]
            g.user_role = decoded["role"]

        except jwt.ExpiredSignatureError:
            logger.warning(f"AUTH FAILURE: Token expired | Path: {request.path} | IP: {request.remote_addr}")
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            logger.warning(f"AUTH FAILURE: Invalid token | Path: {request.path} | IP: {request.remote_addr}")
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

#Enabling RBAC
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role = getattr(g, 'user_role', None)
            if role != required_role:
                return jsonify({"error": f"Access denied. Required role: {required_role}"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

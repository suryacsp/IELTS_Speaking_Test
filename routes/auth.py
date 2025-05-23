import os 
import jwt
import logging
from datetime import datetime, timedelta, timezone
from models import db, User
from flask import Blueprint, request, jsonify, g
from middleware import token_required
from werkzeug.security import generate_password_hash, check_password_hash


auth_bp = Blueprint('auth', __name__)

# --------------------------
# POST /api/auth/register - user registration
# --------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    role = data.get('role')  # Now mandatory

    # Validate required fields
    if not all([name, email, phone, password, role]):
        return jsonify({"error": "All fields (name, email, phone, password, role) are required"}), 400

    # Validate allowed roles
    allowed_roles = {"admin", "test_taker"}
    if role not in allowed_roles:
        return jsonify({"error": f"Invalid role. Allowed roles are: {', '.join(allowed_roles)}"}), 400

    # Check for Email uniqueness
    if User.query.filter_by(email=email).first():
        logging.warning(f"Registration failed: Duplicate email | email={email}")
        return jsonify({"error": "User with this email already exists"}), 409

    # Check for Phone No. uniqueness
    if User.query.filter_by(phone=phone).first():
        logging.warning(f"Registration failed: Duplicate phone | phone={phone}")
        return jsonify({"error": "User with this phone number already exists"}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, phone=phone, password=hashed_password, role=role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201

# --------------------------
# POST /api/auth/login - user login
# --------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        logging.warning(f"LOGIN FAILED: Missing email or password | email={email} | IP={request.remote_addr}")
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        logging.warning(f"LOGIN FAILED: Invalid credentials | email={email} | IP={request.remote_addr}")
        return jsonify({"error": "Invalid email or password"}), 401

    #If login is successful, generate JWT token
    logging.info(f"LOGIN SUCCESS: email={email} | user_id={user.id} | IP={request.remote_addr}")
    token = generate_jwt(user.id, user.role)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200

def generate_jwt(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Token expiration setting
    }
    secret = os.getenv("JWT_SECRET_KEY")  #check in .env 
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

# --------------------------
# GET /api/auth/profile - get user profile
# --------------------------
@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    user = User.query.get(g.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "created_at": user.created_at.isoformat()
    }), 200




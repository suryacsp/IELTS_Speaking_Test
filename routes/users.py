# routes/users.py
from flask import Blueprint, request, jsonify
import re
from models import db, User
from middleware import token_required,require_role

users_bp = Blueprint('users', __name__)

# --------------------------
# POST /api/users/create - Create a new user
# --------------------------
@users_bp.route('/create', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    # Basic validation
    if not all([name, email, phone]):
        return jsonify({'error': 'name, email, and phone are required'}), 400
    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_pattern, email):
        return jsonify({'error': 'Invalid email format'}), 400
    if not (7 <= len(phone) <= 20):
        return jsonify({'error': 'Phone number must be between 7 and 20 characters'}), 400

    user = User(name=name, email=email, phone=phone)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'created_at': user.created_at.isoformat()
    }), 201

# --------------------------
# GET /api/users/list - List all users
# --------------------------
# This endpoint is protected and requires admin role
@users_bp.route('/list', methods=['GET'])
@token_required
@require_role('admin')
def list_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)
    pagination = User.query.paginate(page=page, per_page=limit, error_out=False)

    users = [
        {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'phone': u.phone,
            'created_at': u.created_at.isoformat()
        }
        for u in pagination.items
    ]

    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page
    }), 200

# --------------------------
# GET /api/users/getuserid/<int:user_id> - Get user by ID
# --------------------------
# This endpoint is protected and requires admin role
@users_bp.route('/getuserid/<int:user_id>', methods=['GET'])
@token_required
@require_role('admin')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'created_at': user.created_at.isoformat()
    }), 200

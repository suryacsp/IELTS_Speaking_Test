# routes/speaking_tests.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, SpeakingTest, User

speaking_tests_bp = Blueprint('speaking_tests', __name__)

# --------------------------
#POST /create_speaking_test
# --------------------------
@speaking_tests_bp.route('/create', methods=['POST'])
def create_speaking_test():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    test_date_str = data.get('test_date')
    status = data.get('status')

    # Validation
    if not all([user_id, test_date_str, status]):
        return jsonify({'error': 'user_id, test_date, and status are required'}), 400
    try:
        test_date = datetime.fromisoformat(test_date_str)
    except ValueError:
        return jsonify({'error': 'test_date must be ISO format'}), 400

    # Ensure user exists
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found'}), 404

    test = SpeakingTest(user_id=user_id, test_date=test_date, status=status)
    db.session.add(test)
    db.session.commit()

    return jsonify({
        'id': test.id,
        'user_id': test.user_id,
        'test_date': test.test_date.isoformat(),
        'status': test.status,
        'score': test.score,
        'created_at': test.created_at.isoformat()
    }), 201

# --------------------------
#GET /speaking_test/testid/<int:test_id>
# --------------------------
@speaking_tests_bp.route('/testid/<int:test_id>', methods=['GET'])
def get_speaking_test(test_id):
    test = SpeakingTest.query.get(test_id)
    if not test:
        return jsonify({'error': 'SpeakingTest not found'}), 404
    return jsonify({
        'id': test.id,
        'user_id': test.user_id,
        'test_date': test.test_date.isoformat(),
        'status': test.status,
        'score': test.score,
        'created_at': test.created_at.isoformat()
    }), 200

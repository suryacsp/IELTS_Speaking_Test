import os
from flask import Flask, jsonify
from flask_migrate import Migrate

from config import Config
from models import db

# Import your blueprints (assumes routes/users.py and routes/speaking_tests.py exist)
from routes.users import users_bp
from routes.speaking_tests import speaking_tests_bp
from routes.questions import questions_bp
from routes.auth import auth_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(speaking_tests_bp, url_prefix='/api/speaking_tests')
    app.register_blueprint(questions_bp, url_prefix='/api/questions')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500

    return app

app = create_app()


# Entry point for local development
if __name__ == '__main__':
    # Optionally override via environment
    env_config = os.getenv('FLASK_CONFIG') or 'default'
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=5000, debug=debug)

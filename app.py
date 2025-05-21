import os
import time
import logging
from flask import Flask, jsonify, request, g
from flask_migrate import Migrate
from config import Config
from models import db

# Import blueprints
from routes.users import users_bp
from routes.speaking_tests import speaking_tests_bp
from routes.questions import questions_bp
from routes.auth import auth_bp

# Logging configuration
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "api.log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(module)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


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

# -- Request start time for response time calculation --
@app.before_request
def start_timer():
    g._start_time = time.time()

# -- Log every incoming request --
@app.before_request
def log_request():
    user_id = getattr(g, "user_id", None)
    method = request.method
    path = request.path
    remote_addr = request.remote_addr
    logging.info(
        f"REQUEST: {method} {path} | User: {user_id} | IP: {remote_addr} | Args: {dict(request.args)} | Body: {request.get_json(silent=True)}"
    )

# -- Log every response with status and timing --
@app.after_request
def log_response(response):
    method = request.method
    path = request.path
    status = response.status_code
    user_id = getattr(g, "user_id", None)
    duration = None
    if hasattr(g, "_start_time"):
        duration = round(time.time() - g._start_time, 3)
    logging.info(
        f"RESPONSE: {method} {path} | Status: {status} | User: {user_id} | Duration: {duration}s"
    )
    return response

# -- Log all unhandled exceptions globally --
@app.errorhandler(Exception)
def log_exception(e):
    import traceback
    method = request.method
    path = request.path
    user_id = getattr(g, "user_id", None)
    logging.error(
        f"EXCEPTION: {method} {path} | User: {user_id} | Error: {e} | Traceback: {traceback.format_exc()}"
    )
    return (
        jsonify({"error": "Internal Server Error"}),
        500,
    )


# Entry point for local development
if __name__ == '__main__':
    # Optionally override via environment
    env_config = os.getenv('FLASK_CONFIG') or 'default'
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    app.run(host='0.0.0.0', port=5000, debug=debug)

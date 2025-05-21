from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    role = db.Column(db.String(50), nullable=False, default='test_taker')  # Role: 'admin' or 'test_taker'
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    speaking_tests = db.relationship('SpeakingTest', backref='user', cascade='all, delete-orphan')

class SpeakingTest(db.Model):
    __tablename__ = 'speaking_tests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

class GeneratedQuestion(db.Model):
    __tablename__ = 'generated_questions'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    question = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

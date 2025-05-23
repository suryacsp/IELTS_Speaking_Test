# IELTS Speaking Test API

This repository provides a Flask-based RESTful API for managing IELTS-style speaking test assignments as part of a training assignment. The system supports user registration and authentication, role-based access control, test scheduling and scoring, and AI-powered generation of speaking questions.

## Features

- **User Management**: Registration, login, and listing of users with support for roles (admin, test_taker).
- **Authentication & Authorization**: JWT-based authentication; endpoints protected by role (admin/test_taker).
- **Speaking Test Management**: Schedule, track, and score speaking tests for users.
- **AI Question Generation**: Admins can generate IELTS-style speaking questions using Azure OpenAI integration.
- **Question Retrieval**: Fetch paginated and recent questions, both synchronously and asynchronously.
- **Logging**: Detailed request and response logging for debugging and audit.
- **Database Migrations**: Uses Alembic for tracking schema changes.

## Technology Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Migrate
- **Database**: Configurable via SQLALCHEMY_DATABASE_URI (supports PostgreSQL, MySQL, etc.)
- **Authentication**: JWT (JSON Web Tokens)
- **AI Integration**: Azure OpenAI API
- **Migrations**: Alembic

## API Endpoints

### Authentication

- `POST /api/auth/register` — Register a new user (admin or test_taker)
- `POST /api/auth/login` — Login and obtain JWT token

### Users

- `POST /api/users/create` — Create a user (basic info)
- `GET /api/users/list` — List all users (**admin only**)
- `GET /api/users/getuserid/<user_id>` — Retrieve user by ID (**admin only**)

### Speaking Tests

- Endpoints for speaking test creation, management, and scoring (see source code)

### Questions

- `GET /api/questions/get-questions-sync` — List all generated questions (sync)
- `GET /api/questions/get-questions-async` — List all generated questions (async)
- `GET /api/questions/get-question-pages?page=1&limit=10` — Paginated question retrieval
- `POST /api/questions/generate-question` — Generate a new IELTS-style question using AI (**admin only**)

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/suryacsp/IELTS_Speaking_Test.git
   cd IELTS_Speaking_Test
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```
   DATABASE_URI=your_database_uri
   JWT_SECRET_KEY=your_jwt_secret_key
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   ```

4. Run database migrations:
   ```bash
   flask db upgrade
   ```

5. Start the application:
   ```bash
   flask run
   ```

## Folder Structure

- `app.py` — Application entry point and app factory
- `models.py` — SQLAlchemy data models (User, SpeakingTest, GeneratedQuestion)
- `routes/` — Blueprints for users, authentication, speaking tests, and questions
- `middleware.py` — JWT authentication and role-based access control decorators
- `migrations/` — Alembic migration scripts

## Notes

- This project is intended for educational and assignment purposes.
- For detailed API usage, refer to the docstrings and code in the `routes/` directory.
- Logging is enabled and will write logs to the `logs/api.log` file.


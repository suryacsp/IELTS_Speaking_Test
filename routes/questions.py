import asyncio
from flask import Blueprint, request, jsonify, current_app
from models import db, GeneratedQuestion
from openai import AzureOpenAI
import httpx
import os
from dotenv import load_dotenv
from middleware import token_required, require_role

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-12-01-preview"
    )


questions_bp = Blueprint('questions', __name__)

# --------------------------
# GET /api/questions/ (sync)
# --------------------------
@questions_bp.route('/get-questions-sync', methods=['GET'])
def get_mock_questions_sync():
    questions = fetch_questions_from_db()  # Direct call, no async

    return jsonify({
        "questions": [
            {"id": q.id, "topic": q.topic, "question": q.question, "created_at": q.created_at.isoformat()}
            for q in questions
        ]
    })



# --------------------------
# GET /api/questions (async)
# --------------------------
@questions_bp.route('/get-questions-async', methods=['GET'])
async def get_mock_questions():
    # Fetch questions using a blocking DB call safely in async route
    questions = await asyncio.to_thread(fetch_questions_from_db)

    return jsonify({
        "questions": [
            {"id": q.id, "topic": q.topic, "question": q.question, "created_at": q.created_at.isoformat()}
            for q in questions
        ]
    })

# Synchronous DB fetcher
def fetch_questions_from_db():
    return GeneratedQuestion.query.order_by(GeneratedQuestion.created_at.desc()).all()

# --------------------------
# GET /api/questions/ (with pagination)
# --------------------------

@questions_bp.route('/get-question-pages', methods=['GET'])
async def get_questions_pages():
    # Read pagination params
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Offload DB fetch to thread
    questions, total = await asyncio.to_thread(fetch_question_pages_from_db, page, limit)

    pages = (total + limit - 1) // limit  # ceil division for total pages

    return jsonify({
        "questions": [
            {
                "id": q.id,
                "topic": q.topic,
                "question": q.question,
                "created_at": q.created_at.isoformat()
            }
            for q in questions
        ],
        "total": total,
        "pages": pages,
        "page": page
    }), 200

def fetch_question_pages_from_db(page, limit):
    # Query ordered by most recent
    query = GeneratedQuestion.query.order_by(GeneratedQuestion.created_at.desc())
    total = query.count()
    questions = query.offset((page - 1) * limit).limit(limit).all()
    return questions, total


# --------------------------
# POST /api/generate-question 
# --------------------------
@questions_bp.route('/generate-question', methods=['POST'])
@token_required
@require_role('admin')
def generate_question():
    data = request.get_json()
    topic = data.get("topic")
    
    if not topic:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=[
                {"role": "system", "content": "You are an IELTS speaking examiner."},
                {"role": "user", "content": f"Generate a speaking test question about: {topic}"}
            ],
            max_tokens=200,
            temperature=0.7
            #top_p=1.0
        )

        question = response.choices[0].message.content

        # Save to DB
        new_entry = GeneratedQuestion(topic=topic, question=question)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"question": question}), 200

    except Exception as e:
        return jsonify({"error": "Azure OpenAI call failed", "details": str(e)}), 500
    
@questions_bp.route('/generate-questions', methods=['POST'])
@token_required
@require_role('admin')
def generate_questions():
    data = request.get_json()
    topics = data.get("topics")  # Expecting a list of topics

    if not topics or not isinstance(topics, list) or not all(isinstance(t, str) for t in topics):
        return jsonify({"error": "Request body must include 'topics' as a list of strings"}), 400

    generated = []
    errors = []

    for topic in topics:
        try:
            response = client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[
                    {"role": "system", "content": "You are an IELTS speaking examiner."},
                    {"role": "user", "content": f"Generate a speaking test question about: {topic}"}
                ],
                max_tokens=200,
                temperature=0.7
            )

            question = response.choices[0].message.content

            # Save to DB
            new_entry = GeneratedQuestion(topic=topic, question=question)
            db.session.add(new_entry)
            db.session.commit()

            generated.append({"topic": topic, "question": question})

        except Exception as e:
            errors.append({"topic": topic, "error": str(e)})

    response_payload = {"generated": generated}
    if errors:
        response_payload["errors"] = errors

    return jsonify(response_payload), 200 if not errors else 207  # 207: Multi-Status if partial failure

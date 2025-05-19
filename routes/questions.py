import asyncio
from flask import Blueprint, request, jsonify, current_app
from models import db, GeneratedQuestion
from openai import AzureOpenAI
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-12-01-preview"
    )


questions_bp = Blueprint('questions', __name__)


# --------------------------
# GET /api/questions (async)
# --------------------------
@questions_bp.route('/get-questions', methods=['GET'])
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
# POST /api/generate-question (async)
# --------------------------
@questions_bp.route('/generate-question', methods=['POST'])
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
            max_tokens=150,
            temperature=0.7,
            top_p=1.0
        )

        question = response.choices[0].message.content

        # Save to DB (optional)
        new_entry = GeneratedQuestion(topic=topic, question=question)
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"question": question}), 200

    except Exception as e:
        return jsonify({"error": "Azure OpenAI call failed", "details": str(e)}), 500
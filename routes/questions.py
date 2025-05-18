import asyncio
from flask import Blueprint, request, jsonify, current_app
from models import db, GeneratedQuestion
import httpx
import os

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
async def generate_question():
    data = request.get_json()
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    try:
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-4-scout:free",  # or any other model you want
            #"model": "qwen/qwen3-8b:free",
            "messages": [
                {"role": "system", "content": "You are an IELTS speaking examiner."},
                {"role": "user", "content": f"Generate a speaking test question about: {topic}"}
            ],
            "max_tokens": 150
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        response.raise_for_status()
        generated_question = response.json()["choices"][0]["message"]["content"]

        await asyncio.to_thread(save_question_to_db, topic, generated_question)

        return jsonify({"question": generated_question})

    except httpx.HTTPStatusError as http_err:
        return jsonify({"error": "OpenRouter API call failed", "details": str(http_err)}), 502
    except Exception as e:
        return jsonify({"error": "Internal error during question generation", "details": str(e)}), 500



# Sync function for DB insert
def save_question_to_db(topic, question):
    new_entry = GeneratedQuestion(topic=topic, question=question)
    db.session.add(new_entry)
    db.session.commit()

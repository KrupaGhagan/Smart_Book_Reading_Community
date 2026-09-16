import os
import google.generativeai as genai

from config.database import db
from models.book_model import Book

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)


def ai_recommendation_service(user_id, preferences=None):
    books = Book.query.limit(5).all()
    if not books:
        return {"message": "No books available"}, 404

    prompt = "Generate five thoughtful book recommendations for a social reading platform user. "
    if preferences:
        prompt += f"The user likes: {preferences}. "
    prompt += "Use only general book themes and keep the suggestions concise."

    try:
        response = genai.generate_text(
            model="text-bison-001",
            input=prompt,
            max_output_tokens=250,
        )
        suggestion_text = response.text if hasattr(response, "text") else str(response)
    except Exception:
        suggestion_text = (
            "Please configure GOOGLE_API_KEY or install the Google Generative AI package. "
            "In the meantime, browse the top rated books from the collection."
        )

    return {
        "recommendations": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "average_rating": book.average_rating,
            }
            for book in books
        ],
        "ai_note": suggestion_text,
    }, 200

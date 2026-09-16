from flask import Blueprint, request, jsonify
from middleware.jwt_middleware import token_required
from services.review_service import add_review_service, list_reviews_service

review_bp = Blueprint("review_bp", __name__)

@review_bp.route("/", methods=["POST"])
@token_required
def add_review():
    """
    Add a review for a book.
    ---
    tags:
      - Reviews
    summary: Add a review
    consumes:
      - application/json
    parameters:
      - in: body
        name: review
        schema:
          type: object
          properties:
            book_id:
              type: integer
            rating:
              type: integer
            comment:
              type: string
          required:
            - book_id
            - rating
    responses:
      200:
        description: Review created successfully
    """
    response, status = add_review_service(request.json, request.user_id)
    return jsonify(response), status

@review_bp.route("/", methods=["GET"])
def get_reviews():
    """
    Get reviews for a book.
    ---
    tags:
      - Reviews
    summary: List reviews
    parameters:
      - name: book_id
        in: query
        type: integer
        description: Optional book ID to filter reviews
    responses:
      200:
        description: Reviews returned successfully
    """
    book_id = request.args.get("book_id", type=int)
    response = list_reviews_service(book_id)
    return jsonify(response), 200

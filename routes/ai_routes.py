from flask import Blueprint, request, jsonify
from middleware.jwt_middleware import token_required
from services.ai_service import ai_recommendation_service

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/recommendations", methods=["GET"])
@token_required
def ai_recommendations():
    """
    Get AI-driven book recommendations.
    ---
    tags:
      - AI
    summary: Fetch AI recommendations
    parameters:
      - name: preferences
        in: query
        type: string
        description: Optional user preferences
    responses:
      200:
        description: AI recommendations returned
    """
    preferences = request.args.get("preferences")
    response, status = ai_recommendation_service(request.user_id, preferences)
    return jsonify(response), status

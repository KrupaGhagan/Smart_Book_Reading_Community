from flask import Blueprint, request, jsonify
from middleware.jwt_middleware import token_required
from services.activity_service import list_activity_service

activity_bp = Blueprint("activity_bp", __name__)

@activity_bp.route("/", methods=["GET"])
@token_required
def list_activity():
    """
    List activity logs for the authenticated user.
    ---
    tags:
      - Activity
    summary: List activity logs
    parameters:
      - name: group_id
        in: query
        type: integer
        description: Optional group filter
      - name: book_id
        in: query
        type: integer
        description: Optional book filter
    responses:
      200:
        description: Activity logs returned successfully
    """
    group_id = request.args.get("group_id", type=int)
    book_id = request.args.get("book_id", type=int)
    response = list_activity_service(user_id=request.user_id, group_id=group_id, book_id=book_id)
    return jsonify(response), 200

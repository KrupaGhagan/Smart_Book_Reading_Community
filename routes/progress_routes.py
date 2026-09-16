from flask import Blueprint, request, jsonify, redirect, url_for
from middleware.jwt_middleware import token_required, decode_token
from services.progress_service import track_progress_service, list_progress_service

progress_bp = Blueprint("progress_bp", __name__)

@progress_bp.route("/", methods=["POST"])
@token_required
def track_progress():
    """
    Track reading progress for the authenticated user.
    ---
    tags:
      - Progress
    summary: Track user progress
    consumes:
      - application/json
    parameters:
      - in: body
        name: progress
        schema:
          type: object
          properties:
            book_id:
              type: integer
            current_page:
              type: integer
            status:
              type: string
          required:
            - book_id
            - current_page
    responses:
      200:
        description: Progress tracked successfully
    """
    response, status = track_progress_service(request.json, request.user_id)
    return jsonify(response), status

@progress_bp.route("/", methods=["GET"])
def get_progress():
    """
    Get the authenticated user’s reading progress.
    ---
    tags:
      - Progress
    summary: List progress entries
    responses:
      200:
        description: Progress list returned successfully
    """
    if request.args.get('json') != '1' and request.accept_mimetypes.accept_html:
        return redirect(url_for('progress_page'))

    token_data, error = decode_token()
    if error:
        return jsonify(error[0]), error[1]

    request.user_id = token_data["user_id"]
    response = list_progress_service(request.user_id)
    return jsonify(response), 200

import os
from uuid import uuid4

from flask import Blueprint, current_app, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from middleware.jwt_middleware import token_required, decode_token
from services.group_service import (
    approve_join_request_service,
    create_group_chat_message_service,
    create_group_service,
    create_reading_session_service,
    join_group_service,
    list_group_chat_messages_service,
    list_groups_service,
    list_reading_sessions_service,
    get_group_details_service,
    update_reading_session_page_service,
)
from services.discussion_service import create_group_post_service, list_group_posts_service
from models.group_model import ReadingGroup
from socket_events import socketio

group_bp = Blueprint("group_bp", __name__)

ALLOWED_CHAT_UPLOADS = {
    "png", "jpg", "jpeg", "gif", "webp",
    "pdf",
    "txt", "md",
}


def _attachment_type(filename):
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension in {"png", "jpg", "jpeg", "gif", "webp"}:
        return "image"
    if extension == "pdf":
        return "pdf"
    if extension in {"txt", "md"}:
        return "note"
    return "file"

@group_bp.route("/", methods=["POST"])
@token_required
def create_group():
    """
    Create a new reading group.
    ---
    tags:
      - Groups
    summary: Create a group
    consumes:
      - application/json
    parameters:
      - in: body
        name: group
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
          required:
            - name
    responses:
      200:
        description: Group created successfully
    """
    response, status = create_group_service(request.json, request.user_id)
    return jsonify(response), status

@group_bp.route("/<int:group_id>/join", methods=["POST"])
@token_required
def join_group(group_id):
    """
    Join an existing reading group.
    ---
    tags:
      - Groups
    summary: Join a group
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
        description: ID of the group to join
    responses:
      200:
        description: Joined the group successfully
    """
    response, status = join_group_service(group_id, request.user_id)
    return jsonify(response), status


@group_bp.route("/<int:group_id>/requests/<int:request_id>/approve", methods=["POST"])
@token_required
def approve_join_request(group_id, request_id):
    response, status = approve_join_request_service(group_id, request_id, request.user_id)
    return jsonify(response), status


@group_bp.route("/<int:group_id>", methods=["GET"])
@token_required
def get_group(group_id):
    """
    Get group details including members.
    ---
    tags:
      - Groups
    summary: Get group details
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
        description: Group ID
    responses:
      200:
        description: Group details returned successfully
    """
    response, status = get_group_details_service(group_id, request.user_id)
    return jsonify(response), status

@group_bp.route("/<int:group_id>/posts", methods=["POST"])
@token_required
def create_group_post(group_id):
    """
    Create a discussion post in a reading group.
    ---
    tags:
      - Groups
      - Discussions
    summary: Add a post to group discussion
    consumes:
      - application/json
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
      - in: body
        name: post
        schema:
          type: object
          properties:
            content:
              type: string
          required:
            - content
    responses:
      200:
        description: Group post created successfully
    """
    response, status = create_group_post_service(group_id, request.user_id, request.json)
    return jsonify(response), status

@group_bp.route("/<int:group_id>/posts", methods=["GET"])
@token_required
def list_group_posts(group_id):
    """
    List discussion posts for a reading group.
    ---
    tags:
      - Groups
      - Discussions
    summary: List group discussion posts
    parameters:
      - name: group_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Group posts returned successfully
    """
    response, status = list_group_posts_service(group_id, request.user_id)
    return jsonify(response), status


@group_bp.route("/<int:group_id>/sessions", methods=["POST"])
@token_required
def create_reading_session(group_id):
    response, status = create_reading_session_service(group_id, request.user_id, request.json or {})
    return jsonify(response), status


@group_bp.route("/<int:group_id>/sessions", methods=["GET"])
@token_required
def list_reading_sessions(group_id):
    response, status = list_reading_sessions_service(group_id, request.user_id)
    return jsonify(response), status


@group_bp.route("/<int:group_id>/sessions/<int:session_id>/page", methods=["PUT"])
@token_required
def update_reading_session_page(group_id, session_id):
    response, status = update_reading_session_page_service(
        group_id,
        session_id,
        request.user_id,
        request.json or {},
    )
    return jsonify(response), status


@group_bp.route("/<int:group_id>/chat", methods=["POST"])
@token_required
def create_group_chat_message(group_id):
    response, status = create_group_chat_message_service(group_id, request.user_id, request.json or {})
    return jsonify(response), status


@group_bp.route("/<int:group_id>/chat/upload", methods=["POST"])
@token_required
def upload_group_chat_attachment(group_id):
    attachment = request.files.get("attachment")
    message = request.form.get("message", "")
    if not attachment or not attachment.filename:
        return jsonify({"message": "Attachment file is required"}), 400

    group = ReadingGroup.query.get(group_id)
    if not group:
        return jsonify({"message": "Group not found"}), 404
    is_member = group.owner_id == request.user_id or any(member.id == request.user_id for member in group.members)
    if not is_member:
        return jsonify({"message": "Must be a group member to upload attachments"}), 403

    original_name = secure_filename(attachment.filename)
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if extension not in ALLOWED_CHAT_UPLOADS:
        return jsonify({"message": "Only images, PDF, txt, and md files are allowed"}), 400

    upload_dir = os.path.join(current_app.static_folder, "uploads", "chat", str(group_id))
    os.makedirs(upload_dir, exist_ok=True)
    stored_name = f"{uuid4().hex}_{original_name}"
    attachment.save(os.path.join(upload_dir, stored_name))

    attachment_url = url_for("static", filename=f"uploads/chat/{group_id}/{stored_name}")
    response, status = create_group_chat_message_service(
        group_id,
        request.user_id,
        {
            "message": message,
            "attachment_url": attachment_url,
            "attachment_name": original_name,
            "attachment_type": _attachment_type(original_name),
        },
    )
    if status < 400:
        socketio.emit("group_message", response["chat"], room=f"group:{group_id}")
    return jsonify(response), status


@group_bp.route("/<int:group_id>/chat", methods=["GET"])
@token_required
def list_group_chat_messages(group_id):
    response, status = list_group_chat_messages_service(group_id, request.user_id)
    return jsonify(response), status


@group_bp.route("/", methods=["GET"])
def list_groups():
    """
    List groups for discovery or membership.
    ---
    tags:
      - Groups
    summary: List groups
    parameters:
      - name: all
        in: query
        type: string
        description: Return all groups for discovery when set to 1
    responses:
      200:
        description: Groups returned successfully
    """
    if request.args.get('json') != '1' and request.accept_mimetypes.accept_html:
        return redirect(url_for('groups_page'))

    all_groups = request.args.get('all') == '1'
    current_user_id = None
    if all_groups and 'Authorization' in request.headers:
        token_data, error = decode_token()
        if error:
            return jsonify(error[0]), error[1]
        current_user_id = token_data.get('user_id')

    if all_groups:
        response = list_groups_service(current_user_id, all_groups=True)
    else:
        if 'Authorization' not in request.headers:
            return jsonify({"message": "Authentication required"}), 401
        token_data, error = decode_token()
        if error:
            return jsonify(error[0]), error[1]
        response = list_groups_service(token_data.get('user_id'))
    return jsonify(response), 200

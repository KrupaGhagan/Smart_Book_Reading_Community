import os

import jwt
from flask_socketio import SocketIO, emit, join_room

from config.database import db
from models.group_model import GroupChatMessage, GroupReadingSession, ReadingGroup
from services.group_service import serialize_chat_message


socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")


def _get_user_id(token):
    if not token:
        return None
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data.get("user_id")
    except Exception:
        return None


def _is_group_member(group, user_id):
    return group and user_id and (
        group.owner_id == user_id or any(member.id == user_id for member in group.members)
    )


def _group_room(group_id):
    return f"group:{group_id}"


@socketio.on("join_group_room")
def handle_join_group_room(data):
    group_id = data.get("group_id")
    user_id = _get_user_id(data.get("token"))
    group = ReadingGroup.query.get(group_id)

    if not _is_group_member(group, user_id):
        emit("room_error", {"message": "You must be a group member to join the live room."})
        return

    join_room(_group_room(group_id))
    emit("room_joined", {"group_id": group_id})


@socketio.on("send_group_message")
def handle_send_group_message(data):
    group_id = data.get("group_id")
    message = (data.get("message") or "").strip()
    user_id = _get_user_id(data.get("token"))
    group = ReadingGroup.query.get(group_id)

    if not message:
        emit("room_error", {"message": "Message is required."})
        return
    if not _is_group_member(group, user_id):
        emit("room_error", {"message": "You must be a group member to chat."})
        return

    chat_message = GroupChatMessage(group_id=group_id, user_id=user_id, message=message)
    db.session.add(chat_message)
    db.session.commit()

    socketio.emit(
        "group_message",
        serialize_chat_message(chat_message),
        room=_group_room(group_id),
    )


@socketio.on("update_group_page")
def handle_update_group_page(data):
    group_id = data.get("group_id")
    session_id = data.get("session_id")
    user_id = _get_user_id(data.get("token"))
    group = ReadingGroup.query.get(group_id)

    if not _is_group_member(group, user_id):
        emit("room_error", {"message": "You must be a group member to update the page."})
        return

    session = GroupReadingSession.query.filter_by(id=session_id, group_id=group_id).first()
    if not session:
        emit("room_error", {"message": "Reading session not found."})
        return

    try:
        page = int(data.get("page", session.current_page or 1))
    except (TypeError, ValueError):
        emit("room_error", {"message": "Page must be a number."})
        return

    session.current_page = min(max(page, 1), session.total_pages or 1)
    db.session.commit()

    socketio.emit(
        "group_page_updated",
        {
            "group_id": group_id,
            "session_id": session.id,
            "current_page": session.current_page,
            "total_pages": session.total_pages or 1,
        },
        room=_group_room(group_id),
    )

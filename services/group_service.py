from datetime import datetime

from config.database import db
from models.book_model import Book
from models.group_model import (
    GroupChatMessage,
    GroupJoinRequest,
    GroupReadingSession,
    ReadingGroup,
)
from models.user_model import User
from services.activity_service import log_activity


def _is_group_member(group, user_id):
    return group.owner_id == user_id or any(member.id == user_id for member in group.members)


def _serialize_member(member):
    return {
        "id": member.id,
        "username": member.username,
        "name": member.name,
    }


def _serialize_join_request(join_request):
    return {
        "id": join_request.id,
        "status": join_request.status,
        "created_at": join_request.created_at.isoformat() if join_request.created_at else None,
        "user": _serialize_member(join_request.user),
    }


def _serialize_session(session):
    book = session.book
    return {
        "id": session.id,
        "title": session.title,
        "book_id": session.book_id,
        "book_title": session.book_title,
        "source_type": session.source_type or "book",
        "source_title": session.source_title,
        "source_content": session.source_content,
        "book": {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "cover_url": book.cover,
            "read_url": book.read_url,
            "genres": book.genres,
        } if book else None,
        "scheduled_at": session.scheduled_at.isoformat() if session.scheduled_at else None,
        "meeting_link": session.meeting_link,
        "notes": session.notes,
        "current_page": session.current_page or 1,
        "total_pages": session.total_pages or 20,
        "owner_id": session.owner_id,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


def create_group_service(data, owner_id):
    name = data.get("name")
    description = data.get("description")
    visibility = data.get("visibility", "public").lower()

    if not name:
        return {"message": "Group name is required"}, 400
    if visibility not in {"public", "private"}:
        return {"message": "Visibility must be public or private"}, 400

    group = ReadingGroup(name=name, description=description, visibility=visibility, owner_id=owner_id)
    db.session.add(group)
    db.session.commit()

    owner = User.query.get(owner_id)
    if owner and owner not in group.members:
        group.members.append(owner)
        db.session.commit()

    log_activity(owner_id, "group", f"Created group '{group.name}'", group_id=group.id)
    return {"message": "Group created", "group_id": group.id}, 201


def join_group_service(group_id, user_id):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404

    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    if user in group.members:
        return {"message": "Already a member"}, 200

    if group.visibility == "private":
        existing_request = GroupJoinRequest.query.filter_by(
            group_id=group_id,
            user_id=user_id,
            status="pending",
        ).first()
        if existing_request:
            return {"message": "Join request already pending", "request_id": existing_request.id}, 200

        join_request = GroupJoinRequest(group_id=group_id, user_id=user_id)
        db.session.add(join_request)
        db.session.commit()
        log_activity(user_id, "group", f"Requested to join private group '{group.name}'", group_id=group.id)
        return {"message": "Join request sent to the owner", "request_id": join_request.id}, 202

    group.members.append(user)
    db.session.commit()
    log_activity(user_id, "group", f"Joined group '{group.name}'", group_id=group.id)
    return {"message": "Joined group", "group_id": group.id}, 200


def approve_join_request_service(group_id, request_id, owner_id):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404
    if group.owner_id != owner_id:
        return {"message": "Only the group owner can approve join requests"}, 403

    join_request = GroupJoinRequest.query.filter_by(id=request_id, group_id=group_id).first()
    if not join_request:
        return {"message": "Join request not found"}, 404
    if join_request.status != "pending":
        return {"message": "Join request is not pending"}, 400

    user = User.query.get(join_request.user_id)
    if not user:
        return {"message": "User not found"}, 404
    if user not in group.members:
        group.members.append(user)

    join_request.status = "approved"
    db.session.commit()
    log_activity(user.id, "group", f"Joined private group '{group.name}'", group_id=group.id)
    return {"message": "Join request approved", "group_id": group.id, "user_id": user.id}, 200


def list_groups_service(user_id=None, all_groups=False):
    query = ReadingGroup.query
    if not all_groups and user_id:
        query = query.filter((ReadingGroup.owner_id == user_id) | (ReadingGroup.members.any(id=user_id)))
    groups = query.all()

    return [
        {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "visibility": group.visibility,
            "owner_id": group.owner_id,
            "owner_name": group.owner.name if group.owner else None,
            "member_count": len(group.members),
            "is_owner": bool(user_id and group.owner_id == user_id),
            "is_member": bool(user_id and _is_group_member(group, user_id)),
            "has_pending_request": bool(user_id and GroupJoinRequest.query.filter_by(
                group_id=group.id,
                user_id=user_id,
                status="pending",
            ).first()),
            "members": [_serialize_member(member) for member in group.members],
            "pending_requests": [
                _serialize_join_request(join_request)
                for join_request in group.join_requests
                if join_request.status == "pending" and user_id == group.owner_id
            ],
            "sessions": [
                _serialize_session(session)
                for session in sorted(group.reading_sessions, key=lambda item: item.scheduled_at)
            ] if user_id and _is_group_member(group, user_id) else [],
        }
        for group in groups
    ]


def get_group_details_service(group_id, user_id=None):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404

    if user_id and user_id != group.owner_id and not any(member.id == user_id for member in group.members):
        return {"message": "Access denied"}, 403

    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "visibility": group.visibility,
        "owner_id": group.owner_id,
        "member_count": len(group.members),
        "is_owner": bool(user_id and group.owner_id == user_id),
        "members": [_serialize_member(member) for member in group.members],
        "pending_requests": [
            _serialize_join_request(join_request)
            for join_request in group.join_requests
            if join_request.status == "pending" and user_id == group.owner_id
        ],
        "sessions": [_serialize_session(session) for session in group.reading_sessions],
    }, 200


def create_reading_session_service(group_id, owner_id, data):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404
    if group.owner_id != owner_id:
        return {"message": "Only the group owner can create reading sessions"}, 403

    title = data.get("title")
    source_type = (data.get("source_type") or "book").lower()
    book_id = data.get("book_id")
    scheduled_at = data.get("scheduled_at")
    if not title or not scheduled_at:
        return {"message": "Session title and scheduled time are required"}, 400
    if source_type not in {"book", "member_notes"}:
        return {"message": "Session source must be book or member_notes"}, 400

    book = None
    source_title = data.get("source_title") or data.get("book_title")
    source_content = data.get("source_content")

    if source_type == "book":
        if not book_id:
            return {"message": "Book is required for a book session"}, 400
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        source_title = book.title
    else:
        source_title = (source_title or title).strip()
        source_content = (source_content or "").strip()
        if not source_content:
            return {"message": "Member notes content is required"}, 400

    try:
        scheduled_at_value = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except ValueError:
        return {"message": "scheduled_at must be a valid date/time"}, 400

    total_pages = data.get("total_pages") or 20
    try:
        total_pages = max(1, int(total_pages))
    except (TypeError, ValueError):
        total_pages = 20

    session = GroupReadingSession(
        group_id=group_id,
        owner_id=owner_id,
        title=title,
        book_id=book.id if book else None,
        book_title=(data.get("book_title") or book.title) if book else source_title,
        source_type=source_type,
        source_title=source_title,
        source_content=source_content,
        scheduled_at=scheduled_at_value,
        meeting_link=data.get("meeting_link"),
        notes=data.get("notes"),
        current_page=1,
        total_pages=total_pages,
    )
    db.session.add(session)
    db.session.commit()
    log_activity(owner_id, "group", f"Scheduled reading session '{session.title}'", group_id=group.id)
    return {"message": "Reading session created", "session": _serialize_session(session)}, 201


def list_reading_sessions_service(group_id, user_id):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404
    if not _is_group_member(group, user_id):
        return {"message": "Must be a group member to view sessions"}, 403

    sessions = GroupReadingSession.query.filter_by(group_id=group_id).order_by(GroupReadingSession.scheduled_at.asc()).all()
    return [_serialize_session(session) for session in sessions], 200


def update_reading_session_page_service(group_id, session_id, user_id, data):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404

    if not _is_group_member(group, user_id):
        return {"message": "Must be a group member to update the reading page"}, 403

    session = GroupReadingSession.query.filter_by(id=session_id, group_id=group_id).first()
    if not session:
        return {"message": "Reading session not found"}, 404

    try:
        page = int(data.get("page", session.current_page or 1))
    except (TypeError, ValueError):
        return {"message": "Page must be a number"}, 400

    session.current_page = min(max(page, 1), session.total_pages or 1)
    db.session.commit()
    return {"message": "Reading page updated", "session": _serialize_session(session)}, 200


def create_group_chat_message_service(group_id, user_id, data):
    message = (data.get("message") or "").strip()
    attachment_url = data.get("attachment_url")
    attachment_name = data.get("attachment_name")
    attachment_type = data.get("attachment_type")
    if not message and not attachment_url:
        return {"message": "Message or attachment is required"}, 400

    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404
    if not _is_group_member(group, user_id):
        return {"message": "Must be a group member to chat"}, 403

    chat_message = GroupChatMessage(
        group_id=group_id,
        user_id=user_id,
        message=message,
        attachment_url=attachment_url,
        attachment_name=attachment_name,
        attachment_type=attachment_type,
    )
    db.session.add(chat_message)
    db.session.commit()
    return {"message": "Chat message sent", "chat": serialize_chat_message(chat_message)}, 201


def list_group_chat_messages_service(group_id, user_id):
    group = ReadingGroup.query.get(group_id)
    if not group:
        return {"message": "Group not found"}, 404
    if not _is_group_member(group, user_id):
        return {"message": "Must be a group member to view chat"}, 403

    messages = GroupChatMessage.query.filter_by(group_id=group_id).order_by(GroupChatMessage.created_at.asc()).all()
    return [serialize_chat_message(message) for message in messages], 200


def serialize_chat_message(chat_message):
    return {
        "id": chat_message.id,
        "group_id": chat_message.group_id,
        "user_id": chat_message.user_id,
        "author_name": chat_message.author.name or chat_message.author.username,
        "message": chat_message.message,
        "attachment_url": chat_message.attachment_url,
        "attachment_name": chat_message.attachment_name,
        "attachment_type": chat_message.attachment_type,
        "created_at": chat_message.created_at.isoformat() if chat_message.created_at else None,
    }

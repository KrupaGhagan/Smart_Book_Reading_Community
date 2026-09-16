from config.database import db
from models.activity_model import ActivityLog


def log_activity(user_id, event_type, message, book_id=None, group_id=None):
    log = ActivityLog(
        user_id=user_id,
        event_type=event_type,
        message=message,
        book_id=book_id,
        group_id=group_id,
    )
    db.session.add(log)
    db.session.commit()
    return log


def list_activity_service(user_id=None, group_id=None, book_id=None):
    query = ActivityLog.query.order_by(ActivityLog.created_at.desc())
    if user_id is not None:
        query = query.filter(ActivityLog.user_id == user_id)
    if group_id is not None:
        query = query.filter(ActivityLog.group_id == group_id)
    if book_id is not None:
        query = query.filter(ActivityLog.book_id == book_id)

    logs = query.all()
    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "message": log.message,
            "user_id": log.user_id,
            "book_id": log.book_id,
            "group_id": log.group_id,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]

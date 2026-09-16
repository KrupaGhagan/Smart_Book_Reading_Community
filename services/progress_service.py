from config.database import db
from models.progress_model import Progress
from models.book_model import Book
from services.activity_service import log_activity


def track_progress_service(data, user_id):
    book_id = data.get("book_id")
    current_page = data.get("current_page", 0)
    total_pages = data.get("total_pages")
    status = data.get("status", "reading")

    if not book_id:
        return {"message": "book_id is required"}, 400

    progress = Progress.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not progress:
        progress = Progress(
            user_id=user_id,
            book_id=book_id,
            current_page=current_page,
            total_pages=total_pages,
            status=status,
        )
        db.session.add(progress)
    else:
        progress.current_page = current_page
        progress.total_pages = total_pages or progress.total_pages
        progress.status = status
    db.session.commit()

    book = Book.query.get(book_id)
    log_activity(user_id, "progress", f"Updated reading progress for '{book.title if book else 'book'}'", book_id=book_id)
    return {"message": "Progress updated", "progress_id": progress.id}, 200


def list_progress_service(user_id):
    records = Progress.query.filter_by(user_id=user_id).all()
    return [
        {
            "id": entry.id,
            "book_id": entry.book_id,
            "current_page": entry.current_page,
            "total_pages": entry.total_pages,
            "status": entry.status,
            "last_read": entry.last_read.isoformat() if entry.last_read else None,
        }
        for entry in records
    ]

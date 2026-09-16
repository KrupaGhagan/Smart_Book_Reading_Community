import os
import requests
from sqlalchemy import func, select

from config.database import db
from models.book_model import Book, reading_lists
from models.review_model import Review
from models.user_model import User
from services.activity_service import log_activity

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"


def add_book_service(data):
    title = data.get("title")
    author = data.get("author")
    isbn = data.get("isbn")
    description = data.get("description")
    genres = data.get("genres")

    if not title or not author:
        return {"message": "title and author are required"}, 400

    book = Book(
        title=title,
        author=author,
        description=description,
        isbn=isbn,
        genres=genres,
    )
    db.session.add(book)
    db.session.commit()

    return {"message": "Book added", "book_id": book.id}, 201


def get_cover_url(book):
    if book.cover and isinstance(book.cover, str) and book.cover.startswith(("http://", "https://")):
        return book.cover
    if book.isbn:
        isbn = book.isbn.replace("-", "").strip()
        if isbn:
            return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
    return None


def list_books_service(query=None):
    if query:
        books = Book.query.filter(
            Book.title.ilike(f"%{query}%")
            | Book.author.ilike(f"%{query}%")
            | Book.genres.ilike(f"%{query}%")
        ).all()
    else:
        books = Book.query.order_by(Book.title).all()

    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "isbn": book.isbn,
            "genres": book.genres,
            "cover": book.cover,
            "cover_url": get_cover_url(book),
            "read_url": book.read_url,
            "average_rating": book.average_rating,
        }
        for book in books
    ]


def get_book_service(book_id):
    book = Book.query.get(book_id)
    if not book:
        return None, 404

    reviews = [
        {"rating": r.rating, "comment": r.comment, "user_id": r.user_id}
        for r in book.reviews
    ]

    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "isbn": book.isbn,
        "genres": book.genres,
        "cover": book.cover,
        "cover_url": get_cover_url(book),
        "read_url": book.read_url,
        "average_rating": book.average_rating,
        "reviews": reviews,
    }, 200


def search_external_books_service(query):
    if not query:
        return [], 400

    params = {"q": query, "limit": 10}
    response = requests.get(OPEN_LIBRARY_URL, params=params)
    if response.status_code != 200:
        return [], 502

    results = response.json().get("docs", [])
    return [
        {
            "title": item.get("title"),
            "author": ", ".join(item.get("author_name", [])) if item.get("author_name") else None,
            "publish_year": item.get("first_publish_year"),
            "isbn": item.get("isbn", [None])[0],
        }
        for item in results
    ], 200


def recommend_books_for_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    top_books = (
        Book.query
        .join(Review, Review.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.avg(Review.rating).desc())
        .limit(5)
        .all()
    )

    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "cover": book.cover,
            "read_url": book.read_url,
            "average_rating": book.average_rating,
            "status": _get_user_reading_status(user_id, book.id),
        }
        for book in top_books
    ], 200


def _get_user_reading_status(user_id, book_id):
    row = db.session.execute(
        select(reading_lists.c.status)
        .where(reading_lists.c.user_id == user_id)
        .where(reading_lists.c.book_id == book_id)
    ).first()
    return row[0] if row else None


def add_book_to_list_service(data, user_id):
    book_id = data.get("book_id")
    status = data.get("status", "to-read")

    if not book_id:
        return {"message": "book_id is required"}, 400

    book = Book.query.get(book_id)
    if not book:
        return {"message": "Book not found"}, 404

    existing = db.session.execute(
        select(reading_lists)
        .where(reading_lists.c.user_id == user_id)
        .where(reading_lists.c.book_id == book_id)
    ).first()

    if existing:
        db.session.execute(
            reading_lists.update()
            .where(reading_lists.c.user_id == user_id)
            .where(reading_lists.c.book_id == book_id)
            .values(status=status)
        )
        message = "Reading list status updated"
        status_code = 200
    else:
        db.session.execute(
            reading_lists.insert().values(user_id=user_id, book_id=book_id, status=status)
        )
        message = "Book added to reading list"
        status_code = 201

    db.session.commit()
    log_activity(user_id, "reading_list", f"{message} for '{book.title}'", book_id=book_id)

    return {"message": message, "book_id": book_id, "status": status}, status_code


def list_reading_list_service(user_id, status=None):
    query = select(reading_lists.c.book_id, reading_lists.c.status).where(reading_lists.c.user_id == user_id)
    if status:
        query = query.where(reading_lists.c.status == status)

    rows = db.session.execute(query).fetchall()
    if not rows:
        return []

    book_map = {row.book_id: row.status for row in rows}
    books = Book.query.filter(Book.id.in_(list(book_map.keys()))).all()

    return [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "isbn": book.isbn,
            "genres": book.genres,
            "cover": book.cover,
            "cover_url": get_cover_url(book),
            "read_url": book.read_url,
            "average_rating": book.average_rating,
            "status": book_map.get(book.id),
        }
        for book in books
    ]


def remove_book_from_list_service(user_id, book_id):
    row = db.session.execute(
        select(reading_lists)
        .where(reading_lists.c.user_id == user_id)
        .where(reading_lists.c.book_id == book_id)
    ).first()
    if not row:
        return {"message": "Entry not found in reading list"}, 404

    db.session.execute(
        reading_lists.delete()
        .where(reading_lists.c.user_id == user_id)
        .where(reading_lists.c.book_id == book_id)
    )
    db.session.commit()
    return {"message": "Book removed from reading list"}, 200

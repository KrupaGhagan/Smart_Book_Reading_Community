from config.database import db
from models.book_model import Book
from models.review_model import Review
from models.user_model import User
from services.activity_service import log_activity


def add_review_service(data, user_id):
    book_id = data.get("book_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not book_id or rating is None:
        return {"message": "book_id and rating are required"}, 400

    book = Book.query.get(book_id)
    if not book:
        return {"message": "Book not found"}, 404

    review = Review(
        rating=rating,
        comment=comment,
        user_id=user_id,
        book_id=book_id,
    )
    db.session.add(review)
    db.session.commit()

    reviews = Review.query.filter_by(book_id=book_id).all()
    if reviews:
        book.average_rating = sum(r.rating for r in reviews) / len(reviews)
        db.session.commit()

    log_activity(user_id, "review", f"Published a review for '{book.title}'", book_id=book_id)
    return {"message": "Review added", "review_id": review.id}, 201


def list_reviews_service(book_id=None):
    if book_id:
        reviews = Review.query.filter_by(book_id=book_id).all()
    else:
        reviews = Review.query.order_by(Review.created_at.desc()).all()

    return [
        {
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment,
            "user_id": review.user_id,
            "book_id": review.book_id,
            "created_at": review.created_at.isoformat(),
        }
        for review in reviews
    ]

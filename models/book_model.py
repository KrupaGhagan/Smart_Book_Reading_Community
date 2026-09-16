from config.database import db

reading_lists = db.Table(
    "reading_lists",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("book_id", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("status", db.String(50), default="to-read"),
)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    genres = db.Column(db.String(255), nullable=True)
    cover = db.Column(db.String(255), nullable=True)
    read_url = db.Column(db.String(2048), nullable=True)
    average_rating = db.Column(db.Float, default=0.0)

    reviews = db.relationship("Review", backref="book", lazy=True)
    progress = db.relationship("Progress", backref="book", lazy=True)

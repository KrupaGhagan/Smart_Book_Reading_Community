from config.database import db


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    current_page = db.Column(db.Integer, default=0)
    total_pages = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default="reading")
    last_read = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)

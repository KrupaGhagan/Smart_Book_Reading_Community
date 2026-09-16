from config.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    provider = db.Column(db.String(50), default="local")

    reviews = db.relationship("Review", backref="user", lazy=True)
    books = db.relationship("Book", secondary="reading_lists", backref="users", lazy="dynamic")
    progress = db.relationship("Progress", backref="user", lazy=True)

from config.database import db


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(80), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("reading_groups.id"), nullable=True)

    user = db.relationship("User", backref="activity_logs", lazy=True)
    book = db.relationship("Book", backref="activity_logs", lazy=True)
    group = db.relationship("ReadingGroup", backref="activity_logs", lazy=True)

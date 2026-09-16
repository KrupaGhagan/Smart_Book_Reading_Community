from config.database import db


class DiscussionPost(db.Model):
    __tablename__ = "group_posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    group_id = db.Column(db.Integer, db.ForeignKey("reading_groups.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    group = db.relationship("ReadingGroup", backref="posts", lazy=True)
    author = db.relationship("User", backref="group_posts", lazy=True)

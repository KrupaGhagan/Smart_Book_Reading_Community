from config.database import db


group_membership = db.Table(
    "group_membership",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("group_id", db.Integer, db.ForeignKey("reading_groups.id"), primary_key=True),
)


class ReadingGroup(db.Model):
    __tablename__ = "reading_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    visibility = db.Column(db.String(20), nullable=False, default="public")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", backref="owned_groups", foreign_keys=[owner_id], lazy=True)
    members = db.relationship("User", secondary=group_membership, backref="member_groups")


class GroupJoinRequest(db.Model):
    __tablename__ = "group_join_requests"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    group_id = db.Column(db.Integer, db.ForeignKey("reading_groups.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    group = db.relationship("ReadingGroup", backref="join_requests", lazy=True)
    user = db.relationship("User", backref="group_join_requests", lazy=True)


class GroupReadingSession(db.Model):
    __tablename__ = "group_reading_sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=True)
    book_title = db.Column(db.String(255), nullable=True)
    source_type = db.Column(db.String(30), nullable=False, default="book")
    source_title = db.Column(db.String(255), nullable=True)
    source_content = db.Column(db.Text, nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    meeting_link = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    current_page = db.Column(db.Integer, nullable=False, default=1)
    total_pages = db.Column(db.Integer, nullable=False, default=20)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    group_id = db.Column(db.Integer, db.ForeignKey("reading_groups.id"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    group = db.relationship("ReadingGroup", backref="reading_sessions", lazy=True)
    owner = db.relationship("User", backref="created_reading_sessions", lazy=True)
    book = db.relationship("Book", backref="group_reading_sessions", lazy=True)


class GroupChatMessage(db.Model):
    __tablename__ = "group_chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False, default="")
    attachment_url = db.Column(db.String(500), nullable=True)
    attachment_name = db.Column(db.String(255), nullable=True)
    attachment_type = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    group_id = db.Column(db.Integer, db.ForeignKey("reading_groups.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    group = db.relationship("ReadingGroup", backref="chat_messages", lazy=True)
    author = db.relationship("User", backref="group_chat_messages", lazy=True)

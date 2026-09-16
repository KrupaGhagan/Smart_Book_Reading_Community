from flask_sqlalchemy import SQLAlchemy

from flask import current_app


db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _upgrade_existing_sqlite_schema(app)


def _upgrade_existing_sqlite_schema(app):
    if not app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
        return

    with db.engine.connect() as connection:
        group_columns = [row[1] for row in connection.exec_driver_sql("PRAGMA table_info(reading_groups)").fetchall()]
        if "visibility" not in group_columns:
            connection.exec_driver_sql(
                "ALTER TABLE reading_groups ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'public'"
            )

        session_columns = [
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(group_reading_sessions)").fetchall()
        ]
        session_upgrades = {
            "book_id": "ALTER TABLE group_reading_sessions ADD COLUMN book_id INTEGER",
            "source_type": "ALTER TABLE group_reading_sessions ADD COLUMN source_type VARCHAR(30) NOT NULL DEFAULT 'book'",
            "source_title": "ALTER TABLE group_reading_sessions ADD COLUMN source_title VARCHAR(255)",
            "source_content": "ALTER TABLE group_reading_sessions ADD COLUMN source_content TEXT",
            "current_page": "ALTER TABLE group_reading_sessions ADD COLUMN current_page INTEGER NOT NULL DEFAULT 1",
            "total_pages": "ALTER TABLE group_reading_sessions ADD COLUMN total_pages INTEGER NOT NULL DEFAULT 20",
        }
        for column, statement in session_upgrades.items():
            if column not in session_columns:
                connection.exec_driver_sql(statement)

        chat_columns = [
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(group_chat_messages)").fetchall()
        ]
        chat_upgrades = {
            "attachment_url": "ALTER TABLE group_chat_messages ADD COLUMN attachment_url VARCHAR(500)",
            "attachment_name": "ALTER TABLE group_chat_messages ADD COLUMN attachment_name VARCHAR(255)",
            "attachment_type": "ALTER TABLE group_chat_messages ADD COLUMN attachment_type VARCHAR(30)",
        }
        for column, statement in chat_upgrades.items():
            if column not in chat_columns:
                connection.exec_driver_sql(statement)

        connection.commit()

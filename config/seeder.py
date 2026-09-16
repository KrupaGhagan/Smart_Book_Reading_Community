import json
import os
import re

from config.database import db
from models.book_model import Book


def _load_books_from_js(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    def strip_js_comments(text):
        result = []
        in_string = False
        string_char = None
        escape = False
        i = 0
        while i < len(text):
            char = text[i]
            if in_string:
                result.append(char)
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == string_char:
                    in_string = False
                i += 1
                continue

            if char in ('"', "'"):
                in_string = True
                string_char = char
                result.append(char)
                i += 1
                continue

            if char == "/" and i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == "/":
                    # Skip single-line comment
                    i += 2
                    while i < len(text) and text[i] != "\n":
                        i += 1
                    continue
                if next_char == "*":
                    # Skip block comment
                    i += 2
                    while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                        i += 1
                    i += 2
                    continue

            result.append(char)
            i += 1

        return "".join(result)

    content = strip_js_comments(content)

    # Extract the array literal
    start = content.find("[")
    end = content.rfind("]")
    if start == -1 or end == -1:
        return []

    content = content[start : end + 1]

    # Remove trailing commas to make valid JSON
    content = re.sub(r",\s*(?=[}\]])", "", content)

    return json.loads(content)


def seed_books(app):
    data_file = os.path.join(app.root_path, "static", "data", "booksData.js")
    books = _load_books_from_js(data_file)

    with app.app_context():
        if Book.query.count() > 0:
            return

        for item in books:
            book = Book(
                title=item.get("title"),
                author=item.get("author"),
                description=item.get("description"),
                isbn=item.get("isbn"),
                genres=item.get("genres") or item.get("category") or item.get("subject"),
                cover=item.get("cover"),
                read_url=item.get("readUrl"),
            )
            db.session.add(book)

        db.session.commit()

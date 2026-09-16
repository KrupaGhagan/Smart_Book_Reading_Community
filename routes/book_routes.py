from flask import Blueprint, request, jsonify, redirect, url_for
from middleware.jwt_middleware import token_required
from services.book_service import (
    add_book_service,
    list_books_service,
    get_book_service,
    search_external_books_service,
    recommend_books_for_user,
    add_book_to_list_service,
    list_reading_list_service,
    remove_book_from_list_service,
)

book_bp = Blueprint("book_bp", __name__)

@book_bp.route("/", methods=["POST"])
@token_required
def add_book():
    """
    Add a new book to the catalog.
    ---
    tags:
      - Books
    summary: Add a new book
    consumes:
      - application/json
    parameters:
      - in: body
        name: book
        schema:
          type: object
          properties:
            title:
              type: string
            author:
              type: string
            description:
              type: string
            isbn:
              type: string
          required:
            - title
            - author
    responses:
      200:
        description: Book created successfully
    """
    response, status = add_book_service(request.json)
    return jsonify(response), status

@book_bp.route("/", methods=["GET"])
def list_books():
    """
    List books in the catalog.
    ---
    tags:
      - Books
    summary: List all books
    parameters:
      - name: q
        in: query
        type: string
        description: Optional search query
    responses:
      200:
        description: A list of books
    """
    # Redirect browser navigation to the UI page.
    # The UI fetches JSON explicitly with ?json=1.
    if request.args.get('json') != '1' and request.accept_mimetypes.accept_html:
        return redirect(url_for('books_page'))

    query = request.args.get("q")
    response = list_books_service(query)
    return jsonify(response), 200

@book_bp.route("/search", methods=["GET"])
def search_books():
    """
    Search external book sources.
    ---
    tags:
      - Books
    summary: Search books externally
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search query string
    responses:
      200:
        description: Search results returned
    """
    query = request.args.get("q")
    response, status = search_external_books_service(query)
    return jsonify(response), status

@book_bp.route("/list", methods=["POST"])
@token_required
def add_to_reading_list():
    """
    Add or update a book on the authenticated user’s reading list.
    ---
    tags:
      - Reading Lists
    summary: Add or update a reading list item
    consumes:
      - application/json
    parameters:
      - in: body
        name: list_item
        schema:
          type: object
          properties:
            book_id:
              type: integer
            status:
              type: string
          required:
            - book_id
    responses:
      200:
        description: Book added to reading list successfully
    """
    response, status = add_book_to_list_service(request.json, request.user_id)
    return jsonify(response), status

@book_bp.route("/list", methods=["GET"])
@token_required
def get_reading_list():
    """
    Return the authenticated user’s reading list.
    ---
    tags:
      - Reading Lists
    summary: List reading list items
    parameters:
      - name: status
        in: query
        type: string
        description: Optional reading status filter
    responses:
      200:
        description: Reading list returned successfully
    """
    status = request.args.get("status")
    response = list_reading_list_service(request.user_id, status)
    return jsonify(response), 200

@book_bp.route("/list/<int:book_id>", methods=["DELETE"])
@token_required
def remove_from_reading_list(book_id):
    """
    Remove a book from the authenticated user’s reading list.
    ---
    tags:
      - Reading Lists
    summary: Remove a book from a reading list
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Book removed from reading list successfully
    """
    response, status = remove_book_from_list_service(request.user_id, book_id)
    return jsonify(response), status

@book_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """
    Get a book by its ID.
    ---
    tags:
      - Books
    summary: Get book details
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: Book ID
    responses:
      200:
        description: Book details returned
      404:
        description: Book not found
    """
    response, status = get_book_service(book_id)
    return jsonify(response), status

@book_bp.route("/recommend", methods=["GET"])
@token_required
def recommend_books():
    """
    Recommend books for the authenticated user.
    ---
    tags:
      - Books
    summary: Recommend books
    responses:
      200:
        description: Book recommendations returned
    """
    response, status = recommend_books_for_user(request.user_id)
    return jsonify(response), status

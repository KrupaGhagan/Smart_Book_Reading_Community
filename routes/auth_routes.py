from flask import Blueprint, request, jsonify
from services.auth_service import signup_service, login_service

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    summary: Sign up a new user
    consumes:
      - application/json
    parameters:
      - in: body
        name: user
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
          required:
            - username
            - email
            - password
    responses:
      200:
        description: User signed up successfully
    """
    response, status = signup_service(request.json)
    return jsonify(response), status

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate an existing user.
    ---
    tags:
      - Authentication
    summary: Log in a user
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
          required:
            - email
            - password
    responses:
      200:
        description: User logged in successfully
    """
    response, status = login_service(request.json)
    return jsonify(response), status

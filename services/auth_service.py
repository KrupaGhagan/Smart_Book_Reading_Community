import os
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from config.database import db
from models.user_model import User

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")


def signup_service(data):
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    name = data.get("name")

    if not username or not password or not email:
        return {"message": "username, password, and email are required"}, 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return {"message": "User already exists"}, 409

    user = User(
        username=username,
        password=generate_password_hash(password),
        email=email,
        name=name,
    )
    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully", "user_id": user.id}, 201


def login_service(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "username and password are required"}, 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return {"message": "Invalid credentials"}, 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=8),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    return {"token": token, "user_id": user.id}, 200

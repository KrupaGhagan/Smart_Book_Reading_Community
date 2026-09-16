import os
import jwt
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            bearer = request.headers.get("Authorization")
            if bearer.startswith("Bearer "):
                token = bearer.split(" ", 1)[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except Exception:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


def decode_token():
    token = None

    if "Authorization" in request.headers:
        bearer = request.headers.get("Authorization")
        if bearer.startswith("Bearer "):
            token = bearer.split(" ", 1)[1]

    if not token:
        return None, ({"message": "Token is missing"}, 401)

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data, None
    except jwt.ExpiredSignatureError:
        return None, ({"message": "Token has expired"}, 401)
    except Exception:
        return None, ({"message": "Invalid token"}, 401)

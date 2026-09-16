import os
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, redirect, url_for, session

from flask import current_app as app

oauth_bp = Blueprint("oauth_bp", __name__)

oauth = OAuth()

google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
)


def init_oauth(app):
    oauth.init_app(app)


@oauth_bp.route("/login")
def login():
    """
    Redirect to Google for OAuth login.
    ---
    tags:
      - OAuth
    summary: Redirect to Google login
    responses:
      302:
        description: Redirect to Google authorization
    """
    redirect_uri = url_for("oauth_bp.authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


@oauth_bp.route("/authorize")
def authorize():
    """
    Handle the OAuth callback and return user info.
    ---
    tags:
      - OAuth
    summary: Handle OAuth callback
    responses:
      200:
        description: OAuth login succeeded
    """
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()
    session["user"] = user_info
    return {
        "message": "OAuth login succeeded",
        "user": user_info,
    }

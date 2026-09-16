import os

from flask import Flask, render_template
from flasgger import Swagger
from flask_smorest import Api

from config.database import init_db
from config.oauth_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from config.seeder import seed_books
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.review_routes import review_bp
from routes.group_routes import group_bp
from routes.progress_routes import progress_bp
from routes.payment_routes import payment_bp
from routes.ai_routes import ai_bp
from routes.activity_routes import activity_bp
from routes.oauth_routes import oauth_bp, init_oauth
from socket_events import socketio

app = Flask(__name__, template_folder="templates")

os.makedirs(app.instance_path, exist_ok=True)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "supersecretkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(app.instance_path, 'bookclub.db').replace('\\', '/')}",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["GOOGLE_CLIENT_ID"] = GOOGLE_CLIENT_ID
app.config["GOOGLE_CLIENT_SECRET"] = GOOGLE_CLIENT_SECRET
app.config["API_TITLE"] = "Book Reading Community Platform"
app.config["API_VERSION"] = "1.0.0"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["SWAGGER"] = {
    "title": "Book Reading Community Platform",
    "uiversion": 3,
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Book Community API",
        "description": "Discover books, maintain reading lists, publish reviews, join collaborative reading groups, and track reading activity.",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
}

swagger = Swagger(app, template=swagger_template)
api = Api(app)

init_db(app)
seed_books(app)
init_oauth(app)
socketio.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(book_bp, url_prefix="/api/books")
app.register_blueprint(review_bp, url_prefix="/api/reviews")
app.register_blueprint(group_bp, url_prefix="/api/groups")
app.register_blueprint(progress_bp, url_prefix="/api/progress")
app.register_blueprint(activity_bp, url_prefix="/api/activity")
app.register_blueprint(payment_bp, url_prefix="/api/payment")
app.register_blueprint(ai_bp, url_prefix="/api/ai")
app.register_blueprint(oauth_bp, url_prefix="/auth")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/books")
def books_page():
    return render_template("books.html")

@app.route("/groups")
def groups_page():
    return render_template("groups.html")

@app.route("/groups/room")
def group_room_page():
    return render_template("group_room.html")

@app.route("/progress")
def progress_page():
    return render_template("progress.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug, allow_unsafe_werkzeug=True)

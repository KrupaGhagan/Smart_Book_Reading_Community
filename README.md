# 📚 Smart Book Reading Community

A full-stack **Book Reading Community Platform** that combines digital book discovery, social reading, collaborative reading groups, reading progress tracking, reviews, AI-powered recommendations, and online subscriptions into a single platform.

The application is built using **Python Flask** with a modular backend architecture and provides both web pages and REST APIs for interacting with the platform.

---

## 🌟 Project Overview

**Smart Book Reading Community** is designed for readers who want more than just a digital book library.

The platform allows users to:

* 🔐 Create an account and securely log in
* 🔎 Discover and search for books
* ⭐ Rate and review books
* 📚 Create and manage reading lists
* 📖 Track reading progress
* 👥 Join or create reading groups
* 💬 Participate in collaborative discussions
* 📊 Track reading activities
* 🤖 Get AI-powered book recommendations
* 💳 Subscribe through online payments
* 🔑 Sign in using Google OAuth
* ⚡ Participate in real-time group interactions
* 📘 Access documented REST APIs through Swagger/OpenAPI

The project is structured as a modular Flask application, making it easier to maintain and extend.

---

## ✨ Key Features

### 🔐 Authentication & Authorization

* User registration
* User login
* JWT-based authentication
* Protected API endpoints
* Password handling using Werkzeug
* Google OAuth login
* Session-based web interactions

---

### 📚 Book Discovery

Users can discover and search for books through the platform.

Features include:

* Book search
* Book information
* Book discovery
* Reading-list management
* Seeded book data
* Book-related API endpoints

---

### ⭐ Reviews & Ratings

Users can interact with books by sharing their opinions.

* Submit book reviews
* Give ratings
* View reviews
* Build a community-driven book discovery experience

---

### 📖 Reading Progress

Users can keep track of their reading journey.

The system supports:

* Reading progress tracking
* Progress updates
* Reading activity monitoring
* Personal reading history

This allows users to maintain a structured record of their reading activities.

---

### 👥 Reading Groups

Readers can form communities around books and shared interests.

Users can:

* Create reading groups
* Join groups
* Manage group membership
* Participate in discussions
* Publish discussion posts
* Interact with other readers

---

### 💬 Real-Time Communication

The application uses **Flask-SocketIO** to support real-time communication and group-related interactions.

This allows the platform to provide a more interactive community experience instead of relying only on traditional HTTP requests.

---

### 🤖 AI-Powered Recommendations

The platform includes an AI module for generating book recommendations.

The project includes Google Generative AI integration, allowing the recommendation system to provide intelligent suggestions based on user interactions and reading interests.

Potential recommendation inputs include:

* Reading history
* Books
* User interests
* Reviews
* Reading activity

---

### 💳 Subscription & Payments

The platform includes payment functionality using **Razorpay**.

This provides a foundation for:

* Subscription plans
* Payment processing
* Premium features
* Payment-related API operations

---

### 🔑 Google OAuth

Users can authenticate through Google using OAuth.

The project uses **Authlib** and configurable Google OAuth credentials.

---

### 📘 API Documentation

The backend provides API documentation using:

* Swagger
* OpenAPI
* Flask-Smorest
* Marshmallow

This makes it easier for developers to understand and test the available APIs.

---

## 🏗️ System Architecture

```text
                        ┌──────────────────────────┐
                        │        User / Client     │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │       Flask Web App      │
                        │        app.py             │
                        └────────────┬─────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │    Routes   │       │ Middleware  │       │ Socket.IO   │
       └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
              │                      │                     │
              ▼                      ▼                     ▼
       ┌─────────────────────────────────────────────────────────┐
       │                     Application Logic                    │
       ├──────────┬─────────┬──────────┬──────────┬──────────────┤
       │  Books   │ Reviews │  Groups  │ Progress │     AI       │
       └──────────┴─────────┴──────────┴──────────┴──────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │     Models       │
                            │ Flask-SQLAlchemy │
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │     Database     │
                            │ SQLite / Postgres│
                            └──────────────────┘

                    External Integrations
                    ─────────────────────
                    Google OAuth
                    Google Generative AI
                    Razorpay Payments
```

---

## 🗂️ Project Structure

```text
Smart_Book_Reading_Community/
│
├── app.py
├── socket_events.py
├── requirements.txt
├── Procfile
├── render.yaml
├── runtime.txt
├── README.md
│
├── config/
│   ├── database.py
│   ├── oauth_config.py
│   └── seeder.py
│
├── middleware/
│   └── jwt_middleware.py
│
├── models/
│   ├── __init__.py
│   ├── activity_model.py
│   ├── book_model.py
│   ├── discussion_model.py
│   ├── group_model.py
│   ├── progress_model.py
│   ├── review_model.py
│   └── user_model.py
│
├── routes/
│   ├── auth_routes.py
│   ├── book_routes.py
│   ├── review_routes.py
│   ├── group_routes.py
│   ├── progress_routes.py
│   ├── activity_routes.py
│   ├── payment_routes.py
│   ├── ai_routes.py
│   └── oauth_routes.py
│
├── services/
│   └── ...
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── books.html
│   ├── groups.html
│   ├── group_room.html
│   └── progress.html
│
└── instance/
    └── bookclub.db
```

The repository currently follows this modular structure, with dedicated configuration, middleware, models, routes, services, and application files.

---

## 🧩 Backend Modules

| Module             | Responsibility                         |
| ------------------ | -------------------------------------- |
| `app.py`           | Main Flask application                 |
| `config/`          | Database, OAuth and seed configuration |
| `middleware/`      | JWT authentication middleware          |
| `models/`          | Database models                        |
| `routes/`          | REST/API route definitions             |
| `services/`        | Business/service logic                 |
| `socket_events.py` | Real-time Socket.IO events             |
| `templates/`       | Frontend HTML pages                    |
| `requirements.txt` | Python dependencies                    |
| `render.yaml`      | Render deployment configuration        |
| `Procfile`         | Production process configuration       |
| `runtime.txt`      | Python runtime configuration           |

---

## 🛠️ Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-SocketIO
* PyJWT
* Werkzeug

### Database

* SQLite for local development
* PostgreSQL supported for hosted deployment

### Authentication

* JWT
* Google OAuth
* Authlib

### API

* Flask-Smorest
* Marshmallow
* Flasgger
* OpenAPI / Swagger

### AI

* Google Generative AI

### Payments

* Razorpay

### Deployment

* Gunicorn
* Render
* Railway
* Heroku-style Python hosting

---

## 🔄 Application Flow

```text
User
 │
 ▼
Login / Register
 │
 ▼
Authentication
 │
 ├───────────────┐
 │               │
 ▼               ▼
Book Discovery   Dashboard
 │               │
 ▼               ├── Reading Progress
Reviews          ├── Reading Activity
 │               ├── Reading Groups
 ▼               └── Recommendations
Reading Lists
 │
 ▼
AI Recommendations
 │
 ▼
Personalized Reading Experience
```

---

## 🔐 Authentication Flow

```text
User
 │
 ├── Register/Login
 │
 ▼
Flask Authentication API
 │
 ▼
JWT Token
 │
 ▼
Protected API Routes
 │
 ▼
User-specific Resources
```

Google OAuth is also available as an alternative authentication mechanism.

---

## 🤖 AI Recommendation Flow

```text
User Reading Activity
        │
        ▼
User Preferences / History
        │
        ▼
AI Recommendation API
        │
        ▼
Google Generative AI
        │
        ▼
Recommended Books
        │
        ▼
User
```

---

## 💬 Reading Group Flow

```text
Create / Discover Group
          │
          ▼
       Join Group
          │
          ▼
    Group Membership
          │
          ▼
   Discussion Posts
          │
          ▼
 Real-Time Interaction
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/KrupaGhagan/Smart_Book_Reading_Community.git
```

```bash
cd Smart_Book_Reading_Community
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

If PowerShell blocks activation, you can run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The repository's dependency file includes Flask, SQLAlchemy, Socket.IO, JWT, OAuth, Swagger/OpenAPI libraries, PostgreSQL support, Razorpay, Google Generative AI, and Gunicorn.

---

## 🔑 Environment Variables

Create a `.env` file or configure environment variables in your deployment platform.

Example:

```env
SECRET_KEY=your_secret_key

FLASK_DEBUG=1

DATABASE_URL=your_database_url

GOOGLE_CLIENT_ID=your_google_client_id

GOOGLE_CLIENT_SECRET=your_google_client_secret

RAZORPAY_KEY_ID=your_razorpay_key_id

RAZORPAY_KEY_SECRET=your_razorpay_key_secret

GOOGLE_API_KEY=your_google_ai_api_key
```

> Never commit API keys, passwords, OAuth secrets, or payment credentials to GitHub.

---

## ▶️ Run the Application

Start the application with:

```bash
python app.py
```

The application runs on:

```text
http://127.0.0.1:8000
```

The project also supports production execution through Gunicorn.

---

## 📡 API Endpoints

The application organizes APIs into multiple modules.

### Authentication

```text
/api/auth
```

### Books

```text
/api/books
```

### Reviews

```text
/api/reviews
```

### Reading Groups

```text
/api/groups
```

### Reading Progress

```text
/api/progress
```

### Reading Activity

```text
/api/activity
```

### Payments

```text
/api/payment
```

### AI

```text
/api/ai
```

### OAuth

```text
/auth
```

These blueprints are registered directly by the main Flask application.

---

## 📖 Web Pages

The application currently provides pages such as:

| Route          | Purpose               |
| -------------- | --------------------- |
| `/`            | Home page             |
| `/login`       | Login                 |
| `/register`    | User registration     |
| `/dashboard`   | User dashboard        |
| `/books`       | Book discovery        |
| `/groups`      | Reading groups        |
| `/groups/room` | Group discussion room |
| `/progress`    | Reading progress      |

---

## 📘 API Documentation

Swagger/OpenAPI documentation is integrated into the Flask application.

The API documentation is intended to make it easier to:

* Explore endpoints
* Understand request/response structures
* Test APIs
* Understand authentication requirements
* Develop frontend integrations

---

## 🚀 Deployment

The project contains deployment configuration for Python hosting platforms.

### Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn --worker-class gthread --threads 100 --workers 1 --bind 0.0.0.0:$PORT app:app
```

Required environment variables should be configured through the hosting platform rather than committed to the repository.

The repository already contains:

```text
render.yaml
Procfile
runtime.txt
```

for deployment configuration.

---

## 🔒 Security Considerations

For production deployment:

* Use a strong `SECRET_KEY`
* Store credentials in environment variables
* Never commit `.env` files
* Use HTTPS
* Protect JWT-protected routes
* Use secure OAuth credentials
* Secure Razorpay credentials
* Use PostgreSQL or another production database
* Remove development/debug settings
* Avoid committing local database files and Python cache files

---

## 📈 Future Enhancements

Possible future improvements include:

* 📱 Mobile application
* 🔔 Push notifications
* 🧠 More advanced personalized recommendations
* 📊 Reading analytics dashboard
* 🏆 Reading challenges and achievements
* 🔥 Reading streaks
* 👤 User profiles and followers
* 💬 Advanced real-time chat
* 📚 Book cover and metadata APIs
* 🔍 Semantic book search
* 📝 AI-generated reading summaries
* 🎯 Personalized reading goals
* 🌐 Multi-language support
* ☁️ Cloud database and object storage
* 🧪 Automated testing and CI/CD

---

## 🎯 Project Goals

The main goals of **Smart Book Reading Community** are:

1. Make discovering books easier.
2. Encourage consistent reading.
3. Connect readers with similar interests.
4. Provide collaborative reading experiences.
5. Track individual reading progress.
6. Provide personalized AI-based recommendations.
7. Combine book discovery and social interaction in one platform.

---

## 👨‍💻 Project

**Smart Book Reading Community**

Repository:

`KrupaGhagan/Smart_Book_Reading_Community`

Built with:

**Python · Flask · SQLAlchemy · JWT · OAuth · Socket.IO · Google Generative AI · Razorpay**

---

## 📄 License

Add the appropriate license for your project before publishing or distributing it.

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub and sharing feedback through GitHub Issues.

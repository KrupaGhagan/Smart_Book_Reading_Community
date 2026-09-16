# Book Reading Community Platform

A Flask-based digital book discovery and social reading platform.

## Features
- User signup/login with JWT
- Google OAuth login support
- Book discovery and search
- Reviews and ratings
- Reading lists and progress tracking
- Reading groups and membership with collaborative discussion posts
- Reading activity logs for social engagement
- AI-powered recommendations
- Subscription payments with Razorpay
- Swagger API documentation

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8000`.

## Deploy

This project is ready for Python web hosts such as Render, Railway, or Heroku-style platforms.

### Render

1. Push this project to GitHub.
2. In Render, create a new Web Service from the repository.
3. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --worker-class gthread --threads 100 --workers 1 --bind 0.0.0.0:$PORT app:app`
4. Add environment variables:
   - `SECRET_KEY`: any long random secret
   - `FLASK_DEBUG`: `0`
   - Optional `DATABASE_URL`: hosted PostgreSQL connection string
5. Deploy.

The included `render.yaml`, `Procfile`, and `runtime.txt` provide the same production settings automatically on supported hosts.

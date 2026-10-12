# Blog Project

A small blog API built with [FastAPI](https://fastapi.tiangolo.com/) and SQLAlchemy (SQLite). It provides account management with JWT authentication, and posts that authenticated users can create, edit and like.

## Features

- **Auth** (`/auth`): create, read, update and delete accounts; log in; refresh an access token.
- **Posts** (`/posts`): create a post, update a post, and toggle a like on a post.
- Interactive API docs at `/docs` (Swagger UI) once the server is running.

## Project layout

```
main.py            # FastAPI app, router registration
app/
  config.py        # loads SECRET_KEY / ALGORITHM from .env
  database.py      # SQLite engine and session dependency
  auth/            # accounts, login and token logic
  post/            # post models, schemas, routes and services
nginx/             # nginx reverse proxy used by docker-compose
Dockerfile
docker-compose.yml
```

## Configuration

Create a `.env` file in the project root:

```
SECRET_KEY=change-me
ALGORITHM=HS256   # optional, defaults to HS256
```

The app refuses to start if `SECRET_KEY` is missing.

## Run locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Run with Docker

```bash
docker compose up --build
```

nginx listens on port 80 and proxies to the API container, so the docs are at http://localhost/docs. The SQLite database is stored in `app.db`, mounted from the project root.

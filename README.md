# Blog Project

A blog application with a [FastAPI](https://fastapi.tiangolo.com/) + SQLAlchemy (SQLite) backend and a [Next.js](https://nextjs.org/) frontend. The backend provides account management with JWT authentication, profile photos, and posts that authenticated users can create, edit and like.

## Features

### Backend (`backend/`)

- **Auth** (`/auth`): `POST /login`, `POST /refresh-token`.
- **Accounts** (`/account`): create (`POST`), read (`GET /{account_id}`), update (`PUT /{account_id}`), delete (`DELETE /{account_id}`), and upload a profile photo (`POST /{account_id}/photo`). Uploaded photos are served from `/uploads`.
- **Posts** (`/posts`): create a post (`POST`), update a post (`PATCH /{postId}`), and toggle a like (`POST /{postId}/like`).
- Interactive API docs at `/docs` (Swagger UI) once the server is running.

### Frontend (`frontend/`)

Next.js (App Router) with React, with shared layout components. The signup page is connected to the API: it creates an account through the create account endpoint (`POST /account`, URL taken from `NEXT_PUBLIC_API_URL`). The other pages are still placeholders.

| Route         | Page                 |
| ------------- | -------------------- |
| `/`           | Home                 |
| `/feed`       | My Feed              |
| `/login`      | Login                |
| `/signup`     | Sign up              |
| `/categories` | Categories           |
| `/teams`      | Teams                |
| `/about`      | About                |

Shared components in `frontend/components/`: `Header`, `Footer`, `NavLink`, `StepCard`.

## Project layout

```
backend/
  main.py          # FastAPI app, router registration, /uploads static mount
  .env             # SECRET_KEY / ALGORITHM
  Dockerfile
  requirements.txt
  app/
    config.py      # loads SECRET_KEY / ALGORITHM from .env
    database.py    # SQLite engine and session dependency
    acc/           # account models, schemas, routes, services
    auth/          # login, token logic and auth dependencies
    post/          # post models, schemas, routes and services
frontend/
  app/             # Next.js routes (feed, login, categories, teams, about)
  components/      # Header, Footer, NavLink, StepCard
  public/          # static assets
  package.json
nginx/             # nginx reverse proxy used by docker-compose
scripts/           # init_db, inspect_token, smoke_test_acc
docker-compose.yml
```

## Configuration

Create a `.env` file in `backend/`:

```
SECRET_KEY=change-me
ALGORITHM=HS256   # optional, defaults to HS256
```

The app refuses to start if `SECRET_KEY` is missing. `.env` and `*.db` files are git-ignored.

## Run locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000. Other scripts: `npm run build`, `npm start`, `npm run lint`.

## Run with Docker

```bash
docker compose up --build
```

This starts the API and nginx only (the frontend is not containerized yet). nginx listens on port 80 and proxies to the API container, so the docs are at http://localhost/docs. The SQLite database (`app.db`) and `uploads/` are mounted from the project root. Running locally from `backend/` uses `backend/app.db` unless you set `DATABASE_URL`.

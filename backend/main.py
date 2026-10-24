from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.auth.routers import router as auth_router
from app.acc.routers import router as acc_router
from app.post.routers import router as blog_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mentorship API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(acc_router)
app.include_router(blog_router)

Path("uploads/profile_photos").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



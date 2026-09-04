from fastapi import FastAPI
from app.database import engine, Base
from app.auth.routers import router as auth_router
from app.post.routers import router as blog_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mentorship API")

app.include_router(auth_router)
app.include_router(blog_router)

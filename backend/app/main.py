from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .config import settings
from .routers import auth_router, reports_router
from . import models

app = FastAPI(title="Frying Report OCR API")

# create tables
models.Base = models  # not used; keep for clarity
Base.metadata.create_all(bind=engine)

# create admin on startup
@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    from .crud import get_user_by_email, create_user
    from .auth import hash_password
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        if not get_user_by_email(db, settings.ADMIN_EMAIL):
            create_user(db, "System Admin", settings.ADMIN_EMAIL, hash_password(settings.ADMIN_PASSWORD))
    db.close()

app.include_router(auth_router.router)
app.include_router(reports_router.router)

@app.get("/")
def root():
    return {"status": "ok"}

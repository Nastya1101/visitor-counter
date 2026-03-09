from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Visitor
from app.schemas import VisitResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visitor Counter")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/visit", response_model=VisitResponse)
def create_visit(
    request: Request,
    db: Session = Depends(get_db),
):
    forwarded_for = request.headers.get("x-forwarded-for")
    real_ip = request.headers.get("x-real-ip")

    ip_address = forwarded_for or real_ip or (request.client.host if request.client else None)
    user_agent = request.headers.get("user-agent")

    visitor = Visitor(
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(visitor)
    db.commit()

    return VisitResponse(message="Visitor saved")
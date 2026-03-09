from pathlib import Path
from collections import Counter
from datetime import datetime
from io import BytesIO

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from openpyxl import Workbook
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Visitor
from app.schemas import VisitResponse, VisitorRecord

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visitor Counter")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

def get_client_ip(request: Request) -> str | None:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # RFC 7239 chain format: client, proxy1, proxy2...
        first_hop = forwarded_for.split(",")[0].strip()
        if first_hop:
            return first_hop

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    return request.client.host if request.client else None


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
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("user-agent")

    visitor = Visitor(
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(visitor)
    db.commit()

    return VisitResponse(message="Visitor saved")


@app.get("/visitors", response_model=list[VisitorRecord])
def get_visitors(db: Session = Depends(get_db)):
    visitors = db.query(Visitor).order_by(desc(Visitor.visited_at), desc(Visitor.id)).all()
    return visitors


@app.get("/visitors/export")
def export_visitors_to_excel(db: Session = Depends(get_db)):
    visitors = db.query(Visitor).order_by(desc(Visitor.visited_at), desc(Visitor.id)).all()
    visits_per_ip = Counter(visitor.ip_address for visitor in visitors)
    unique_visitors: dict[str | None, Visitor] = {}

    # visitors already sorted by newest first; keep first row per ip
    for visitor in visitors:
        if visitor.ip_address not in unique_visitors:
            unique_visitors[visitor.ip_address] = visitor

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Visitors"
    worksheet.append(["id", "ip_address", "user_agent", "visited_at", "quantity"])

    for visitor in unique_visitors.values():
        visited_at = visitor.visited_at.isoformat() if visitor.visited_at else None
        quantity = visits_per_ip[visitor.ip_address]
        worksheet.append([visitor.id, visitor.ip_address, visitor.user_agent, visited_at, quantity])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"visitors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

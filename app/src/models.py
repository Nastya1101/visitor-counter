from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    visited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GradeClick(Base):
    __tablename__ = "grade_clicks"

    id = Column(Integer, primary_key=True, index=True)
    grade_name = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

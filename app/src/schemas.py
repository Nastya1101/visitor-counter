from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisitResponse(BaseModel):
    message: str


class VisitorRecord(BaseModel):
    id: int
    ip_address: str | None
    user_agent: str | None
    visited_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GradeClickResponse(BaseModel):
    message: str
    grade_name: str


class GradeClickRecord(BaseModel):
    id: int
    grade_name: str
    ip_address: str | None
    user_agent: str | None
    clicked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GradeClickStats(BaseModel):
    grade_name: str
    clicks: int

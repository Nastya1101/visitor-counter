from pydantic import BaseModel


class VisitResponse(BaseModel):
    message: str
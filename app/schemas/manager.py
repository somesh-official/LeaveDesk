from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ApproveRequest(BaseModel):
    comment: str | None = Field(default=None, max_length=500)


class RejectRequest(BaseModel):
    comment: str = Field(min_length=5, max_length=500)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 5:
            raise ValueError("Comment must contain at least 5 non-space characters")

        return value


class ManagerRequestResponse(BaseModel):
    request_type: Literal["LEAVE", "WFH"]

    id: int
    employee_id: int
    employee_name: str

    leave_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None

    leave_type: str | None = None
    duration_type: str | None = None
    half: str | None = None
    hours: int | None = None

    days_counted: float
    status: str
    reason: str | None = None

    created_at: datetime

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator


class LeaveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    leave_date: date
    leave_type: str
    duration_type: str
    half: str | None
    hours: int | None
    days_counted: float
    status: str
    reason: str | None

class LeaveCreate(BaseModel):
    leave_date: date

    leave_type: Literal["CASUAL", "SICK", "EARNED"]

    duration_type: Literal["FULL_DAY", "HALF_DAY", "HOURS"]

    half: Literal["FIRST_HALF", "SECOND_HALF"] | None = None

    hours: int | None = None

    reason: str | None = Field(default=None, max_length=500)

    @field_validator("hours", mode="before")
    @classmethod
    def validate_hours_type(cls, value):
        if isinstance(value, float) and not value.is_integer():
            raise ValueError(
                "Hours must be a whole number: choose 1, 2, or 3."
            )

        return value

    @model_validator(mode="after")
    def validate_duration(self):
        if self.duration_type == "FULL_DAY":
            if self.half is not None or self.hours is not None:
                raise ValueError("FULL_DAY must not contain half or hours")

        elif self.duration_type == "HALF_DAY":
            if self.half is None:
                raise ValueError("HALF_DAY requires FIRST_HALF or SECOND_HALF")

            if self.hours is not None:
                raise ValueError("HALF_DAY must not contain hours")

        elif self.duration_type == "HOURS":
            if self.hours not in (1, 2, 3):
                raise ValueError("HOURS must be 1 to 3")

            if self.half is not None:
                raise ValueError("HOURS must not contain half")

        return self

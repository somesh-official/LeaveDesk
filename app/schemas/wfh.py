
from datetime import date, timedelta

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WFHCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")

        working_days = 0
        current_date = self.start_date

        while current_date <= self.end_date:
            if current_date.weekday() < 5:
                working_days += 1

            current_date += timedelta(days=1)

        if working_days == 0:
            raise ValueError("WFH must include at least one working day")

        if working_days > 2:
            raise ValueError("WFH request cannot exceed 2 working days")

        return self


class WFHResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    start_date: date
    end_date: date
    days_counted: float
    status: str
    reason: str | None

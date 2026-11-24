from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Leave(Base):
    __tablename__ = "leaves"

    __table_args__ = (
        CheckConstraint(
            "leave_type IN ('CASUAL', 'SICK', 'EARNED')",
            name="check_leave_type",
        ),
        CheckConstraint(
            "duration_type IN ('FULL_DAY', 'HALF_DAY', 'HOURS')",
            name="check_duration_type",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')",
            name="check_leave_status",
        ),
        CheckConstraint(
            "days_counted > 0",
            name="check_leave_days_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    leave_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    
    leave_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    duration_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    half: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    hours: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    days_counted: Mapped[float] = mapped_column(
        Numeric(4, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    decided_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    decision_comment: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date

from app.models.leave import Leave
from app.schemas.leave import LeaveCreate
from app.models.wfh import WFH


def calculate_leave_days(payload: LeaveCreate) -> float:
    if payload.duration_type == "FULL_DAY":
        return 1.0

    if payload.duration_type == "HALF_DAY":
        return 0.5

    if payload.duration_type == "HOURS":
        return payload.hours / 8

    raise ValueError("Invalid leave duration type")



def check_leave_overlap(
    db: Session,
    employee_id: int,
    payload: LeaveCreate,
) -> None:

    # Check existing active leave requests on the same date.
    existing_leaves = db.scalars(
        select(Leave).where(
            Leave.employee_id == employee_id,
            Leave.leave_date == payload.leave_date,
            Leave.status.in_(["PENDING", "APPROVED"]),
        )
    ).all()

    for existing in existing_leaves:

        # Allow only opposite half-day combinations.
        if (
            existing.duration_type == "HALF_DAY"
            and payload.duration_type == "HALF_DAY"
            and existing.half != payload.half
        ):
            continue

        # Block every other combination.
        raise ValueError("Leave already exists for this date")

    # A full-day leave cannot overlap with an active WFH request.
    if payload.duration_type == "FULL_DAY":

        existing_wfh = db.scalars(
            select(WFH).where(
                WFH.employee_id == employee_id,
                WFH.status.in_(["PENDING", "APPROVED"]),
                WFH.start_date <= payload.leave_date,
                WFH.end_date >= payload.leave_date,
            )
        ).first()

        if existing_wfh is not None:
            raise ValueError(
                "Full-day leave cannot overlap with an active WFH request"
            )



def create_leave_request(
    db: Session,
    employee_id: int,
    payload: LeaveCreate,
) -> Leave:

    check_leave_overlap(db, employee_id, payload)

    days = calculate_leave_days(payload)

    new_leave = Leave(
        employee_id=employee_id,
        leave_date=payload.leave_date,
        leave_type=payload.leave_type,
        duration_type=payload.duration_type,
        half=payload.half,
        hours=payload.hours,
        days_counted=days,
        status="PENDING",
        reason=payload.reason,
    )

    try:
        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)
    except Exception:
        db.rollback()
        raise

    return new_leave



def get_my_leaves(
    db: Session,
    employee_id: int,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[Leave]:

    query = select(Leave).where(
        Leave.employee_id == employee_id
    )

    if status is not None:
        query = query.where(Leave.status == status)

    if from_date is not None:
        query = query.where(Leave.leave_date >= from_date)

    if to_date is not None:
        query = query.where(Leave.leave_date <= to_date)

    leaves = db.scalars(
        query.order_by(Leave.created_at.desc())
    ).all()

    return leaves


def cancel_leave_request(
    db: Session,
    leave_id: int,
    employee_id: int,
) -> Leave:

    leave = db.get(Leave, leave_id)

    if leave is None or leave.employee_id != employee_id:
        raise LookupError("Leave request not found")

    if leave.status != "PENDING":
        raise ValueError("Only pending leave requests can be cancelled")

    leave.status = "CANCELLED"

    try:
        db.commit()
        db.refresh(leave)
    except Exception:
        db.rollback()
        raise

    return leave

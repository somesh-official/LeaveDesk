
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.leave import Leave
from app.models.wfh import WFH
from app.schemas.wfh import WFHCreate


def get_working_dates(start_date: date, end_date: date) -> list[date]:
    working_dates = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:
            working_dates.append(current_date)

        current_date += timedelta(days=1)

    return working_dates


def check_wfh_overlap(
    db: Session,
    employee_id: int,
    working_dates: list[date],
) -> None:

    requested_dates = set(working_dates)

    existing_wfh = db.scalars(
        select(WFH).where(
            WFH.employee_id == employee_id,
            WFH.status.in_(["PENDING", "APPROVED"]),
        )
    ).all()

    for existing in existing_wfh:
        existing_dates = set(
            get_working_dates(existing.start_date, existing.end_date)
        )

        if requested_dates.intersection(existing_dates):
            raise ValueError(
                "WFH already exists for an overlapping date"
            )

    full_day_leaves = db.scalars(
        select(Leave).where(
            Leave.employee_id == employee_id,
            Leave.leave_date.in_(working_dates),
            Leave.duration_type == "FULL_DAY",
            Leave.status.in_(["PENDING", "APPROVED"]),
        )
    ).all()

    if full_day_leaves:
        raise ValueError("WFH cannot overlap with a full-day leave")


def create_wfh_request(
    db: Session,
    employee_id: int,
    payload: WFHCreate,
) -> WFH:

    working_dates = get_working_dates(
        payload.start_date,
        payload.end_date,
    )

    check_wfh_overlap(
        db=db,
        employee_id=employee_id,
        working_dates=working_dates,
    )

    new_wfh = WFH(
        employee_id=employee_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days_counted=len(working_dates),
        status="PENDING",
        reason=payload.reason,
    )

    try:
        db.add(new_wfh)
        db.commit()
        db.refresh(new_wfh)
    except Exception:
        db.rollback()
        raise

    return new_wfh



def get_my_wfh(
    db: Session,
    employee_id: int,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[WFH]:

    query = select(WFH).where(WFH.employee_id == employee_id)

    if status is not None:
        query = query.where(WFH.status == status)

    if from_date is not None:
        query = query.where(WFH.end_date >= from_date)

    if to_date is not None:
        query = query.where(WFH.start_date <= to_date)

    return db.scalars(
        query.order_by(WFH.created_at.desc())
    ).all()



def cancel_wfh_request(
    db: Session,
    wfh_id: int,
    employee_id: int,
) -> WFH:

    wfh = db.get(WFH, wfh_id)

    if wfh is None or wfh.employee_id != employee_id:
        raise LookupError("WFH request not found")

    if wfh.status != "PENDING":
        raise ValueError("Only pending WFH requests can be cancelled")

    wfh.status = "CANCELLED"

    try:
        db.commit()
        db.refresh(wfh)
    except Exception:
        db.rollback()
        raise

    return wfh


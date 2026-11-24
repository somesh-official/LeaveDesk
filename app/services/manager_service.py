
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.leave import Leave
from app.models.wfh import WFH


def get_manager_requests(
    db: Session,
    manager_id: int,
    status_filter: str = "PENDING",
    employee_id: int | None = None,
    from_date=None,
    to_date=None,
):
    # Find only this manager's direct reports.
    employees = db.scalars(
        select(User).where(User.manager_id == manager_id)
    ).all()

    employee_ids = [employee.id for employee in employees]
    employee_names = {
        employee.id: employee.name for employee in employees
    }

    if not employee_ids:
        return []

    # Fetch leave requests.
    leave_query = select(Leave).where(
        Leave.employee_id.in_(employee_ids),
        Leave.status == status_filter,
    )

    if employee_id is not None:
        leave_query = leave_query.where(
            Leave.employee_id == employee_id
        )

    if from_date is not None:
        leave_query = leave_query.where(
            Leave.leave_date >= from_date
        )

    if to_date is not None:
        leave_query = leave_query.where(
            Leave.leave_date <= to_date
        )

    leaves = db.scalars(leave_query).all()

    # Fetch WFH requests.
    wfh_query = select(WFH).where(
        WFH.employee_id.in_(employee_ids),
        WFH.status == status_filter,
    )

    if employee_id is not None:
        wfh_query = wfh_query.where(
            WFH.employee_id == employee_id
        )

    if from_date is not None:
        wfh_query = wfh_query.where(
            WFH.end_date >= from_date
        )

    if to_date is not None:
        wfh_query = wfh_query.where(
            WFH.start_date <= to_date
        )

    wfh_requests = db.scalars(wfh_query).all()

    # Combine both request types into one list.
    results = []

    for leave in leaves:
        results.append({
            "request_type": "LEAVE",
            "id": leave.id,
            "employee_id": leave.employee_id,
            "employee_name": employee_names[leave.employee_id],
            "leave_date": leave.leave_date,
            "leave_type": leave.leave_type,
            "duration_type": leave.duration_type,
            "half": leave.half,
            "hours": leave.hours,
            "days_counted": leave.days_counted,
            "status": leave.status,
            "reason": leave.reason,
            "created_at": leave.created_at,
        })

    for wfh in wfh_requests:
        results.append({
            "request_type": "WFH",
            "id": wfh.id,
            "employee_id": wfh.employee_id,
            "employee_name": employee_names[wfh.employee_id],
            "start_date": wfh.start_date,
            "end_date": wfh.end_date,
            "days_counted": wfh.days_counted,
            "status": wfh.status,
            "reason": wfh.reason,
            "created_at": wfh.created_at,
        })

    results.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    return results


def decide_request(
    db: Session,
    request_type: str,
    request_id: int,
    manager: User,
    decision: str,
    comment: str | None = None,
):
    if request_type == "LEAVE":
        request = db.get(Leave, request_id)

    elif request_type == "WFH":
        request = db.get(WFH, request_id)

    else:
        raise ValueError("Invalid request type")

    if request is None:
        raise LookupError("Request not found")

    # Confirm that the employee reports directly to this manager.
    employee = db.get(User, request.employee_id)

    if employee is None or employee.manager_id != manager.id:
        raise PermissionError("You cannot access this employee's request")

    # Only pending requests can be decided.
    if request.status != "PENDING":
        raise ValueError("Only pending requests can be approved or rejected")

    if decision == "REJECTED":
        if comment is None or len(comment.strip()) < 5:
            raise ValueError("Rejection comment must contain at least 5 characters")

    request.status = decision
    request.decided_by = manager.id
    request.decided_at = datetime.now(timezone.utc)
    request.decision_comment = comment

    try:
        db.commit()
        db.refresh(request)
    except Exception:
        db.rollback()
        raise

    return request

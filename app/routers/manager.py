
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.manager import (
    ApproveRequest,
    RejectRequest,
    ManagerRequestResponse,
)
from app.schemas.leave import LeaveResponse
from app.schemas.wfh import WFHResponse
from app.services.manager_service import (
    get_manager_requests,
    decide_request,
)


router = APIRouter(
    prefix="/manager",
    tags=["Manager"],
)


@router.get(
    "/requests",
    response_model=list[ManagerRequestResponse],
)
def list_manager_requests(
    status_filter: Literal[
        "PENDING", "APPROVED", "REJECTED", "CANCELLED"
    ] = Query(default="PENDING", alias="status"),
    employee_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    manager: User = Depends(require_role("manager")),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="from_date cannot be after to_date",
        )

    return get_manager_requests(
        db=db,
        manager_id=manager.id,
        status_filter=status_filter,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date,
    )


def handle_decision(
    db: Session,
    manager: User,
    request_type: str,
    request_id: int,
    decision: str,
    comment: str | None,
):
    try:
        return decide_request(
            db=db,
            request_type=request_type,
            request_id=request_id,
            manager=manager,
            decision=decision,
            comment=comment,
        )

    except LookupError:
        raise HTTPException(
            status_code=404,
            detail="Request not found",
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this employee's request",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@router.post(
    "/leaves/{leave_id}/approve",
    response_model=LeaveResponse,
)
def approve_leave(
    leave_id: int,
    payload: ApproveRequest,
    db: Session = Depends(get_db),
    manager: User = Depends(require_role("manager")),
):
    return handle_decision(
        db, manager, "LEAVE", leave_id, "APPROVED", payload.comment
    )


@router.post(
    "/leaves/{leave_id}/reject",
    response_model=LeaveResponse,
)
def reject_leave(
    leave_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    manager: User = Depends(require_role("manager")),
):
    return handle_decision(
        db, manager, "LEAVE", leave_id, "REJECTED", payload.comment
    )


@router.post(
    "/wfh/{wfh_id}/approve",
    response_model=WFHResponse,
)
def approve_wfh(
    wfh_id: int,
    payload: ApproveRequest,
    db: Session = Depends(get_db),
    manager: User = Depends(require_role("manager")),
):
    return handle_decision(
        db, manager, "WFH", wfh_id, "APPROVED", payload.comment
    )


@router.post(
    "/wfh/{wfh_id}/reject",
    response_model=WFHResponse,
)
def reject_wfh(
    wfh_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    manager: User = Depends(require_role("manager")),
):
    return handle_decision(
        db, manager, "WFH", wfh_id, "REJECTED", payload.comment
    )

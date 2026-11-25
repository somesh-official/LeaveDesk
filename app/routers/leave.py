from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.leave import LeaveCreate, LeaveResponse
from app.services.leave_service import (
    create_leave_request,
    get_my_leaves,
    cancel_leave_request,
)

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post(
    "",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_leave(
    payload: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_leave_request(
            db=db,
            employee_id=current_user.id,
            payload=payload,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.get("/me", response_model=list[LeaveResponse])
def list_my_leaves(
    status_filter: (
        Literal[
            "PENDING",
            "APPROVED",
            "REJECTED",
            "CANCELLED",
        ]
        | None
    ) = Query(default=None, alias="status"),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if from_date is not None and to_date is not None:
        if from_date > to_date:
            raise HTTPException(
                status_code=422,
                detail="from_date cannot be greater than to_date",
            )
    return get_my_leaves(
        db=db,
        employee_id=current_user.id,
        status=status_filter,
        from_date=from_date,
        to_date=to_date,
    )


@router.post("/{leave_id}/cancel", response_model=LeaveResponse)
def cancel_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return cancel_leave_request(
            db=db,
            leave_id=leave_id,
            employee_id=current_user.id,
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

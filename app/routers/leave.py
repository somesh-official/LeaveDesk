from fastapi import APIRouter, Depends, HTTPException, status
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


@router.post("/", status_code=status.HTTP_201_CREATED)
def submit_leave(
    payload: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        new_leave = create_leave_request(
            db=db,
            employee_id=current_user.id,
            payload=payload,
        )

        return {
            "message": "Leave request submitted successfully",
            "leave_id": new_leave.id,
            "employee_id": new_leave.employee_id,
            "leave_date": new_leave.leave_date,
            "leave_type": new_leave.leave_type,
            "duration_type": new_leave.duration_type,
            "half": new_leave.half,
            "hours": new_leave.hours,
            "days_counted": new_leave.days_counted,
            "status": new_leave.status,
            "reason": new_leave.reason,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.get("/me", response_model=list[LeaveResponse])
def list_my_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_leaves(
        db=db,
        employee_id=current_user.id,
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

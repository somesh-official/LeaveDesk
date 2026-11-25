
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Literal

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.wfh import WFHCreate, WFHResponse
from app.services.wfh_service import (
    create_wfh_request,
    get_my_wfh,
    cancel_wfh_request,
)

router = APIRouter(prefix="/wfh", tags=["Work From Home"])


@router.post(
    "",
    response_model=WFHResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_wfh(
    payload: WFHCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_wfh_request(
            db=db,
            employee_id=current_user.id,
            payload=payload,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )



@router.get("/me", response_model=list[WFHResponse])
def list_my_wfh(
    status_filter: Literal[
    "PENDING",
    "APPROVED",
    "REJECTED",
    "CANCELLED",
] | None = Query(default=None, alias="status"),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_wfh(
        db=db,
        employee_id=current_user.id,
        status=status_filter,
        from_date=from_date,
        to_date=to_date,
    )



@router.post("/{wfh_id}/cancel", response_model=WFHResponse)
def cancel_wfh(
    wfh_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return cancel_wfh_request(
            db=db,
            wfh_id=wfh_id,
            employee_id=current_user.id,
        )

    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WFH request not found",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

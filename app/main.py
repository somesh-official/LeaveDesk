from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import router as auth_router
from app.routers.leave import router as leave_router
from app.routers.wfh import router as wfh_router
from app.routers.manager import router as manager_router


app = FastAPI(
    title="LeaveDesk API",
    description="Employee Leave and Work From Home Management System",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(leave_router)
app.include_router(wfh_router)
app.include_router(manager_router)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

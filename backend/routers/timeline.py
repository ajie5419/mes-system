from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import timeline_service

router = APIRouter(tags=["时间线"])


@router.get("/api/v1/work-orders/{wo_id}/timeline")
def get_timeline(wo_id: int, db: Session = Depends(get_db)):
    events = timeline_service.get_work_order_timeline(db, wo_id)
    return events

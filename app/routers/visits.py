"""就诊记录接口:新增、时间段筛选查询。"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import logger
from app.models import Patient, Visit
from app.schemas import VisitCreate, VisitOut

router = APIRouter(prefix="/api/visits", tags=["visits"])


@router.post("", response_model=VisitOut, status_code=status.HTTP_201_CREATED)
def create_visit(payload: VisitCreate, db: Session = Depends(get_db)):
    """新增就诊记录。"""
    if db.get(Patient, payload.patient_id) is None:
        raise HTTPException(
            status_code=404, detail=f"病人 ID {payload.patient_id} 不存在"
        )
    visit = Visit(**payload.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    logger.info("新增就诊记录成功 id=%s patient_id=%s", visit.id, visit.patient_id)
    return visit


@router.get("", response_model=list[VisitOut])
def list_visits(
    start_date: date | None = None,
    end_date: date | None = None,
    patient_id: int | None = None,
    department: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """时间段筛选查询就诊记录,动态拼接 SQL 条件。"""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="开始日期不能晚于结束日期")
    if limit > 200:
        raise HTTPException(status_code=422, detail="limit 不能超过 200")

    # 动态拼接查询条件:仅对传入的筛选参数追加 WHERE 子句
    stmt = select(Visit)
    conditions = []
    if start_date:
        conditions.append(Visit.visit_date >= start_date)
    if end_date:
        conditions.append(Visit.visit_date <= end_date)
    if patient_id:
        conditions.append(Visit.patient_id == patient_id)
    if department:
        conditions.append(Visit.department.like(f"%{department}%"))
    if conditions:
        stmt = stmt.where(*conditions)

    stmt = stmt.order_by(Visit.visit_date.desc(), Visit.id.desc()).offset(skip).limit(limit)
    logger.info(
        "查询就诊记录 start=%s end=%s patient=%s dept=%s",
        start_date, end_date, patient_id, department,
    )
    return db.scalars(stmt).all()

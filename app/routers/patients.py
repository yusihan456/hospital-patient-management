"""病人信息 RESTful 接口:CRUD。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.logger import logger
from app.models import Patient
from app.schemas import PatientCreate, PatientOut, PatientUpdate, PatientWithVisits

router = APIRouter(prefix="/api/patients", tags=["patients"])


def _get_patient_or_404(db: Session, patient_id: int) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"病人 ID {patient_id} 不存在")
    return patient


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    """新增病人基础信息。"""
    patient = Patient(**payload.model_dump())
    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        # 主键冲突/唯一约束冲突(手机号、身份证重复)
        db.rollback()
        logger.warning("创建病人失败:唯一约束冲突 phone=%s id_card=%s",
                       payload.phone, payload.id_card)
        raise HTTPException(status_code=409, detail="手机号或身份证号已存在")
    logger.info("创建病人成功 id=%s name=%s", patient.id, patient.name)
    return patient


@router.get("", response_model=list[PatientOut])
def list_patients(
    skip: int = 0,
    limit: int = 20,
    name: str | None = None,
    db: Session = Depends(get_db),
):
    """分页查询病人列表,支持按姓名模糊搜索。"""
    if limit > 100:
        raise HTTPException(status_code=422, detail="limit 不能超过 100")
    stmt = select(Patient)
    if name:
        stmt = stmt.where(Patient.name.like(f"%{name}%"))
    stmt = stmt.order_by(Patient.id).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{patient_id}", response_model=PatientWithVisits)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """查询单个病人及其全部就诊记录。"""
    stmt = (
        select(Patient)
        .where(Patient.id == patient_id)
        .options(selectinload(Patient.visits))
    )
    patient = db.scalar(stmt)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"病人 ID {patient_id} 不存在")
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)
):
    """更新病人信息(仅更新传入字段)。"""
    patient = _get_patient_or_404(db, patient_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        db.rollback()
        logger.warning("更新病人失败:唯一约束冲突 id=%s", patient_id)
        raise HTTPException(status_code=409, detail="手机号或身份证号与其他病人重复")
    logger.info("更新病人成功 id=%s", patient_id)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """删除病人(级联删除其就诊记录)。"""
    patient = _get_patient_or_404(db, patient_id)
    db.delete(patient)
    db.commit()
    logger.info("删除病人成功 id=%s", patient_id)

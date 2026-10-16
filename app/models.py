"""数据模型:病人基础信息表 + 就诊记录表。"""
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    """病人基础信息表。"""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    gender: Mapped[str] = mapped_column(String(4), nullable=False, comment="男/女")
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    id_card: Mapped[str] = mapped_column(String(18), unique=True, comment="身份证号")
    address: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    visits: Mapped[list["Visit"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )


class Visit(Base):
    """就诊记录表。"""

    __tablename__ = "visits"
    __table_args__ = (
        # 高频查询字段索引:按就诊日期范围筛选、按病人查就诊历史
        Index("ix_visits_visit_date", "visit_date"),
        Index("ix_visits_patient_id", "patient_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    doctor: Mapped[str] = mapped_column(String(50), nullable=False)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False, comment="诊断结果")
    prescription: Mapped[str] = mapped_column(Text, default="", comment="处方/医嘱")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    patient: Mapped[Patient] = relationship(back_populates="visits")

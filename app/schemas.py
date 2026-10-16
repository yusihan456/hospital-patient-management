"""Pydantic 请求/响应模型:参数校验,拦截空值与非法输入。"""
import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
ID_CARD_PATTERN = re.compile(r"^\d{17}[\dXx]$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class PatientBase(BaseModel):
    name: str
    gender: str
    birth_date: date
    phone: str
    id_card: str
    address: str = ""

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("姓名不能为空")
        if len(v) > 50:
            raise ValueError("姓名长度不能超过 50 个字符")
        return v

    @field_validator("gender")
    @classmethod
    def gender_valid(cls, v: str) -> str:
        if v not in ("男", "女"):
            raise ValueError("性别只能是'男'或'女'")
        return v

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v: str) -> str:
        if not PHONE_PATTERN.match(v):
            raise ValueError("手机号格式非法,应为 11 位大陆手机号")
        return v

    @field_validator("id_card")
    @classmethod
    def id_card_valid(cls, v: str) -> str:
        if not ID_CARD_PATTERN.match(v):
            raise ValueError("身份证号格式非法,应为 18 位")
        return v.upper()


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    phone: str | None = None
    id_card: str | None = None
    address: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("姓名不能为空")
        return v

    @field_validator("gender")
    @classmethod
    def gender_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in ("男", "女"):
            raise ValueError("性别只能是'男'或'女'")
        return v

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v: str | None) -> str | None:
        if v is not None and not PHONE_PATTERN.match(v):
            raise ValueError("手机号格式非法,应为 11 位大陆手机号")
        return v

    @field_validator("id_card")
    @classmethod
    def id_card_valid(cls, v: str | None) -> str | None:
        if v is not None and not ID_CARD_PATTERN.match(v):
            raise ValueError("身份证号格式非法,应为 18 位")
        return v.upper()


class VisitCreate(BaseModel):
    patient_id: int
    visit_date: date
    department: str
    doctor: str
    diagnosis: str
    prescription: str = ""

    @field_validator("patient_id")
    @classmethod
    def patient_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("病人 ID 必须为正整数")
        return v

    @field_validator("department", "doctor", "diagnosis")
    @classmethod
    def fields_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("科室/医生/诊断不能为空")
        return v


class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    visit_date: date
    department: str
    doctor: str
    diagnosis: str
    prescription: str
    created_at: datetime


class PatientWithVisits(PatientOut):
    visits: list[VisitOut] = []

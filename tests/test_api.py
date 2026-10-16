"""接口自测:pytest + FastAPI TestClient。"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_PATIENT = {
    "name": "张三",
    "gender": "男",
    "birth_date": "1990-05-20",
    "phone": "13800000001",
    "id_card": "110101199005200011",
    "address": "北京市朝阳区",
}


def _create_patient(**overrides):
    payload = {**SAMPLE_PATIENT, **overrides}
    return client.post("/api/patients", json=payload)


@pytest.fixture(autouse=True)
def clean_patient():
    """测试后清理:删除测试产生的病人数据。"""
    yield
    resp = client.get("/api/patients", params={"name": "张三", "limit": 100})
    for p in resp.json():
        client.delete(f"/api/patients/{p['id']}")


def test_create_patient_success():
    resp = _create_patient()
    assert resp.status_code == 201
    assert resp.json()["name"] == "张三"


def test_create_patient_duplicate_phone_conflict():
    """主键/唯一约束冲突应返回 409。"""
    assert _create_patient().status_code == 201
    resp = _create_patient(id_card="110101199005200022")  # 手机号重复
    assert resp.status_code == 409


def test_create_patient_invalid_phone():
    """非法手机号应被参数校验拦截。"""
    resp = _create_patient(phone="12345")
    assert resp.status_code == 422


def test_create_patient_blank_name():
    """空姓名应被拦截。"""
    resp = _create_patient(name="  ")
    assert resp.status_code == 422


def test_get_patient_not_found():
    resp = client.get("/api/patients/999999")
    assert resp.status_code == 404


def test_visit_time_range_filter():
    """时间段筛选查询:只返回区间内的记录。"""
    p = _create_patient().json()
    for d in ("2024-01-10", "2024-03-15", "2024-06-01"):
        client.post(
            "/api/visits",
            json={
                "patient_id": p["id"],
                "visit_date": d,
                "department": "内科",
                "doctor": "李医生",
                "diagnosis": "感冒",
                "prescription": "多喝热水",
            },
        )

    resp = client.get(
        "/api/visits",
        params={"start_date": "2024-02-01", "end_date": "2024-05-01"},
    )
    assert resp.status_code == 200
    dates = [v["visit_date"] for v in resp.json()]
    assert dates == ["2024-03-15"]


def test_visit_invalid_date_range():
    resp = client.get(
        "/api/visits",
        params={"start_date": "2024-06-01", "end_date": "2024-01-01"},
    )
    assert resp.status_code == 422


def test_visit_patient_not_found():
    resp = client.post(
        "/api/visits",
        json={
            "patient_id": 999999,
            "visit_date": "2024-01-01",
            "department": "内科",
            "doctor": "李医生",
            "diagnosis": "感冒",
        },
    )
    assert resp.status_code == 404


def test_health():
    assert client.get("/health").json() == {"status": "ok"}

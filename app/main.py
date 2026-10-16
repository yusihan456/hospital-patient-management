"""医院病人信息管理系统 API 入口。"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.logger import logger
from app.routers import patients, visits

app = FastAPI(
    title="医院病人信息管理系统",
    description="病人基础信息与就诊记录管理 RESTful API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(visits.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件:记录每个接口的请求与响应状态。"""
    logger.info("请求 %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("响应 %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(OperationalError)
async def db_connection_error_handler(request: Request, exc: OperationalError):
    """捕获数据库连接异常,返回统一错误响应。"""
    logger.error("数据库连接异常: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "数据库服务不可用,请稍后重试"},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("未处理异常: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

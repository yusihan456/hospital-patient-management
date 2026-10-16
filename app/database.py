"""数据库连接管理:SQLAlchemy 引擎与会话。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # 取连接前先探测,避免使用失效连接
    pool_recycle=3600,    # 连接超时回收,防止 MySQL wait_timeout 断连
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖:为每个请求提供独立会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 医院病人信息管理系统

用 FastAPI + MySQL 写的一个病人信息管理后端,支持病人基础信息和就诊记录的管理,项目不大,主要是练手 RESTful API 和数据库设计。

## 主要功能

- 病人信息的增删改查,就诊记录的新增和查询
- 就诊记录支持按时间段筛选(动态拼 SQL 条件)
- 给 visit_date、patient_id 这些常查的字段加了索引
- 接口参数校验,手机号、身份证格式不对会直接拦截
- 处理了主键冲突、唯一约束冲突、数据库连接失败这些异常情况
- 日志会写到控制台和 logs/ 目录,出问题好排查

## 环境

- Python 3.12
- MySQL 8.x
- 依赖见 requirements.txt

## 跑起来

先建库建表:

```bash
mysql -u root -p < sql/init.sql
```

改一下 `.env` 里的数据库配置(模板是 `.env.example`):

```bash
cp .env.example .env
```

装依赖、启动:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

起来之后 Swagger 文档在 http://127.0.0.1:8000/docs,健康检查是 http://127.0.0.1:8000/health。

测试:

```bash
pytest tests/ -v
```

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/patients | 新增病人 |
| GET | /api/patients | 病人列表,支持分页和按姓名模糊查 |
| GET | /api/patients/{id} | 病人详情,带上他的就诊记录 |
| PUT | /api/patients/{id} | 更新病人信息 |
| DELETE | /api/patients/{id} | 删除病人,就诊记录会级联删掉 |
| POST | /api/visits | 新增就诊记录 |
| GET | /api/visits | 按时间段筛选就诊记录 |

时间段查询例子:

```
GET /api/visits?start_date=2024-03-01&end_date=2024-06-30&patient_id=1&department=内科
```

## 数据库设计

两张表:`patients`(病人基础信息)和 `visits`(就诊记录)。

`visits.patient_id` 是外键,指向 `patients.id`,建了 ON DELETE CASCADE,删病人时他的就诊记录一起删。

`phone` 和 `id_card` 建了唯一索引,重复插入会返回 409。

具体字段和索引见 `sql/init.sql`,里面有注释。

## 目录结构

```
app/
  main.py        # 入口,注册路由和异常处理
  config.py      # 读 .env 配置
  database.py    # SQLAlchemy 引擎和会话
  models.py      # 表模型
  schemas.py     # 请求参数校验
  logger.py      # 日志配置
  routers/
    patients.py  # 病人接口
    visits.py    # 就诊记录接口
sql/init.sql     # 建库建表脚本
tests/           # 接口测试
```

# 医院病人信息管理系统

基于 **FastAPI + MySQL** 的医院病人信息管理系统,提供病人基础信息与就诊记录的 RESTful API。

## 功能特性

- 病人基础信息 CRUD(增删改查),就诊记录管理
- 就诊记录时间段筛选查询,动态拼接 SQL 条件
- 高频查询字段(就诊日期、病人 ID、姓名、手机号)建立索引,降低查询耗时
- 完善的参数校验:拦截空值与非法输入(手机号、身份证、日期区间)
- 统一异常处理:数据库连接异常、主键冲突、唯一约束冲突
- 日志模块:控制台 + 滚动文件双输出,记录接口请求与报错信息
- 接口自测:13 个 pytest 测试用例覆盖正常与异常场景

## 技术栈

- Python 3.12 / FastAPI / Uvicorn
- SQLAlchemy 2.0 + PyMySQL
- MySQL 8.4
- Pydantic v2 参数校验

## 快速开始

### 1. 初始化数据库

```bash
mysql -u root -p < sql/init.sql
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env,填写 DB_USER / DB_PASSWORD
```

### 3. 安装依赖并启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

服务启动后访问:

- API 文档(Swagger): http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health

### 4. 运行自测

```bash
pytest tests/ -v
```

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/patients | 新增病人 |
| GET | /api/patients | 病人列表(分页 + 姓名模糊搜索) |
| GET | /api/patients/{id} | 病人详情(含就诊记录) |
| PUT | /api/patients/{id} | 更新病人信息 |
| DELETE | /api/patients/{id} | 删除病人(级联删除就诊记录) |
| POST | /api/visits | 新增就诊记录 |
| GET | /api/visits | 时间段筛选查询就诊记录 |

### 时间段筛选示例

```
GET /api/visits?start_date=2024-03-01&end_date=2024-06-30&patient_id=1&department=内科
```

## 数据库设计

**patients(病人基础信息表)**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT UNSIGNED | PK, AUTO_INCREMENT | 病人 ID |
| name | VARCHAR(50) | NOT NULL, INDEX | 姓名 |
| gender | VARCHAR(4) | NOT NULL | 性别 |
| birth_date | DATE | NOT NULL | 出生日期 |
| phone | VARCHAR(20) | UNIQUE, INDEX | 手机号 |
| id_card | VARCHAR(18) | UNIQUE | 身份证号 |
| address | VARCHAR(200) | - | 住址 |

**visits(就诊记录表)**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INT UNSIGNED | PK, AUTO_INCREMENT | 记录 ID |
| patient_id | INT UNSIGNED | FK -> patients.id, INDEX | 病人 ID |
| visit_date | DATE | NOT NULL, INDEX | 就诊日期 |
| department | VARCHAR(50) | NOT NULL | 就诊科室 |
| doctor | VARCHAR(50) | NOT NULL | 接诊医生 |
| diagnosis | TEXT | NOT NULL | 诊断结果 |
| prescription | TEXT | - | 处方/医嘱 |

> 索引设计:visit_date、patient_id 为高频查询字段建立普通索引;phone、id_card 建立唯一索引兼顾查询与数据完整性;外键 ON DELETE CASCADE 保证删除病人时联动清理就诊记录。

## 项目结构

```
hospital-patient-management/
├── app/
│   ├── main.py           # FastAPI 入口 + 异常处理 + 请求日志中间件
│   ├── config.py         # .env 配置读取
│   ├── database.py       # 数据库引擎与会话管理
│   ├── models.py         # SQLAlchemy 数据模型
│   ├── schemas.py        # Pydantic 参数校验模型
│   ├── logger.py         # 日志模块
│   └── routers/
│       ├── patients.py   # 病人 CRUD 接口
│       └── visits.py     # 就诊记录 + 时间段筛选接口
├── sql/init.sql          # 建库建表 + 索引脚本
├── tests/test_api.py     # 接口自测
└── requirements.txt
```

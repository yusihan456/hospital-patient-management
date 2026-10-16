-- 医院病人信息管理系统 初始化脚本
-- 执行方式: mysql -u root -p < sql/init.sql

CREATE DATABASE IF NOT EXISTS hospital_patient
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE hospital_patient;

-- 病人基础信息表
CREATE TABLE IF NOT EXISTS patients (
  id         INT UNSIGNED     NOT NULL AUTO_INCREMENT COMMENT '病人ID(主键)',
  name       VARCHAR(50)      NOT NULL                COMMENT '姓名',
  gender     VARCHAR(4)       NOT NULL                COMMENT '性别:男/女',
  birth_date DATE             NOT NULL                COMMENT '出生日期',
  phone      VARCHAR(20)      NOT NULL                COMMENT '手机号',
  id_card    VARCHAR(18)      NOT NULL                COMMENT '身份证号',
  address    VARCHAR(200)     NOT NULL DEFAULT ''     COMMENT '住址',
  created_at DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_phone (phone),
  UNIQUE KEY uk_id_card (id_card),
  KEY idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='病人基础信息表';

-- 就诊记录表
CREATE TABLE IF NOT EXISTS visits (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID(主键)',
  patient_id  INT UNSIGNED NOT NULL                COMMENT '病人ID(外键)',
  visit_date  DATE         NOT NULL                COMMENT '就诊日期',
  department  VARCHAR(50)  NOT NULL                COMMENT '就诊科室',
  doctor      VARCHAR(50)  NOT NULL                COMMENT '接诊医生',
  diagnosis   TEXT         NOT NULL                COMMENT '诊断结果',
  prescription TEXT        NOT NULL                COMMENT '处方/医嘱',
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_visits_visit_date (visit_date),
  KEY idx_visits_patient_id (patient_id),
  CONSTRAINT fk_visits_patient FOREIGN KEY (patient_id)
    REFERENCES patients (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='就诊记录表';

-- 高频查询字段索引说明:
--   idx_visits_visit_date 支持按时间段筛选就诊记录
--   idx_visits_patient_id 支持按病人查询就诊历史
--   idx_name / uk_phone / uk_id_card 加速病人查找并保证唯一性

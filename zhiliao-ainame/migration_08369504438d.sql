-- Migration: add user email_code model
-- Revision ID: 08369504438d
-- Revises: (base)
-- Create Date: 2025-12-02 13:30:23.386242

-- ============================================
-- Upgrade SQL (将数据库从旧版本升级到新版本)
-- ============================================

-- 如果 alembic_version 表不存在，先创建它（首次迁移时需要）
CREATE TABLE IF NOT EXISTS `alembic_version` (
    `version_num` VARCHAR(32) NOT NULL,
    PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建 email_code 表
CREATE TABLE `email_code` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(100) NOT NULL,
    `code` VARCHAR(10) NOT NULL,
    `created_time` DATETIME NOT NULL,
    CONSTRAINT `pk_email_code` PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建 user 表
CREATE TABLE `user` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `email` VARCHAR(100) NOT NULL,
    `username` VARCHAR(100) NOT NULL,
    `_password` VARCHAR(200) NOT NULL,
    CONSTRAINT `pk_user` PRIMARY KEY (`id`),
    CONSTRAINT `uq_user_email` UNIQUE (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 更新 Alembic 版本表
INSERT INTO `alembic_version` (`version_num`) VALUES ('08369504438d');

-- ============================================
-- Downgrade SQL (将数据库从新版本降级到旧版本)
-- ============================================

-- 删除 user 表
-- DROP TABLE IF EXISTS `user`;

-- 删除 email_code 表
-- DROP TABLE IF EXISTS `email_code`;

-- 删除 Alembic 版本记录
-- DELETE FROM `alembic_version` WHERE `version_num` = '08369504438d';

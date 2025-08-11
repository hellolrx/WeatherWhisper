-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS weatherwhisper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE weatherwhisper;

-- 创建用户并授权（如果不存在）
CREATE USER IF NOT EXISTS 'weatheruser'@'%' IDENTIFIED BY 'weatherpass123';
GRANT ALL PRIVILEGES ON weatherwhisper.* TO 'weatheruser'@'%';
FLUSH PRIVILEGES;

-- 显示数据库信息
SHOW DATABASES;
SELECT USER(), CURRENT_USER();

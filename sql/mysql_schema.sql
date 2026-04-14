-- 创建数据库
CREATE DATABASE IF NOT EXISTS legal_risk_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE legal_risk_app;

-- 创建 users 表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at VARCHAR(50) NOT NULL,
    last_login VARCHAR(50),
    role VARCHAR(20) DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建 reports 表，添加 user_id 字段
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    created_at VARCHAR(50) NOT NULL,
    title TEXT,
    input_content LONGTEXT,
    final_report LONGTEXT,
    expert1_report LONGTEXT,
    expert2_report LONGTEXT,
    expert3_report LONGTEXT,
    pdf_path TEXT,
    txt1_path TEXT,
    txt2_path TEXT,
    txt3_path TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建 user_configs 表
CREATE TABLE IF NOT EXISTS user_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    api_key TEXT,
    base_url TEXT,
    model TEXT,
    prompt_configs TEXT,
    created_at VARCHAR(50) NOT NULL,
    updated_at VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认管理员用户（用户名：admin，密码：admin123）
-- 密码使用 SHA256 哈希：admin123 -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a
INSERT INTO users (username, password, email, created_at, role) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a', 'admin@example.com', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), 'admin')
ON DUPLICATE KEY UPDATE username=username;

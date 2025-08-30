-- =====================
-- API Gateway / User Service Database Schema
-- =====================

CREATE DATABASE IF NOT EXISTS gateway_db;
USE gateway_db;

-- =====================
-- 👤 Usuarios (Users)
-- =====================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin', 'teacher') DEFAULT 'student',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_picture_url VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);

-- =====================
-- 🔑 User Sessions
-- =====================
CREATE TABLE user_sessions (
    id VARCHAR(100) PRIMARY KEY,  -- Session token
    user_id INT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_active (is_active)
);

-- =====================
-- 🔐 API Keys (for service-to-service communication)
-- =====================
CREATE TABLE api_keys (
    id VARCHAR(100) PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    permissions JSON,  -- Array of allowed operations
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    INDEX idx_service_name (service_name),
    INDEX idx_active (is_active),
    INDEX idx_expires_at (expires_at)
);

-- =====================
-- 📊 Request Logs (for monitoring and rate limiting)
-- =====================
CREATE TABLE request_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    api_key_id VARCHAR(100) NULL,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    status_code INT NOT NULL,
    response_time_ms INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    correlation_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_correlation_id (correlation_id),
    INDEX idx_status_code (status_code)
);

-- =====================
-- 🌱 Datos de prueba migrados
-- =====================

-- Usuarios (manteniendo IDs originales para migración)
INSERT INTO users (id, username, email, hashed_password, role, first_name, last_name, email_verified, is_active) VALUES
(1, 'santiago', 'santiago@example.com', 'hashed_pw_demo', 'student', 'Santiago', NULL, TRUE, TRUE),
(2, 'admin1', 'admin@example.com', 'hashed_pw_admin', 'admin', 'Admin', 'User', TRUE, TRUE);

-- API Keys para comunicación entre servicios
INSERT INTO api_keys (id, service_name, key_hash, permissions, is_active) VALUES
('key_syllabus_001', 'syllabus-service', 'hashed_key_syllabus', '["read:users", "read:subjects"]', TRUE),
('key_subject_001', 'subject-service', 'hashed_key_subject', '["read:users"]', TRUE),
('key_file_001', 'file-service', 'hashed_key_file', '["read:users"]', TRUE),
('key_config_001', 'config-service', 'hashed_key_config', '["read:users", "read:config"]', TRUE);
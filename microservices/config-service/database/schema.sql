-- =====================
-- Configuration Service Database Schema
-- =====================

CREATE DATABASE IF NOT EXISTS config_db;
USE config_db;

-- =====================
-- ⚙️ Application Configuration
-- =====================
CREATE TABLE app_configurations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL,
    config_value JSON NOT NULL,
    environment ENUM('development', 'staging', 'production', 'all') DEFAULT 'all',
    service_name VARCHAR(50),  -- NULL means global config
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,  -- For secrets/passwords
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,  -- User ID who created the config
    UNIQUE KEY unique_config (config_key, environment, service_name),
    INDEX idx_service_name (service_name),
    INDEX idx_environment (environment),
    INDEX idx_active (is_active),
    INDEX idx_config_key (config_key)
);

-- =====================
-- 🚩 Feature Flags
-- =====================
CREATE TABLE feature_flags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flag_name VARCHAR(100) NOT NULL,
    flag_key VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_enabled BOOLEAN DEFAULT FALSE,
    environment ENUM('development', 'staging', 'production', 'all') DEFAULT 'all',
    service_name VARCHAR(50),  -- NULL means global flag
    rollout_percentage INT DEFAULT 0,  -- 0-100 for gradual rollout
    conditions JSON,  -- Complex conditions for flag activation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    created_by INT,
    INDEX idx_flag_key (flag_key),
    INDEX idx_service_name (service_name),
    INDEX idx_environment (environment),
    INDEX idx_enabled (is_enabled),
    INDEX idx_expires_at (expires_at)
);

-- =====================
-- 📈 Configuration History
-- =====================
CREATE TABLE config_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    config_id INT NOT NULL,
    action ENUM('created', 'updated', 'deleted') NOT NULL,
    old_value JSON,
    new_value JSON,
    changed_by INT,
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (config_id) REFERENCES app_configurations(id) ON DELETE CASCADE,
    INDEX idx_config_id (config_id),
    INDEX idx_created_at (created_at),
    INDEX idx_changed_by (changed_by)
);

-- =====================
-- 🌱 Configuraciones iniciales
-- =====================

-- Configuraciones globales del sistema
INSERT INTO app_configurations (config_key, config_value, environment, service_name, description, is_sensitive) VALUES
('database.connection_pool.max_size', '20', 'all', NULL, 'Maximum database connection pool size', FALSE),
('database.connection_pool.timeout', '30', 'all', NULL, 'Database connection timeout in seconds', FALSE),
('logging.level', '"INFO"', 'production', NULL, 'Default logging level for production', FALSE),
('logging.level', '"DEBUG"', 'development', NULL, 'Default logging level for development', FALSE),
('cors.allowed_origins', '["http://localhost:3000", "http://localhost:8080"]', 'development', NULL, 'Allowed CORS origins for development', FALSE),
('cors.allowed_origins', '["https://aurora.example.com"]', 'production', NULL, 'Allowed CORS origins for production', FALSE);

-- Configuraciones específicas por servicio
INSERT INTO app_configurations (config_key, config_value, environment, service_name, description, is_sensitive) VALUES
('file_storage.max_file_size', '52428800', 'all', 'file-service', 'Maximum file size in bytes (50MB)', FALSE),
('file_storage.allowed_types', '["pdf", "doc", "docx", "txt", "md"]', 'all', 'file-service', 'Allowed file types for upload', FALSE),
('syllabus.auto_publish', 'false', 'all', 'syllabus-service', 'Auto-publish syllabus after creation', FALSE),
('subject.max_credits', '10', 'all', 'subject-service', 'Maximum credits per subject', FALSE),
('api_gateway.rate_limit.requests_per_minute', '100', 'all', 'api-gateway', 'Rate limit for API requests', FALSE);

-- Feature flags iniciales
INSERT INTO feature_flags (flag_name, flag_key, description, is_enabled, environment, service_name, rollout_percentage) VALUES
('New Syllabus Editor', 'new_syllabus_editor', 'Enable the new rich text syllabus editor', FALSE, 'development', 'syllabus-service', 0),
('Advanced File Search', 'advanced_file_search', 'Enable advanced search capabilities in file service', TRUE, 'development', 'file-service', 100),
('Repository Auto-Sync', 'repository_auto_sync', 'Enable automatic repository synchronization', FALSE, 'all', 'file-service', 25),
('Multi-tenant Support', 'multi_tenant_support', 'Enable multi-tenant functionality', FALSE, 'all', NULL, 0),
('Enhanced Analytics', 'enhanced_analytics', 'Enable enhanced user analytics and tracking', TRUE, 'production', 'api-gateway', 50);
-- =====================
-- File Service Database Schema
-- =====================

CREATE DATABASE IF NOT EXISTS file_db;
USE file_db;

-- =====================
-- 📂 Files
-- =====================
CREATE TABLE files (
    id VARCHAR(100) PRIMARY KEY,  -- UUID for file identification
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    checksum VARCHAR(64) NOT NULL,  -- SHA-256 hash
    user_id INT NOT NULL,           -- Owner of the file
    service_name VARCHAR(50) NOT NULL,  -- Which service uploaded it
    entity_type VARCHAR(50),        -- Type of entity (syllabus, repository, etc.)
    entity_id VARCHAR(100),         -- ID of the related entity
    storage_provider ENUM('local', 's3', 'gcs', 'azure') DEFAULT 'local',
    storage_metadata JSON,          -- Provider-specific metadata
    status ENUM('uploading', 'available', 'processing', 'deleted') DEFAULT 'uploading',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_service_entity (service_name, entity_type, entity_id),
    INDEX idx_status (status),
    INDEX idx_checksum (checksum)
);

-- =====================
-- 📂 Repositorios (Repositories)
-- =====================
CREATE TABLE repositories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    provider ENUM('github', 'gitlab', 'bitbucket', 'local') NOT NULL,
    access_token_encrypted TEXT,    -- Encrypted access token
    branch VARCHAR(100) DEFAULT 'main',
    last_sync DATETIME,
    sync_status ENUM('never', 'syncing', 'success', 'failed') DEFAULT 'never',
    sync_error TEXT,
    metadata JSON,                  -- Repository metadata (stars, forks, etc.)
    status ENUM('active', 'inactive', 'archived') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_provider (provider),
    INDEX idx_status (status),
    INDEX idx_sync_status (sync_status)
);

-- =====================
-- 📁 Repository Files (for synced files)
-- =====================
CREATE TABLE repository_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repository_id INT NOT NULL,
    file_id VARCHAR(100) NOT NULL,  -- Reference to files table
    relative_path VARCHAR(500) NOT NULL,
    commit_hash VARCHAR(40),
    last_modified DATETIME,
    file_type ENUM('code', 'documentation', 'config', 'other') DEFAULT 'other',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    UNIQUE KEY unique_repo_path (repository_id, relative_path),
    INDEX idx_file_type (file_type),
    INDEX idx_commit_hash (commit_hash)
);

-- =====================
-- 🌱 Datos de prueba migrados
-- =====================

-- Archivos de sílabos existentes
INSERT INTO files (id, original_filename, stored_filename, file_path, file_size, mime_type, checksum, user_id, service_name, entity_type, entity_id, status) VALUES
('file_001', 'intro_prog.pdf', 'intro_prog_20231201.pdf', 'syllabus/intro_prog.pdf', 1024000, 'application/pdf', 'abc123def456', 1, 'syllabus-service', 'syllabus', '1', 'available'),
('file_002', 'matematicas_discretas.pdf', 'matematicas_discretas_20231201.pdf', 'syllabus/matematicas_discretas.pdf', 2048000, 'application/pdf', 'def456ghi789', 1, 'syllabus-service', 'syllabus', '2', 'available'),
('file_003', 'estructuras_datos.pdf', 'estructuras_datos_20231201.pdf', 'syllabus/estructuras_datos.pdf', 1536000, 'application/pdf', 'ghi789jkl012', 1, 'syllabus-service', 'syllabus', '3', 'available'),
('file_004', 'bases_datos.pdf', 'bases_datos_20231201.pdf', 'syllabus/bases_datos.pdf', 1792000, 'application/pdf', 'jkl012mno345', 1, 'syllabus-service', 'syllabus', '4', 'available');

-- Repositorios (manteniendo IDs originales para migración)
INSERT INTO repositories (id, user_id, name, url, provider, last_sync, sync_status, status) VALUES
(1, 1, 'intro-prog-project', 'https://github.com/santi/intro-prog', 'github', NOW(), 'success', 'active'),
(2, 1, 'data-structures', 'https://github.com/santi/data-structures', 'github', NOW(), 'success', 'active'),
(3, 1, 'db-labs', 'https://gitlab.com/santi/db-labs', 'gitlab', NOW(), 'success', 'active');
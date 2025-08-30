-- =====================
-- Syllabus Service Database Schema
-- =====================

CREATE DATABASE IF NOT EXISTS syllabus_db;
USE syllabus_db;

-- =====================
-- 📚 Semestres (Semesters)
-- =====================
CREATE TABLE semesters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- Reference to user in API Gateway/User Service
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_dates (start_date, end_date)
);

-- =====================
-- 📄 Sílabos (Syllabus)
-- =====================
CREATE TABLE syllabus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,  -- Reference to subject in Subject Service
    semester_id INT NOT NULL, -- Local reference for queries
    user_id INT NOT NULL,     -- Denormalized for performance
    file_url VARCHAR(255),
    file_id VARCHAR(100),     -- Reference to file in File Service
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE,
    INDEX idx_subject_id (subject_id),
    INDEX idx_semester_id (semester_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- =====================
-- 🌱 Datos de prueba migrados
-- =====================

-- Semestres (manteniendo IDs originales para migración)
INSERT INTO semesters (id, user_id, name, start_date, end_date) VALUES
(1, 1, 'Semestre 1 - 2023A', '2023-01-15', '2023-06-30'),
(2, 1, 'Semestre 2 - 2023B', '2023-08-01', '2023-12-20');

-- Sílabos (actualizados con nuevos campos)
INSERT INTO syllabus (id, subject_id, semester_id, user_id, file_url, file_id, status) VALUES
(1, 1, 1, 1, 'syllabus/intro_prog.pdf', 'file_001', 'published'),
(2, 2, 1, 1, 'syllabus/matematicas_discretas.pdf', 'file_002', 'published'),
(3, 3, 2, 1, 'syllabus/estructuras_datos.pdf', 'file_003', 'published'),
(4, 4, 2, 1, 'syllabus/bases_datos.pdf', 'file_004', 'published');
-- =====================
-- Subject Service Database Schema
-- =====================

CREATE DATABASE IF NOT EXISTS subject_db;
USE subject_db;

-- =====================
-- 🏫 Materias (Subjects)
-- =====================
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    semester_id INT NOT NULL,  -- Reference to semester in Syllabus Service
    user_id INT NOT NULL,      -- Denormalized for performance and authorization
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),          -- Course code (e.g., CS101)
    credits INT,
    description TEXT,
    prerequisites JSON,        -- Array of prerequisite subject IDs
    status ENUM('active', 'inactive', 'archived') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_semester_id (semester_id),
    INDEX idx_user_id (user_id),
    INDEX idx_code (code),
    INDEX idx_status (status)
);

-- =====================
-- 📊 Subject Metadata
-- =====================
CREATE TABLE subject_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_subject_key (subject_id, metadata_key),
    INDEX idx_metadata_key (metadata_key)
);

-- =====================
-- 🌱 Datos de prueba migrados
-- =====================

-- Materias (manteniendo IDs originales para migración)
INSERT INTO subjects (id, semester_id, user_id, name, credits, code, description, status) VALUES
(1, 1, 1, 'Introducción a la Programación', 5, 'CS101', 'Fundamentos de programación y algoritmos básicos', 'active'),
(2, 1, 1, 'Matemáticas Discretas', 4, 'MATH201', 'Lógica, conjuntos, grafos y matemáticas para ciencias de la computación', 'active'),
(3, 2, 1, 'Estructuras de Datos', 5, 'CS201', 'Estructuras de datos fundamentales y algoritmos', 'active'),
(4, 2, 1, 'Bases de Datos', 4, 'CS301', 'Diseño y gestión de bases de datos relacionales', 'active');

-- Metadata de ejemplo
INSERT INTO subject_metadata (subject_id, metadata_key, metadata_value) VALUES
(1, 'difficulty_level', '"beginner"'),
(1, 'programming_languages', '["Python", "Java"]'),
(2, 'difficulty_level', '"intermediate"'),
(2, 'topics', '["Logic", "Set Theory", "Graph Theory"]'),
(3, 'difficulty_level', '"intermediate"'),
(3, 'prerequisites', '[1]'),
(4, 'difficulty_level', '"advanced"'),
(4, 'prerequisites', '[1, 3]');
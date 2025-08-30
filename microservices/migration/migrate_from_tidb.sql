-- =====================
-- Migration Script from TiDB Monolith to Microservices
-- =====================

-- This script helps migrate data from the existing aurora_db (TiDB) 
-- to the new microservices database structure

-- =====================
-- Step 1: Export data from TiDB (run these on your TiDB cluster)
-- =====================

-- Export users
-- SELECT * FROM aurora_db.users INTO OUTFILE '/tmp/users_export.csv' 
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

-- Export semesters  
-- SELECT * FROM aurora_db.semesters INTO OUTFILE '/tmp/semesters_export.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

-- Export subjects
-- SELECT * FROM aurora_db.subjects INTO OUTFILE '/tmp/subjects_export.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

-- Export syllabus
-- SELECT * FROM aurora_db.syllabus INTO OUTFILE '/tmp/syllabus_export.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

-- Export repositories
-- SELECT * FROM aurora_db.repositories INTO OUTFILE '/tmp/repositories_export.csv'
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

-- =====================
-- Step 2: Data Transformation Queries
-- =====================

-- Transform users data for API Gateway
-- Add new columns with default values
SELECT 
    id,
    username,
    email,
    hashed_password,
    role,
    NULL as first_name,
    NULL as last_name,
    NULL as profile_picture_url,
    FALSE as email_verified,
    TRUE as is_active,
    NULL as last_login,
    NOW() as created_at,
    NOW() as updated_at
FROM aurora_db.users;

-- Transform semesters data for Syllabus Service
-- Keep existing structure, add timestamps
SELECT 
    id,
    user_id,
    name,
    start_date,
    end_date,
    NOW() as created_at,
    NOW() as updated_at
FROM aurora_db.semesters;

-- Transform subjects data for Subject Service
-- Add new fields with defaults
SELECT 
    s.id,
    s.semester_id,
    sem.user_id,  -- Get user_id from semester
    s.name,
    NULL as code,  -- Will need to be populated manually
    s.credits,
    NULL as description,
    NULL as prerequisites,
    'active' as status,
    NOW() as created_at,
    NOW() as updated_at
FROM aurora_db.subjects s
JOIN aurora_db.semesters sem ON s.semester_id = sem.id;

-- Transform syllabus data for Syllabus Service
-- Add new fields and generate file IDs
SELECT 
    syl.id,
    syl.subject_id,
    s.semester_id,
    sem.user_id,
    syl.file_url,
    CONCAT('file_', LPAD(syl.id, 3, '0')) as file_id,
    'published' as status,
    1 as version,
    NOW() as created_at,
    NOW() as updated_at
FROM aurora_db.syllabus syl
JOIN aurora_db.subjects s ON syl.subject_id = s.id
JOIN aurora_db.semesters sem ON s.semester_id = sem.id;

-- Transform repositories data for File Service
-- Add new fields with defaults
SELECT 
    id,
    user_id,
    name,
    url,
    provider,
    NULL as access_token_encrypted,
    'main' as branch,
    last_sync,
    CASE 
        WHEN last_sync IS NOT NULL THEN 'success'
        ELSE 'never'
    END as sync_status,
    NULL as sync_error,
    NULL as metadata,
    'active' as status,
    NOW() as created_at,
    NOW() as updated_at
FROM aurora_db.repositories;

-- Generate file records for existing syllabus files
SELECT 
    CONCAT('file_', LPAD(syl.id, 3, '0')) as id,
    SUBSTRING_INDEX(syl.file_url, '/', -1) as original_filename,
    CONCAT(SUBSTRING_INDEX(syl.file_url, '/', -1), '_', DATE_FORMAT(NOW(), '%Y%m%d')) as stored_filename,
    syl.file_url as file_path,
    1024000 as file_size,  -- Default size, needs to be updated
    'application/pdf' as mime_type,
    MD5(syl.file_url) as checksum,  -- Temporary checksum
    sem.user_id,
    'syllabus-service' as service_name,
    'syllabus' as entity_type,
    syl.id as entity_id,
    'local' as storage_provider,
    NULL as storage_metadata,
    'available' as status,
    NOW() as created_at,
    NOW() as updated_at,
    NULL as deleted_at
FROM aurora_db.syllabus syl
JOIN aurora_db.subjects s ON syl.subject_id = s.id
JOIN aurora_db.semesters sem ON s.semester_id = sem.id
WHERE syl.file_url IS NOT NULL;

-- =====================
-- Step 3: Validation Queries
-- =====================

-- Verify data consistency after migration
-- Check user count matches
-- SELECT 'Users' as table_name, COUNT(*) as original_count FROM aurora_db.users
-- UNION ALL
-- SELECT 'Users (migrated)', COUNT(*) FROM gateway_db.users;

-- Check semester count matches  
-- SELECT 'Semesters' as table_name, COUNT(*) as original_count FROM aurora_db.semesters
-- UNION ALL
-- SELECT 'Semesters (migrated)', COUNT(*) FROM syllabus_db.semesters;

-- Check subject count matches
-- SELECT 'Subjects' as table_name, COUNT(*) as original_count FROM aurora_db.subjects  
-- UNION ALL
-- SELECT 'Subjects (migrated)', COUNT(*) FROM subject_db.subjects;

-- Check syllabus count matches
-- SELECT 'Syllabus' as table_name, COUNT(*) as original_count FROM aurora_db.syllabus
-- UNION ALL  
-- SELECT 'Syllabus (migrated)', COUNT(*) FROM syllabus_db.syllabus;

-- Check repository count matches
-- SELECT 'Repositories' as table_name, COUNT(*) as original_count FROM aurora_db.repositories
-- UNION ALL
-- SELECT 'Repositories (migrated)', COUNT(*) FROM file_db.repositories;
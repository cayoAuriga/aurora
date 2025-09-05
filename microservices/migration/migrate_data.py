#!/usr/bin/env python3
"""
Data migration script from TiDB monolith to microservices
"""
import os
import sys
import pymysql
import json
from datetime import datetime
from typing import Dict, List, Any
import hashlib
import uuid

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.logging import get_logger

logger = get_logger("migration-service")

class DatabaseMigrator:
    """Handles migration from TiDB monolith to microservices databases"""
    
    def __init__(self, source_config: Dict, target_configs: Dict):
        self.source_config = source_config
        self.target_configs = target_configs
        self.connections = {}
        
    def connect_databases(self):
        """Establish connections to all databases"""
        try:
            # Connect to source TiDB
            self.connections['source'] = pymysql.connect(**self.source_config)
            logger.info("Connected to source TiDB database")
            
            # Connect to target microservice databases
            for service, config in self.target_configs.items():
                self.connections[service] = pymysql.connect(**config)
                logger.info(f"Connected to {service} database")
                
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise
    
    def close_connections(self):
        """Close all database connections"""
        for name, conn in self.connections.items():
            if conn:
                conn.close()
                logger.info(f"Closed connection to {name}")
    
    def migrate_users(self):
        """Migrate users to API Gateway database"""
        logger.info("Starting user migration...")
        
        source_cursor = self.connections['source'].cursor(pymysql.cursors.DictCursor)
        target_cursor = self.connections['api-gateway'].cursor()
        
        try:
            # Fetch users from source
            source_cursor.execute("SELECT * FROM aurora_db.users")
            users = source_cursor.fetchall()
            
            # Insert into target
            insert_query = """
                INSERT INTO gateway_db.users 
                (id, username, email, hashed_password, role, first_name, last_name, 
                 email_verified, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for user in users:
                target_cursor.execute(insert_query, (
                    user['id'],
                    user['username'], 
                    user['email'],
                    user['hashed_password'],
                    user['role'],
                    None,  # first_name
                    None,  # last_name
                    True,  # email_verified
                    True,  # is_active
                    datetime.now(),
                    datetime.now()
                ))
            
            self.connections['api-gateway'].commit()
            logger.info(f"Migrated {len(users)} users successfully")
            
        except Exception as e:
            self.connections['api-gateway'].rollback()
            logger.error(f"User migration failed: {str(e)}")
            raise
        finally:
            source_cursor.close()
            target_cursor.close()
    
    def migrate_semesters(self):
        """Migrate semesters to Syllabus Service database"""
        logger.info("Starting semester migration...")
        
        source_cursor = self.connections['source'].cursor(pymysql.cursors.DictCursor)
        target_cursor = self.connections['syllabus-service'].cursor()
        
        try:
            # Fetch semesters from source
            source_cursor.execute("SELECT * FROM aurora_db.semesters")
            semesters = source_cursor.fetchall()
            
            # Insert into target
            insert_query = """
                INSERT INTO syllabus_db.semesters 
                (id, user_id, name, start_date, end_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for semester in semesters:
                target_cursor.execute(insert_query, (
                    semester['id'],
                    semester['user_id'],
                    semester['name'],
                    semester['start_date'],
                    semester['end_date'],
                    datetime.now(),
                    datetime.now()
                ))
            
            self.connections['syllabus-service'].commit()
            logger.info(f"Migrated {len(semesters)} semesters successfully")
            
        except Exception as e:
            self.connections['syllabus-service'].rollback()
            logger.error(f"Semester migration failed: {str(e)}")
            raise
        finally:
            source_cursor.close()
            target_cursor.close()
    
    def migrate_subjects(self):
        """Migrate subjects to Subject Service database"""
        logger.info("Starting subject migration...")
        
        source_cursor = self.connections['source'].cursor(pymysql.cursors.DictCursor)
        target_cursor = self.connections['subject-service'].cursor()
        
        try:
            # Fetch subjects with semester info
            query = """
                SELECT s.*, sem.user_id 
                FROM aurora_db.subjects s
                JOIN aurora_db.semesters sem ON s.semester_id = sem.id
            """
            source_cursor.execute(query)
            subjects = source_cursor.fetchall()
            
            # Insert into target
            insert_query = """
                INSERT INTO subject_db.subjects 
                (id, semester_id, user_id, name, credits, code, description, 
                 prerequisites, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for subject in subjects:
                # Generate a code if not exists
                code = f"SUBJ{subject['id']:03d}"
                
                target_cursor.execute(insert_query, (
                    subject['id'],
                    subject['semester_id'],
                    subject['user_id'],
                    subject['name'],
                    subject['credits'],
                    code,
                    None,  # description
                    None,  # prerequisites (JSON)
                    'active',
                    datetime.now(),
                    datetime.now()
                ))
            
            self.connections['subject-service'].commit()
            logger.info(f"Migrated {len(subjects)} subjects successfully")
            
        except Exception as e:
            self.connections['subject-service'].rollback()
            logger.error(f"Subject migration failed: {str(e)}")
            raise
        finally:
            source_cursor.close()
            target_cursor.close()
    
    def migrate_syllabus_and_files(self):
        """Migrate syllabus and create file records"""
        logger.info("Starting syllabus and file migration...")
        
        source_cursor = self.connections['source'].cursor(pymysql.cursors.DictCursor)
        syllabus_cursor = self.connections['syllabus-service'].cursor()
        file_cursor = self.connections['file-service'].cursor()
        
        try:
            # Fetch syllabus with related info
            query = """
                SELECT syl.*, s.semester_id, sem.user_id 
                FROM aurora_db.syllabus syl
                JOIN aurora_db.subjects s ON syl.subject_id = s.id
                JOIN aurora_db.semesters sem ON s.semester_id = sem.id
            """
            source_cursor.execute(query)
            syllabus_records = source_cursor.fetchall()
            
            # Insert syllabus records
            syllabus_query = """
                INSERT INTO syllabus_db.syllabus 
                (id, subject_id, semester_id, user_id, file_url, file_id, 
                 status, version, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Insert file records
            file_query = """
                INSERT INTO file_db.files 
                (id, original_filename, stored_filename, file_path, file_size, 
                 mime_type, checksum, user_id, service_name, entity_type, 
                 entity_id, storage_provider, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for record in syllabus_records:
                if record['file_url']:
                    # Generate file ID
                    file_id = f"file_{record['id']:03d}"
                    
                    # Extract filename
                    original_filename = record['file_url'].split('/')[-1]
                    stored_filename = f"{original_filename}_{datetime.now().strftime('%Y%m%d')}"
                    
                    # Generate checksum (placeholder)
                    checksum = hashlib.md5(record['file_url'].encode()).hexdigest()
                    
                    # Insert syllabus record
                    syllabus_cursor.execute(syllabus_query, (
                        record['id'],
                        record['subject_id'],
                        record['semester_id'],
                        record['user_id'],
                        record['file_url'],
                        file_id,
                        'published',
                        1,
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    # Insert file record
                    file_cursor.execute(file_query, (
                        file_id,
                        original_filename,
                        stored_filename,
                        record['file_url'],
                        1024000,  # Default size - needs to be updated
                        'application/pdf',
                        checksum,
                        record['user_id'],
                        'syllabus-service',
                        'syllabus',
                        str(record['id']),
                        'local',
                        'available',
                        datetime.now(),
                        datetime.now()
                    ))
            
            self.connections['syllabus-service'].commit()
            self.connections['file-service'].commit()
            logger.info(f"Migrated {len(syllabus_records)} syllabus records and files successfully")
            
        except Exception as e:
            self.connections['syllabus-service'].rollback()
            self.connections['file-service'].rollback()
            logger.error(f"Syllabus/file migration failed: {str(e)}")
            raise
        finally:
            source_cursor.close()
            syllabus_cursor.close()
            file_cursor.close()
    
    def migrate_repositories(self):
        """Migrate repositories to File Service database"""
        logger.info("Starting repository migration...")
        
        source_cursor = self.connections['source'].cursor(pymysql.cursors.DictCursor)
        target_cursor = self.connections['file-service'].cursor()
        
        try:
            # Fetch repositories from source
            source_cursor.execute("SELECT * FROM aurora_db.repositories")
            repositories = source_cursor.fetchall()
            
            # Insert into target
            insert_query = """
                INSERT INTO file_db.repositories 
                (id, user_id, name, url, provider, branch, last_sync, 
                 sync_status, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for repo in repositories:
                sync_status = 'success' if repo['last_sync'] else 'never'
                
                target_cursor.execute(insert_query, (
                    repo['id'],
                    repo['user_id'],
                    repo['name'],
                    repo['url'],
                    repo['provider'],
                    'main',  # default branch
                    repo['last_sync'],
                    sync_status,
                    'active',
                    datetime.now(),
                    datetime.now()
                ))
            
            self.connections['file-service'].commit()
            logger.info(f"Migrated {len(repositories)} repositories successfully")
            
        except Exception as e:
            self.connections['file-service'].rollback()
            logger.error(f"Repository migration failed: {str(e)}")
            raise
        finally:
            source_cursor.close()
            target_cursor.close()
    
    def validate_migration(self):
        """Validate that migration was successful"""
        logger.info("Validating migration...")
        
        validations = []
        
        try:
            # Check user counts
            source_cursor = self.connections['source'].cursor()
            source_cursor.execute("SELECT COUNT(*) FROM aurora_db.users")
            source_users = source_cursor.fetchone()[0]
            
            target_cursor = self.connections['api-gateway'].cursor()
            target_cursor.execute("SELECT COUNT(*) FROM gateway_db.users")
            target_users = target_cursor.fetchone()[0]
            
            validations.append(("Users", source_users, target_users, source_users == target_users))
            
            # Add more validation checks...
            
            # Print validation results
            logger.info("Migration validation results:")
            for table, source_count, target_count, is_valid in validations:
                status = "✓" if is_valid else "✗"
                logger.info(f"{status} {table}: {source_count} -> {target_count}")
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise
    
    def run_migration(self):
        """Run the complete migration process"""
        try:
            logger.info("Starting database migration from TiDB to microservices...")
            
            self.connect_databases()
            
            # Run migrations in order
            self.migrate_users()
            self.migrate_semesters()
            self.migrate_subjects()
            self.migrate_syllabus_and_files()
            self.migrate_repositories()
            
            # Validate results
            self.validate_migration()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise
        finally:
            self.close_connections()


def main():
    """Main migration function"""
    
    # Configuration for source TiDB database
    source_config = {
        'host': os.getenv('TIDB_HOST', 'localhost'),
        'port': int(os.getenv('TIDB_PORT', 4000)),
        'user': os.getenv('TIDB_USER', 'root'),
        'password': os.getenv('TIDB_PASSWORD', ''),
        'database': 'aurora_db',
        'charset': 'utf8mb4'
    }
    
    # Configuration for target microservice databases
    target_configs = {
        'api-gateway': {
            'host': os.getenv('GATEWAY_DB_HOST', 'localhost'),
            'port': int(os.getenv('GATEWAY_DB_PORT', 3307)),
            'user': os.getenv('GATEWAY_DB_USER', 'root'),
            'password': os.getenv('GATEWAY_DB_PASSWORD', 'password'),
            'database': 'gateway_db',
            'charset': 'utf8mb4'
        },
        'syllabus-service': {
            'host': os.getenv('SYLLABUS_DB_HOST', 'localhost'),
            'port': int(os.getenv('SYLLABUS_DB_PORT', 3308)),
            'user': os.getenv('SYLLABUS_DB_USER', 'root'),
            'password': os.getenv('SYLLABUS_DB_PASSWORD', 'password'),
            'database': 'syllabus_db',
            'charset': 'utf8mb4'
        },
        'subject-service': {
            'host': os.getenv('SUBJECT_DB_HOST', 'localhost'),
            'port': int(os.getenv('SUBJECT_DB_PORT', 3309)),
            'user': os.getenv('SUBJECT_DB_USER', 'root'),
            'password': os.getenv('SUBJECT_DB_PASSWORD', 'password'),
            'database': 'subject_db',
            'charset': 'utf8mb4'
        },
        'file-service': {
            'host': os.getenv('FILE_DB_HOST', 'localhost'),
            'port': int(os.getenv('FILE_DB_PORT', 3310)),
            'user': os.getenv('FILE_DB_USER', 'root'),
            'password': os.getenv('FILE_DB_PASSWORD', 'password'),
            'database': 'file_db',
            'charset': 'utf8mb4'
        }
    }
    
    # Run migration
    migrator = DatabaseMigrator(source_config, target_configs)
    migrator.run_migration()


if __name__ == "__main__":
main()
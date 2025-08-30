# Migration Guide: TiDB Cloud Microservices Migration

This guide walks you through migrating your existing Aurora application to the new microservices architecture using TiDB Cloud as the distributed database backend.

## Overview

The new architecture uses a single TiDB Cloud cluster with multiple databases for different services:

- **gateway_db** (API Gateway): Users, sessions, API keys
- **syllabus_db** (Syllabus Service): Semesters, syllabus records
- **subject_db** (Subject Service): Subjects and metadata
- **file_db** (File Service): Files and repositories
- **config_db** (Config Service): Application configuration

All services will connect to the same TiDB Cloud cluster but use different databases, providing distributed storage with ACID transactions and horizontal scalability.

## Prerequisites

1. **TiDB Cloud Access**:
   - Active TiDB Cloud cluster: `gateway01.us-east-1.prod.aws.tidbcloud.com:4000`
   - Database credentials: `3Eo7CXZzQYFQ3i5.root`
   - SSL certificate: `ca-cert.pem` (already downloaded)

2. **Install MySQL client** (for connecting to TiDB):

   ```bash
   # On Ubuntu/Debian (WSL)
   sudo apt-get install mysql-client

   # On Windows
   # Download MySQL client or use MySQL Workbench
   ```

3. **Backup existing data** (if migrating from existing system):
   ```bash
   mysqldump --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D 'aurora' --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p'[PASSWORD]' > aurora_backup.sql
   ```

## Setup Steps

### Step 1: Verify TiDB Cloud Connection

1. **Test your TiDB Cloud connection**:

   ```bash
   mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D 'aurora' --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p
   ```

2. **Verify current database structure**:

   ```bash
   # List existing databases
   mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW DATABASES;"
   
   # Check current aurora database tables
   mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D 'aurora' --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW TABLES;"
   ```

### Step 2: Create Service Databases

Create separate databases for each microservice on TiDB Cloud:

```bash
# Connect to TiDB Cloud and create databases
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "
CREATE DATABASE IF NOT EXISTS gateway_db;
CREATE DATABASE IF NOT EXISTS syllabus_db;
CREATE DATABASE IF NOT EXISTS subject_db;
CREATE DATABASE IF NOT EXISTS file_db;
CREATE DATABASE IF NOT EXISTS config_db;
"
```

### Step 3: Load Database Schemas

Run the schema creation scripts for each service on TiDB Cloud:

```bash
# API Gateway database
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D gateway_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p < microservices/api-gateway/database/schema.sql

# Syllabus Service database
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D syllabus_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p < microservices/syllabus-service/database/schema.sql

# File Service database
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D file_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p < microservices/file-service/database/schema.sql

# Config Service database
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D config_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p < microservices/config-service/database/schema.sql
```

### Step 4: Configure Migration Environment

Create a `.env` file in the `migration/` directory:

```bash
# Source Database Configuration (TiDB Cloud - existing aurora database)
SOURCE_DB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
SOURCE_DB_PORT=4000
SOURCE_DB_USER=3Eo7CXZzQYFQ3i5.root
SOURCE_DB_PASSWORD=[YOUR_PASSWORD]
SOURCE_DB_NAME=aurora
SOURCE_DB_SSL_CA=ca-cert.pem

# TiDB Cloud Configuration (same cluster, multiple databases)
TIDB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=3Eo7CXZzQYFQ3i5.root
TIDB_PASSWORD=[YOUR_PASSWORD]
TIDB_SSL_CA=ca-cert.pem

# Service Database Names (all on same TiDB Cloud cluster)
GATEWAY_DB_NAME=gateway_db
SYLLABUS_DB_NAME=syllabus_db
SUBJECT_DB_NAME=subject_db
FILE_DB_NAME=file_db
CONFIG_DB_NAME=config_db
```

### Step 5: Run Data Migration (Optional)

If migrating from an existing system, execute the automated migration script:

```bash
cd microservices/migration
python migrate_data.py
```

The script will:

1. Connect to your source database
2. Extract data from existing `aurora_db`
3. Transform and load data into TiDB microservice databases
4. Validate the migration results

### Step 6: Verify Setup

Check that databases were created correctly on TiDB Cloud:

```bash
# List all databases
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW DATABASES;"

# Check table creation in each database
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D gateway_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW TABLES;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D syllabus_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW TABLES;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D file_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW TABLES;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D config_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SHOW TABLES;"

# If you migrated data, check record counts
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D gateway_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT COUNT(*) FROM users;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D syllabus_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT COUNT(*) FROM semesters;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D file_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT COUNT(*) FROM files;"
```

## Data Mapping

### Users Table

- **From**: `aurora_db.users`
- **To**: `gateway_db.users`
- **Changes**: Added fields for profile info, email verification, activity status

### Semesters Table

- **From**: `aurora_db.semesters`
- **To**: `syllabus_db.semesters`
- **Changes**: Added created_at/updated_at timestamps

### Subjects Table

- **From**: `aurora_db.subjects`
- **To**: `subject_db.subjects`
- **Changes**:
  - Added `user_id` (denormalized from semester)
  - Added `code`, `description`, `prerequisites`, `status` fields
  - Added metadata support via `subject_metadata` table

### Syllabus Table

- **From**: `aurora_db.syllabus`
- **To**: `syllabus_db.syllabus`
- **Changes**:
  - Added `semester_id`, `user_id` (denormalized)
  - Added `file_id` reference to file service
  - Added `status`, `version` fields

### Files (New)

- **From**: `aurora_db.syllabus.file_url`
- **To**: `file_db.files`
- **Changes**: Created proper file metadata records for existing syllabus files

### Repositories Table

- **From**: `aurora_db.repositories`
- **To**: `file_db.repositories`
- **Changes**: Added fields for branch, sync status, metadata, encryption support

## Post-Migration Tasks

### 1. Update File Checksums

The migration creates placeholder checksums. Update them with actual file hashes:

```python
# Run this after migration to calculate real checksums
python update_file_checksums.py
```

### 2. Configure Service Communication

Update service configurations to use TiDB Cloud:

```yaml
# Example environment variables for microservices
environment:
  - DATABASE_URL=mysql+pymysql://3Eo7CXZzQYFQ3i5.root:[PASSWORD]@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/gateway_db?ssl_ca=ca-cert.pem&ssl_verify_cert=true
  - TIDB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
  - TIDB_PORT=4000
  - TIDB_USER=3Eo7CXZzQYFQ3i5.root
  - TIDB_SSL_CA=ca-cert.pem
  - DATABASE_NAME=gateway_db
```

### 3. Access TiDB Cloud Dashboard

Monitor your cluster performance through TiDB Cloud console:

- **TiDB Cloud Console**: https://tidbcloud.com/
- **Features**: Query performance, cluster topology, slow queries, metrics, scaling controls

### 4. Test Service Endpoints

Verify each service can connect to its database on TiDB Cloud:

```bash
# Test database connections
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D gateway_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT 'Gateway DB Connected' as status;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D syllabus_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT 'Syllabus DB Connected' as status;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D file_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT 'File DB Connected' as status;"
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D config_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT 'Config DB Connected' as status;"
```

### 4. Update Application Code

Modify your application code to:

- Use service-specific database connections
- Implement inter-service communication
- Handle distributed transactions appropriately

## TiDB Cloud Management

### Backup and Restore

```bash
# Backup all databases from TiDB Cloud
mysqldump --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p --all-databases > tidb_cloud_backup.sql

# Backup specific database
mysqldump --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D gateway_db --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p > gateway_backup.sql

# Restore from backup
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p < tidb_cloud_backup.sql
```

### Scaling the Cluster

TiDB Cloud provides automatic scaling through the web console:

- **Compute Scaling**: Adjust TiDB node count and specifications
- **Storage Scaling**: Add TiKV nodes for increased storage capacity
- **Auto-scaling**: Configure automatic scaling based on workload
- **Read Replicas**: Add read-only replicas for read-heavy workloads

## Rollback Plan

If you need to rollback to the original setup:

1. **Restore original aurora database** (if needed):

   ```bash
   # Restore from backup to original aurora database
   mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D aurora --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p < aurora_backup.sql
   ```

2. **Drop microservice databases** (if needed):

   ```bash
   mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "
   DROP DATABASE IF EXISTS gateway_db;
   DROP DATABASE IF EXISTS syllabus_db;
   DROP DATABASE IF EXISTS subject_db;
   DROP DATABASE IF EXISTS file_db;
   DROP DATABASE IF EXISTS config_db;
   "
   ```

3. **Revert application configuration** to use the original aurora database

## Troubleshooting

### Connection Issues

```bash
# Test TiDB Cloud connection
mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p -e "SELECT VERSION();"

# Check SSL certificate
ls -la ca-cert.pem

# Verify SSL certificate validity
openssl x509 -in ca-cert.pem -text -noout
```

### Performance Issues

- **Monitor with TiDB Cloud Console**: https://tidbcloud.com/
- **Check slow queries**: Use TiDB Cloud's performance insights
- **Add indexes**: TiDB supports MySQL-compatible indexing
- **Scale horizontally**: Use TiDB Cloud console to add compute/storage capacity

### Data Inconsistencies

- Run validation queries in `migrate_from_tidb.sql`
- Check migration logs for errors
- Use TiDB's ACID transactions for consistency
- Verify foreign key relationships across databases

### Common Issues

**SSL Certificate Issues**:

```bash
# Ensure ca-cert.pem is in the correct location
ls -la ca-cert.pem

# Re-download certificate from TiDB Cloud console if needed
```

**Connection Timeout**:

```bash
# Check network connectivity
ping gateway01.us-east-1.prod.aws.tidbcloud.com

# Verify firewall/security group settings allow port 4000
```

**Authentication Errors**:

- Verify username: `3Eo7CXZzQYFQ3i5.root`
- Check password is correct
- Ensure SSL mode is set to `VERIFY_IDENTITY`

## Next Steps

After successful setup:

1. **Configure microservices** to connect to their respective databases
2. **Implement service discovery** and configuration management
3. **Set up monitoring** using TiDB Dashboard and application metrics
4. **Configure automated backups** for production environments
5. **Implement distributed tracing** for cross-service requests
6. **Set up CI/CD pipelines** for each microservice
7. **Consider read replicas** for high-traffic read operations

## TiDB Advantages

- **MySQL Compatibility**: Existing MySQL applications work with minimal changes
- **Horizontal Scaling**: Add TiKV nodes to scale storage and compute
- **ACID Transactions**: Full ACID compliance across distributed storage
- **High Availability**: Built-in replication and failover
- **Real-time Analytics**: HTAP (Hybrid Transactional/Analytical Processing)
- **Cloud Native**: Kubernetes-ready architecture

## Production Considerations

- **Resource Requirements**: Minimum 4GB RAM, 8GB recommended
- **Storage**: Use persistent volumes for production data
- **Networking**: Configure proper security groups and firewalls
- **Monitoring**: Set up Prometheus/Grafana integration
- **Backup Strategy**: Implement automated daily backups
- **Security**: Enable TLS and authentication for production

## Support

For setup and migration issues:

1. Check Docker container logs: `docker-compose logs [service-name]`
2. Verify TiDB cluster status in Dashboard: http://localhost:12333
3. Test database connectivity with MySQL client
4. Review TiDB documentation: https://docs.pingcap.com/tidb/stable
5. Check migration logs in console output for data migration issues

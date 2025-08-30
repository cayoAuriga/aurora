#!/bin/bash

# TiDB Cloud Connection Script
echo -e "\033[32mConnecting to TiDB Cloud...\033[0m"

# Check if SSL certificate exists
if [ ! -f "ca-cert.pem" ]; then
    echo -e "\033[31mError: ca-cert.pem not found!\033[0m"
    echo -e "\033[33mPlease download the SSL certificate from TiDB Cloud dashboard and save it as ca-cert.pem\033[0m"
    exit 1
fi

echo -e "\033[33mTesting TiDB Cloud connection...\033[0m"

# Check if TiDB is accessible
echo -e "\033[33mTesting TiDB connection...\033[0m"
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    
    # Test connection to TiDB Cloud
    if mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D 'aurora' --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p'sgCKlsXv6OhBfMta' -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "\033[32mTiDB is ready!\033[0m"
        break
    else
        echo -e "\033[33mAttempt $attempt failed, retrying...\033[0m"
        sleep 5
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "\033[31mFailed to connect to TiDB after $max_attempts attempts\033[0m"
    exit 1
fi

echo -e "\033[32mTiDB Cloud connection successful!\033[0m"
echo -e "\033[36mConnection details:\033[0m"
echo -e "  Host: gateway01.us-east-1.prod.aws.tidbcloud.com"
echo -e "  Port: 4000"
echo -e "  User: 3Eo7CXZzQYFQ3i5.root"
echo -e "  Database: aurora"
echo ""
echo -e "\033[33mTo connect manually:\033[0m"
echo -e "mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D 'aurora' --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p"
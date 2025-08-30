#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro v3 - NEW DATABASE SETUP 🚀"
echo "Version: 2024-08-30-FINAL"
echo "=================================================="

# Wait for external services (if using external MySQL/Redis)
if [ "$WAIT_FOR_SERVICES" = "true" ]; then
    echo "Waiting for database..."
    while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-3306}; do
        sleep 1
    done
    echo "Database is ready!"
    
    if [ -n "$REDIS_HOST" ]; then
        echo "Waiting for Redis..."
        while ! nc -z ${REDIS_HOST:-localhost} ${REDIS_PORT:-6379}; do
            sleep 1
        done
        echo "Redis is ready!"
    fi
fi

# Run database setup with simple SQL approach
echo "=== GridTrader Pro Database Setup ==="
cd /app && python simple_db_setup.py

if [ $? -ne 0 ]; then
    echo "Database setup failed, exiting..."
    exit 1
fi

echo "Database setup completed successfully!"

# Start services with supervisor
echo "Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

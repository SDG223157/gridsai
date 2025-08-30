#!/bin/bash
set -e

echo "Starting GridTrader Pro..."

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

# Run database setup
echo "Setting up database..."
cd /app && python setup_database.py

if [ $? -ne 0 ]; then
    echo "Database setup failed, exiting..."
    exit 1
fi

# Start services with supervisor
echo "Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

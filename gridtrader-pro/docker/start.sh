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

# Run database migrations
echo "Running database migrations..."
cd /app && python -c "
import sys
import os
sys.path.insert(0, '/app')

try:
    from app.database import engine, Base
    from app.models import *
    
    print('Creating all database tables...')
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f'Created {len(tables)} tables: {tables}')
    
    if 'securities' in tables:
        print('Securities table created successfully')
    else:
        print('Warning: Securities table not found in created tables')
        
    print('Database tables created successfully')
    
except Exception as e:
    print(f'Database initialization error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Initialize sample data if needed
if [ "$INIT_SAMPLE_DATA" = "true" ]; then
    echo "Initializing sample data..."
    # Wait a moment for database to be fully ready
    sleep 2
    cd /app && python -c "
import sys
import os
import time
sys.path.insert(0, '/app')

from app.database import SessionLocal, engine
from app.models import Securities
from sqlalchemy import inspect

# Wait for database to be ready and verify tables exist
time.sleep(3)

# Verify securities table exists
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Available tables: {tables}')

if 'securities' not in tables:
    print('Securities table not found, skipping sample data initialization')
    exit(0)

db = SessionLocal()
try:
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ']
    
    # Check if any securities already exist
    existing_count = db.query(Securities).count()
    print(f'Found {existing_count} existing securities')
    
    if existing_count == 0:
        print(f'Adding {len(popular_symbols)} sample securities...')
        for symbol in popular_symbols:
            security = Securities(symbol=symbol, name=f'{symbol} Corp', is_active=True)
            db.add(security)
        
        db.commit()
        print(f'Sample data initialized successfully with {len(popular_symbols)} securities')
    else:
        print(f'Sample data already exists ({existing_count} securities found)')
        
except Exception as e:
    print(f'Error initializing sample data: {e}')
    import traceback
    traceback.print_exc()
    try:
        db.rollback()
    except:
        pass
finally:
    try:
        db.close()
    except:
        pass
"
fi

# Start services with supervisor
echo "Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

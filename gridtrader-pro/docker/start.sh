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
try:
    from app.init_db import init_database
    success = init_database()
    if not success:
        print('Database initialization failed')
        exit(1)
except Exception as e:
    print(f'Database initialization error: {e}')
    # Fallback to simple table creation
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print('Database tables created successfully (fallback)')
"

# Initialize sample data if needed
if [ "$INIT_SAMPLE_DATA" = "true" ]; then
    echo "Initializing sample data..."
    # Wait a moment for database to be fully ready
    sleep 2
    cd /app && python -c "
from app.database import SessionLocal
from app.models import Securities
import time

# Wait for database to be ready
time.sleep(2)

db = SessionLocal()
try:
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ']
    
    # Check if any securities already exist
    try:
        existing_count = db.query(Securities).count()
        print(f'Found {existing_count} existing securities')
    except Exception as e:
        print(f'Securities table not ready yet: {e}')
        existing_count = 0
    
    if existing_count == 0:
        for symbol in popular_symbols:
            try:
                security = Securities(symbol=symbol, name=f'{symbol} Corp', is_active=True)
                db.add(security)
            except Exception as e:
                print(f'Error adding {symbol}: {e}')
        
        try:
            db.commit()
            print(f'Sample data initialized with {len(popular_symbols)} securities')
        except Exception as e:
            print(f'Error committing sample data: {e}')
            db.rollback()
    else:
        print(f'Sample data already exists ({existing_count} securities found)')
        
except Exception as e:
    print(f'Error initializing sample data: {e}')
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

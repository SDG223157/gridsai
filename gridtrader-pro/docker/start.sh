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
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Initialize sample data if needed
if [ "$INIT_SAMPLE_DATA" = "true" ]; then
    echo "Initializing sample data..."
    cd /app && python -c "
from app.database import SessionLocal
from app.models import Securities
db = SessionLocal()
try:
    popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ']
    existing_symbols = set(s[0] for s in db.query(Securities.symbol).all())
    
    for symbol in popular_symbols:
        if symbol not in existing_symbols:
            security = Securities(symbol=symbol, name=f'{symbol} Corp', is_active=True)
            db.add(security)
    
    db.commit()
    print(f'Sample data initialized')
except Exception as e:
    print(f'Error initializing sample data: {e}')
    db.rollback()
finally:
    db.close()
"
fi

# Start services with supervisor
echo "Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

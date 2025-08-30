from celery import Celery
from .data_provider import YFinanceDataProvider
from .database import SessionLocal
from .models import Securities, RealTimePrices
import asyncio
import os

# Initialize Celery
celery_app = Celery(
    'gridtrader',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

@celery_app.task
def update_real_time_prices():
    """Update real-time prices for all tracked securities"""
    async def _update():
        db = SessionLocal()
        try:
            securities = db.query(Securities).filter(Securities.is_active == True).all()
            symbols = [s.symbol for s in securities]
            
            if symbols:
                provider = YFinanceDataProvider()
                price_data = await provider.get_real_time_prices(symbols)
                
                for symbol, data in price_data.items():
                    existing = db.query(RealTimePrices).filter(RealTimePrices.symbol == symbol).first()
                    
                    if existing:
                        for key, value in data.items():
                            setattr(existing, key, value)
                    else:
                        real_time_price = RealTimePrices(symbol=symbol, **data)
                        db.add(real_time_price)
                
                db.commit()
                print(f"Updated real-time prices for {len(price_data)} securities")
                
        except Exception as e:
            db.rollback()
            print(f"Error updating real-time prices: {e}")
        finally:
            db.close()
    
    asyncio.run(_update())

@celery_app.task
def update_daily_price_data():
    """Update daily price data for all securities"""
    async def _update():
        db = SessionLocal()
        try:
            securities = db.query(Securities).filter(Securities.is_active == True).all()
            symbols = [s.symbol for s in securities]
            
            provider = YFinanceDataProvider()
            await provider.update_price_data(symbols, period="5d")
            
            print(f"Updated daily price data for {len(symbols)} securities")
            
        except Exception as e:
            print(f"Error updating daily price data: {e}")
        finally:
            db.close()
    
    asyncio.run(_update())

# Schedule tasks
celery_app.conf.beat_schedule = {
    'update-real-time-prices': {
        'task': 'tasks.update_real_time_prices',
        'schedule': 300.0,  # Every 5 minutes
    },
    'update-daily-price-data': {
        'task': 'tasks.update_daily_price_data',
        'schedule': 3600.0,  # Every hour
    },
}

celery_app.conf.timezone = 'UTC'

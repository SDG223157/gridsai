from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from ..database import get_db
from ..models import Securities, PriceData, RealTimePrices
from ..data_provider import YFinanceDataProvider
from ..middleware.auth import get_current_user

router = APIRouter()
data_provider = YFinanceDataProvider()

@router.get("/securities/search")
async def search_securities(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, le=100),
    current_user = Depends(get_current_user)
):
    """Search for securities using yfinance data"""
    try:
        results = await data_provider.search_symbols(q, limit)
        return {"securities": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/securities/{symbol}")
async def get_security_info(
    symbol: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed information about a security"""
    security = db.query(Securities).filter(Securities.symbol == symbol.upper()).first()
    
    if not security:
        info = await data_provider.get_stock_info(symbol.upper())
        if info:
            security = Securities(**info)
            db.add(security)
            db.commit()
            db.refresh(security)
        else:
            raise HTTPException(status_code=404, detail="Security not found")
    
    return security

@router.get("/prices/{symbol}")
async def get_price_data(
    symbol: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    interval: str = Query("1d", regex="^(1d|1wk|1mo)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get historical price data for a symbol"""
    
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    prices = db.query(PriceData).filter(
        PriceData.symbol == symbol.upper(),
        PriceData.date >= start_date,
        PriceData.date <= end_date
    ).order_by(PriceData.date).all()
    
    if not prices:
        period_map = {
            (end_date - start_date).days <= 30: "1mo",
            (end_date - start_date).days <= 90: "3mo", 
            (end_date - start_date).days <= 365: "1y"
        }
        period = next((v for k, v in period_map.items() if k), "2y")
        
        hist_data = await data_provider.get_historical_data(symbol.upper(), period=period)
        
        if not hist_data.empty:
            await data_provider.update_price_data([symbol.upper()], period=period)
            prices = hist_data.to_dict('records')
    
    return {
        "symbol": symbol.upper(),
        "prices": prices,
        "count": len(prices)
    }

@router.get("/prices/{symbol}/current")
async def get_current_price(
    symbol: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current/real-time price for a symbol"""
    
    cached_price = db.query(RealTimePrices).filter(RealTimePrices.symbol == symbol.upper()).first()
    
    if cached_price and (datetime.now() - cached_price.last_updated).seconds < 300:
        return cached_price
    
    price_data = await data_provider.get_real_time_prices([symbol.upper()])
    
    if symbol.upper() in price_data:
        data = price_data[symbol.upper()]
        
        if cached_price:
            for key, value in data.items():
                setattr(cached_price, key, value)
        else:
            cached_price = RealTimePrices(symbol=symbol.upper(), **data)
            db.add(cached_price)
        
        db.commit()
        return cached_price
    else:
        raise HTTPException(status_code=404, detail="Price data not available")

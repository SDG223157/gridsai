import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Securities, PriceData, RealTimePrices

class YFinanceDataProvider:
    def __init__(self):
        self.timeout = 30
        
    async def get_stock_info(self, symbol: str) -> Dict:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'exchange': info.get('exchange', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'country': info.get('country', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE'),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield'),
                'yfinance_info': info
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return pd.DataFrame()
                
            data = data.reset_index()
            data['Symbol'] = symbol
            
            data = data.rename(columns={
                'Date': 'date',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Adj Close': 'adj_close',
                'Volume': 'volume'
            })
            
            return data[['Symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'adj_close', 'volume']]
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    async def get_real_time_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        real_time_data = {}
        
        try:
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    hist = ticker.history(period="5d", interval="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        
                        change_amount = current_price - prev_close
                        change_percent = (change_amount / prev_close * 100) if prev_close != 0 else 0
                        
                        real_time_data[symbol] = {
                            'current_price': float(current_price),
                            'change_amount': float(change_amount),
                            'change_percent': float(change_percent),
                            'volume': int(hist['Volume'].iloc[-1]),
                            'market_cap': info.get('marketCap', 0),
                            'pe_ratio': info.get('trailingPE')
                        }
                except Exception as e:
                    print(f"Error fetching real-time data for {symbol}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching real-time data: {e}")
            
        return real_time_data

    async def search_symbols(self, query: str, limit: int = 20) -> List[Dict]:
        common_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'SPY', 'QQQ', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'TLT',
            'BABA', 'JD', 'BIDU', 'NIO', 'XPEV', 'LI',
            'FXI', 'ASHR', 'KWEB', 'PGJ', 'CHIQ',
            'VGK', 'EWG', 'EWU', 'EWJ'
        ]
        
        filtered_symbols = [s for s in common_symbols if query.upper() in s]
        results = []
        
        for symbol in filtered_symbols[:limit]:
            info = await self.get_stock_info(symbol)
            if info:
                results.append(info)
                
        return results

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 50:
            return pd.DataFrame()
            
        indicators = pd.DataFrame()
        indicators['symbol'] = df['Symbol']
        indicators['date'] = df['date']
        
        for period in [20, 50, 200]:
            if len(df) >= period:
                indicators[f'sma_{period}'] = df['close_price'].rolling(window=period).mean()
        
        def calculate_rsi(prices, period=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        if len(df) >= 14:
            indicators['rsi_14'] = calculate_rsi(df['close_price'])
        
        indicators = indicators.dropna()
        return indicators

    async def update_securities_database(self, symbols: List[str]):
        db = SessionLocal()
        try:
            for symbol in symbols:
                info = await self.get_stock_info(symbol)
                if info:
                    existing = db.query(Securities).filter(Securities.symbol == symbol).first()
                    
                    if existing:
                        for key, value in info.items():
                            if key != 'symbol':
                                setattr(existing, key, value)
                    else:
                        security = Securities(**info)
                        db.add(security)
                        
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error updating securities database: {e}")
        finally:
            db.close()

    async def update_price_data(self, symbols: List[str], period: str = "30d"):
        db = SessionLocal()
        try:
            for symbol in symbols:
                hist_data = await self.get_historical_data(symbol, period=period)
                
                if not hist_data.empty:
                    price_records = hist_data.to_dict('records')
                    
                    for record in price_records:
                        existing = db.query(PriceData).filter(
                            PriceData.symbol == record['Symbol'],
                            PriceData.date == record['date']
                        ).first()
                        
                        if not existing:
                            price_data = PriceData(
                                symbol=record['Symbol'],
                                date=record['date'],
                                open_price=record['open_price'],
                                high_price=record['high_price'],
                                low_price=record['low_price'],
                                close_price=record['close_price'],
                                adj_close=record['adj_close'],
                                volume=record['volume']
                            )
                            db.add(price_data)
                            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error updating price data: {e}")
        finally:
            db.close()

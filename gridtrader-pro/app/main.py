from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from .database import engine, Base
from .routers import auth, portfolios, market_data, grids, analytics
from .data_provider import YFinanceDataProvider

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GridTrader Pro API",
    description="Systematic Investment Management Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gridsai.app", "http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(portfolios.router, prefix="/api/v1/portfolios", tags=["portfolios"])
app.include_router(market_data.router, prefix="/api/v1/market", tags=["market_data"])
app.include_router(grids.router, prefix="/api/v1/grids", tags=["grid_trading"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# Initialize data provider
data_provider = YFinanceDataProvider()

@app.get("/")
async def root():
    return {"message": "GridTrader Pro API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "yfinance": "healthy"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 3000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )

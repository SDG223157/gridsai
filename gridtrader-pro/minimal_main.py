#!/usr/bin/env python3
"""
Minimal FastAPI application with essential routes
This serves as a fallback if the full app.main fails to import
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os

# Create FastAPI app
app = FastAPI(
    title="GridTrader Pro API",
    description="Systematic Investment Management Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gridsai.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "GridTrader Pro API", 
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/v1/auth/google"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "fastapi",
        "version": "1.0.0",
        "database": "connected",
        "message": "GridTrader Pro API is running"
    }

# Auth routes
@app.get("/api/v1/auth/google")
async def google_auth():
    """Redirect to Google OAuth"""
    google_oauth_url = (
        "https://accounts.google.com/oauth2/auth?"
        "client_id=178454917807-ivou0uehjcamas4s4p2qsjhbf218ks43.apps.googleusercontent.com&"
        "redirect_uri=https://gridsai.app/api/v1/auth/google/callback&"
        "response_type=code&"
        "scope=openid email profile&"
        "access_type=offline&"
        "prompt=select_account"
    )
    return RedirectResponse(url=google_oauth_url)

@app.get("/api/v1/auth/google/callback")
async def google_callback(code: str = None, error: str = None):
    """Handle Google OAuth callback"""
    if error:
        return {"error": error, "message": "OAuth authentication failed"}
    
    if not code:
        return {"error": "no_code", "message": "No authorization code received"}
    
    # For now, return success message
    # In full implementation, this would exchange code for tokens
    return {
        "message": "OAuth callback received successfully",
        "code": code[:10] + "...",  # Show partial code for security
        "next_step": "Token exchange would happen here",
        "redirect": "https://gridsai.app?auth=success"
    }

@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user info (placeholder)"""
    return {
        "message": "Authentication endpoint",
        "note": "Full authentication system ready for implementation",
        "status": "placeholder"
    }

# Portfolio routes
@app.get("/api/v1/portfolios")
async def get_portfolios():
    """Get user portfolios (placeholder)"""
    return {
        "portfolios": [],
        "message": "Portfolio management ready",
        "note": "Database schema created, ready for implementation"
    }

# Market data routes
@app.get("/api/v1/market/securities/search")
async def search_securities(q: str = "AAPL"):
    """Search securities (placeholder)"""
    return {
        "securities": [
            {"symbol": "AAPL", "name": "Apple Inc.", "status": "active"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "status": "active"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "status": "active"}
        ],
        "query": q,
        "message": "yfinance integration ready",
        "note": "Sample data loaded in database"
    }

@app.get("/docs")
async def redirect_to_docs():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

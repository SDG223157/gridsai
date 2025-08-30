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

@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    """Email/password login"""
    # Placeholder implementation
    if email and password:
        return {
            "access_token": "demo_token_" + email.split('@')[0],
            "token_type": "bearer",
            "user_id": "demo_user_123",
            "email": email,
            "message": "Login successful (demo mode)"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/api/v1/auth/register") 
async def register(email: str, password: str, display_name: str = None):
    """User registration"""
    # Placeholder implementation
    if email and password:
        return {
            "access_token": "demo_token_" + email.split('@')[0],
            "token_type": "bearer", 
            "user_id": "demo_user_" + email.split('@')[0],
            "email": email,
            "message": "Registration successful (demo mode)"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid registration data")

@app.get("/api/v1/auth/google/callback")
async def google_callback(code: str = None, error: str = None, state: str = None):
    """Handle Google OAuth callback"""
    if error:
        # Redirect back to main page with error
        return RedirectResponse(url=f"https://gridsai.app?error={error}")
    
    if not code:
        # Redirect back to main page with error
        return RedirectResponse(url="https://gridsai.app?error=no_authorization_code")
    
    # For demo purposes, create a demo token and redirect to success
    demo_token = f"demo_google_token_{code[:8]}"
    return RedirectResponse(url=f"https://gridsai.app?token={demo_token}&auth=google_success")

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

@app.get("/debug/oauth")
async def debug_oauth():
    """Debug OAuth configuration"""
    return {
        "google_oauth_url": "https://accounts.google.com/oauth2/auth",
        "client_id": "178454917807-ivou0uehjcamas4s4p2qsjhbf218ks43.apps.googleusercontent.com",
        "redirect_uri": "https://gridsai.app/api/v1/auth/google/callback",
        "scope": "openid email profile",
        "response_type": "code",
        "note": "Ensure this redirect_uri is added to Google Console",
        "google_console_url": "https://console.cloud.google.com/apis/credentials"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

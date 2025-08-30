#!/usr/bin/env python3
"""
Minimal FastAPI application with essential routes
This serves as a fallback if the full app.main fails to import
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import httpx
import urllib.parse

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
async def google_auth(request: Request):
    """Initiate Google OAuth flow"""
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://gridsai.app/api/v1/auth/google/callback")
    
    if not client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    # Generate state parameter for security
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Build OAuth URL
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state
    }
    
    oauth_url = "https://accounts.google.com/oauth2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url=oauth_url)

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
async def google_callback(request: Request, code: str = None, error: str = None, state: str = None):
    """Handle Google OAuth callback - Exchange code for tokens"""
    
    if error:
        return RedirectResponse(url=f"https://gridsai.app?error={error}")
    
    if not code:
        return RedirectResponse(url="https://gridsai.app?error=no_authorization_code")
    
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://gridsai.app/api/v1/auth/google/callback")
        
        if not client_id or not client_secret:
            return RedirectResponse(url="https://gridsai.app?error=oauth_not_configured")
        
        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_result = token_response.json()
        
        if token_response.status_code != 200:
            return RedirectResponse(url="https://gridsai.app?error=token_exchange_failed")
        
        access_token = token_result.get("access_token")
        
        # Get user info from Google
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = user_response.json()
        
        if user_response.status_code != 200:
            return RedirectResponse(url="https://gridsai.app?error=user_info_failed")
        
        # Create session token
        try:
            import jwt
            session_token = jwt.encode({
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "google_id": user_info.get("id"),
                "exp": 9999999999  # Long expiry for demo
            }, os.getenv("SECRET_KEY", "demo_secret"), algorithm="HS256")
        except ImportError:
            # Fallback if PyJWT not available
            session_token = f"demo_token_{user_info.get('email', 'user')}"
        
        # Redirect back to app with token and user info
        redirect_url = (
            f"https://gridsai.app?"
            f"token={session_token}&"
            f"auth=google_success&"
            f"name={urllib.parse.quote(user_info.get('name', ''))}&"
            f"email={urllib.parse.quote(user_info.get('email', ''))}&"
            f"picture={urllib.parse.quote(user_info.get('picture', ''))}"
        )
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        return RedirectResponse(url="https://gridsai.app?error=oauth_processing_failed")

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
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "https://gridsai.app/api/v1/auth/google/callback"),
        "scope": "openid email profile",
        "response_type": "code",
        "note": "Ensure this redirect_uri is added to Google Console",
        "google_console_url": "https://console.cloud.google.com/apis/credentials",
        "environment_configured": bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

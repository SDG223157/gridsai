from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os

from ..database import get_db
from ..models import Users, UserProfiles
from ..auth.google_oauth import google_oauth_handler, oauth
from ..middleware.auth import create_access_token, get_current_user

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/google")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    try:
        redirect_uri = str(request.url_for('google_callback'))
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Google OAuth: {str(e)}"
        )

@router.get("/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        oauth_data = await google_oauth_handler.handle_callback(request)
        user = await google_oauth_handler.create_or_update_user(oauth_data)
        
        access_token_expires = timedelta(hours=int(os.getenv("JWT_EXPIRE_HOURS", 24)))
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        frontend_url = os.getenv("FRONTEND_URL", "https://gridsai.app")
        return RedirectResponse(
            url=f"{frontend_url}?token={access_token}&user_id={user.id}"
        )
        
    except Exception as e:
        frontend_url = os.getenv("FRONTEND_URL", "https://gridsai.app")
        return RedirectResponse(
            url=f"{frontend_url}?error={str(e)}"
        )

@router.post("/register")
async def register(
    email: str,
    password: str,
    display_name: str = None,
    db: Session = Depends(get_db)
):
    """Register new user with email and password"""
    
    existing_user = db.query(Users).filter(Users.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    password_hash = pwd_context.hash(password)
    
    user = Users(
        email=email,
        password_hash=password_hash,
        auth_provider='local',
        is_email_verified=False
    )
    db.add(user)
    db.flush()
    
    profile = UserProfiles(
        user_id=user.id,
        display_name=display_name or email.split('@')[0]
    )
    db.add(profile)
    db.commit()
    
    access_token_expires = timedelta(hours=int(os.getenv("JWT_EXPIRE_HOURS", 24)))
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

@router.post("/login")
async def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    
    user = db.query(Users).filter(Users.email == email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(hours=int(os.getenv("JWT_EXPIRE_HOURS", 24)))
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

@router.get("/me")
async def get_current_user_info(current_user: Users = Depends(get_current_user)):
    """Get current user profile information"""
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "auth_provider": current_user.auth_provider,
            "subscription_tier": current_user.subscription_tier,
            "is_email_verified": current_user.is_email_verified
        },
        "profile": current_user.profile
    }

@router.post("/logout")
async def logout(current_user: Users = Depends(get_current_user)):
    """Logout user"""
    return {"message": "Successfully logged out"}

from fastapi import HTTPException, status
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from sqlalchemy.orm import Session
import httpx
import os
from typing import Dict, Any

from ..database import SessionLocal
from ..models import Users, UserProfiles, OAuthSessions

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
    }
)

class GoogleOAuthHandler:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
    async def get_authorization_url(self, request: Request) -> str:
        try:
            redirect_uri = str(request.url_for('google_callback'))
            return await oauth.google.authorize_redirect(request, redirect_uri)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate authorization URL: {str(e)}"
            )
    
    async def handle_callback(self, request: Request) -> Dict[str, Any]:
        try:
            token = await oauth.google.authorize_access_token(request)
            user_info = token.get('userinfo')
            
            if not user_info:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': f"Bearer {token['access_token']}"}
                    )
                    user_info = response.json()
            
            return {
                'token': token,
                'user_info': user_info
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth callback failed: {str(e)}"
            )
    
    async def create_or_update_user(self, oauth_data: Dict[str, Any]) -> Users:
        db = SessionLocal()
        try:
            user_info = oauth_data['user_info']
            token_data = oauth_data['token']
            
            google_id = user_info['id']
            email = user_info['email']
            
            existing_user = db.query(Users).filter(
                (Users.google_id == google_id) | (Users.email == email)
            ).first()
            
            if existing_user:
                existing_user.google_id = google_id
                existing_user.email = email
                existing_user.auth_provider = 'google'
                existing_user.is_email_verified = user_info.get('verified_email', True)
                
                profile = db.query(UserProfiles).filter(UserProfiles.user_id == existing_user.id).first()
                if profile:
                    profile.first_name = user_info.get('given_name', '')
                    profile.last_name = user_info.get('family_name', '')
                    profile.display_name = user_info.get('name', email.split('@')[0])
                    profile.avatar_url = user_info.get('picture', '')
                    profile.locale = user_info.get('locale', 'en')
                    profile.google_profile_data = user_info
                
                user = existing_user
                
            else:
                user = Users(
                    email=email,
                    google_id=google_id,
                    auth_provider='google',
                    is_email_verified=user_info.get('verified_email', True),
                    password_hash=None
                )
                db.add(user)
                db.flush()
                
                profile = UserProfiles(
                    user_id=user.id,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    display_name=user_info.get('name', email.split('@')[0]),
                    avatar_url=user_info.get('picture', ''),
                    locale=user_info.get('locale', 'en'),
                    google_profile_data=user_info
                )
                db.add(profile)
            
            oauth_session = db.query(OAuthSessions).filter(
                OAuthSessions.user_id == user.id,
                OAuthSessions.provider == 'google'
            ).first()
            
            if oauth_session:
                oauth_session.access_token = token_data['access_token']
                oauth_session.refresh_token = token_data.get('refresh_token')
                oauth_session.expires_at = token_data.get('expires_at')
                oauth_session.scope = token_data.get('scope', 'openid email profile')
            else:
                oauth_session = OAuthSessions(
                    user_id=user.id,
                    provider='google',
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    expires_at=token_data.get('expires_at'),
                    scope=token_data.get('scope', 'openid email profile')
                )
                db.add(oauth_session)
            
            db.commit()
            db.refresh(user)
            return user
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create/update user: {str(e)}"
            )
        finally:
            db.close()

google_oauth_handler = GoogleOAuthHandler()

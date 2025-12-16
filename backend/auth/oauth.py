import os
from google_auth_oauthlib.flow import Flow
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import OAuthToken, User
import datetime

# Allow OAuth over HTTP for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "openid",
    "email",
    "profile"
]

def create_flow():
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def get_google_auth_url(username: str):
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=username
    )
    return authorization_url

async def handle_google_callback(request: Request, db: AsyncSession):
    code = request.query_params.get("code")
    state = request.query_params.get("state") # This is the username
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    if not state:
        raise HTTPException(status_code=400, detail="State (username) missing")

    flow = create_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Find the user
    result = await db.execute(select(User).where(User.username == state))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if token already exists
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id, OAuthToken.provider == "google"))
    existing_token = result.scalars().first()

    if existing_token:
        existing_token.access_token = credentials.token
        existing_token.refresh_token = credentials.refresh_token
        existing_token.expires_at = credentials.expiry
    else:
        new_token = OAuthToken(
            user_id=user.id,
            provider="google",
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expires_at=credentials.expiry
        )
        db.add(new_token)
    
    await db.commit()
    return {"msg": "Google Drive connected successfully"}

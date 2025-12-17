import os
from google_auth_oauthlib.flow import Flow
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import OAuthToken, User
import datetime
import httpx

# Allow OAuth over HTTP for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google/callback"

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = "http://localhost:8000/auth/github/callback"

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
        redirect_uri=GOOGLE_REDIRECT_URI
    )

def get_google_auth_url(username: str):
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=username
    )
    return authorization_url

def get_github_auth_url(username: str):
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID not configured")
        
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "repo user",
        "state": username
    }
    # Construct URL manually
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    return f"https://github.com/login/oauth/authorize?{query_string}"

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

async def handle_github_callback(request: Request, db: AsyncSession):
    code = request.query_params.get("code")
    state = request.query_params.get("state") # This is the username
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    if not state:
        raise HTTPException(status_code=400, detail="State (username) missing")

    # Exchange code for token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve token from GitHub")
        
    token_data = response.json()
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data["error_description"])
        
    access_token = token_data["access_token"]
    # GitHub tokens don't typically expire in the same way as Google's unless configured, 
    # and refresh tokens are for GitHub Apps, not OAuth Apps usually (though they can be).
    # For simplicity, we'll just store the access token.
    
    # Find the user
    result = await db.execute(select(User).where(User.username == state))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if token already exists
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id, OAuthToken.provider == "github"))
    existing_token = result.scalars().first()

    if existing_token:
        existing_token.access_token = access_token
        # GitHub OAuth apps don't provide refresh tokens by default
        existing_token.refresh_token = None 
        existing_token.expires_at = None
    else:
        new_token = OAuthToken(
            user_id=user.id,
            provider="github",
            access_token=access_token,
            refresh_token=None,
            expires_at=None
        )
        db.add(new_token)
    
    await db.commit()
    return {"msg": "GitHub connected successfully"}

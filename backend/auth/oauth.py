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

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = "http://localhost:8000/auth/slack/callback"

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

def get_slack_auth_url(username: str):
    if not SLACK_CLIENT_ID:
        raise HTTPException(status_code=500, detail="SLACK_CLIENT_ID not configured")
        
    # User scopes for reading channels, groups, IMs, MPIMs and their history
    scopes = "channels:read,groups:read,im:read,mpim:read,channels:history,groups:history,im:history,mpim:history,users:read"
    
    params = {
        "client_id": SLACK_CLIENT_ID,
        "redirect_uri": SLACK_REDIRECT_URI,
        "user_scope": scopes, # Note: user_scope for user tokens
        "state": username
    }
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    return f"https://slack.com/oauth/v2/authorize?{query_string}"

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
    else:
        new_token = OAuthToken(
            user_id=user.id,
            provider="github",
            access_token=access_token
        )
        db.add(new_token)
    
    await db.commit()
    return {"msg": "GitHub connected successfully"}

async def handle_slack_callback(request: Request, db: AsyncSession):
    code = request.query_params.get("code")
    state = request.query_params.get("state") # This is the username
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    if not state:
        raise HTTPException(status_code=400, detail="State (username) missing")

    # Exchange code for token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": SLACK_CLIENT_ID,
                "client_secret": SLACK_CLIENT_SECRET,
                "code": code,
                "redirect_uri": SLACK_REDIRECT_URI
            }
        )
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve token from Slack")
        
    token_data = response.json()
    if not token_data.get("ok"):
        raise HTTPException(status_code=400, detail=f"Slack Error: {token_data.get('error')}")
        
    # For user tokens, we look at 'authed_user' -> 'access_token'
    # If we requested bot scopes, we'd look at 'access_token'
    # Since we used 'user_scope', we want the user token.
    authed_user = token_data.get("authed_user", {})
    access_token = authed_user.get("access_token")
    
    if not access_token:
         raise HTTPException(status_code=400, detail="No user access token returned")

    # Find the user
    result = await db.execute(select(User).where(User.username == state))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if token already exists
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id, OAuthToken.provider == "slack"))
    existing_token = result.scalars().first()

    if existing_token:
        existing_token.access_token = access_token
        existing_token.refresh_token = None 
        existing_token.expires_at = None
    else:
        new_token = OAuthToken(
            user_id=user.id,
            provider="slack",
            access_token=access_token,
            refresh_token=None,
            expires_at=None
        )
        db.add(new_token)
    
    await db.commit()
    return {"msg": "Slack connected successfully"}

async def refresh_google_token(token_record: OAuthToken, db: AsyncSession):
    """
    Refreshes the Google OAuth token if it is expired or close to expiring.
    """
    if not token_record.refresh_token:
        return token_record.access_token
    
    # Check if expired (with 5 minute buffer)
    # Note: expires_at might be None if not set initially, though it should be for Google
    if token_record.expires_at:
        # Ensure we're comparing compatible datetimes (naive vs aware)
        # Assuming expires_at is stored as naive UTC in DB
        now = datetime.datetime.utcnow()
        if token_record.expires_at > now + datetime.timedelta(minutes=5):
            return token_record.access_token

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": token_record.refresh_token,
                "grant_type": "refresh_token",
            }
        )
        
    if response.status_code == 200:
        data = response.json()
        token_record.access_token = data["access_token"]
        # Calculate new expiry
        expires_in = data.get("expires_in", 3600)
        token_record.expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        
        await db.commit()
        return token_record.access_token
    else:
        print(f"Failed to refresh Google token: {response.text}")
        # Return existing token as fallback, though it likely won't work
        return token_record.access_token

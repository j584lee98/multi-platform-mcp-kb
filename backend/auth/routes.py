from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from models import OAuthToken, User
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .oauth import (
    get_github_auth_url,
    get_google_auth_url,
    get_slack_auth_url,
    handle_github_callback,
    handle_google_callback,
    handle_slack_callback,
)
from .services import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await register_user(data.username, data.password, db)

@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(data.username, data.password, db)

# Google Routes
@router.get("/google/login")
def google_login(username: str):
    auth_url = get_google_auth_url(username)
    return {"url": auth_url}

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    await handle_google_callback(request, db)
    return RedirectResponse(url="http://localhost:3000/connectors/google-drive")

@router.get("/google/status")
async def google_status(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "google",
        )
    )
    token = result.scalars().first()
    
    return {"connected": token is not None}

@router.delete("/google/disconnect")
async def google_disconnect(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "google",
        )
    )
    token = result.scalars().first()
    
    if token:
        await db.delete(token)
        await db.commit()
        
    return {"msg": "Disconnected successfully"}

# GitHub Routes
@router.get("/github/login")
def github_login(username: str):
    auth_url = get_github_auth_url(username)
    return {"url": auth_url}

@router.get("/github/callback")
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    await handle_github_callback(request, db)
    # Redirect to a GitHub connector page (which we might need to create later)
    return RedirectResponse(url="http://localhost:3000/connectors/github")

@router.get("/github/status")
async def github_status(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "github",
        )
    )
    token = result.scalars().first()
    
    return {"connected": token is not None}

@router.delete("/github/disconnect")
async def github_disconnect(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "github",
        )
    )
    token = result.scalars().first()
    
    if token:
        await db.delete(token)
        await db.commit()
        
    return {"msg": "Disconnected successfully"}

# Slack Routes
@router.get("/slack/login")
def slack_login(username: str):
    auth_url = get_slack_auth_url(username)
    return {"url": auth_url}

@router.get("/slack/callback")
async def slack_callback(request: Request, db: AsyncSession = Depends(get_db)):
    await handle_slack_callback(request, db)
    return RedirectResponse(url="http://localhost:3000/connectors/slack")

@router.get("/slack/status")
async def slack_status(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "slack",
        )
    )
    token = result.scalars().first()
    
    return {"connected": token is not None}

@router.delete("/slack/disconnect")
async def slack_disconnect(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "slack",
        )
    )
    token = result.scalars().first()
    
    if token:
        await db.delete(token)
        await db.commit()
        
    return {"msg": "Disconnected successfully"}

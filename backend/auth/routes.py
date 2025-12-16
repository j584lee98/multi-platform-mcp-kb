from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .services import register_user, authenticate_user
from .oauth import get_google_auth_url, handle_google_callback

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

@router.get("/google/login")
def google_login(username: str):
    auth_url = get_google_auth_url(username)
    return {"url": auth_url}

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    await handle_google_callback(request, db)
    return RedirectResponse(url="http://localhost:3000/home")

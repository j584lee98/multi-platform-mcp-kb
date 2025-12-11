from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from .services import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(data: UserRegister):
    return register_user(data.username, data.password)

@router.post("/login")
def login(data: UserLogin):
    return authenticate_user(data.username, data.password)

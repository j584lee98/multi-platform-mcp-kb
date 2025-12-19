import bcrypt
from fastapi import HTTPException, status
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

async def register_user(username: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    return {"msg": "User registered successfully"}

async def authenticate_user(username: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"msg": "Login successful"}

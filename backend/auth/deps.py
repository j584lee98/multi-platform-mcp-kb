import secrets

from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .services import verify_password


security = HTTPBasic()


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalars().first()

    # Always do a constant-time compare on username to avoid leaking timing info
    # between "user not found" and "bad password" branches.
    username_ok = secrets.compare_digest(credentials.username, user.username) if user else False
    password_ok = verify_password(credentials.password, user.hashed_password) if user else False

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user

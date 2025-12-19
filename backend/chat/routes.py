from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from mcp_client import list_google_drive_files
from models import OAuthToken, User
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/chat", tags=["chat"])

class QueryRequest(BaseModel):
    username: str

@router.post("/list-files")
async def list_files(data: QueryRequest, db: AsyncSession = Depends(get_db)):
    # Get user
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get Google Token
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "google",
        )
    )
    token_record = result.scalars().first()
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Google Drive not connected")
        
    # Call MCP
    # Note: In production, we should handle token refresh here if expired
    response = await list_google_drive_files(token_record.access_token)
    
    return {"response": response}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User, OAuthToken
from mcp_client import call_google_drive_tool
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/mcp", tags=["mcp"])

class MCPToolRequest(BaseModel):
    username: str
    tool_name: str
    arguments: Dict[str, Any] = {}

@router.post("/google-drive/execute")
async def execute_tool(request: MCPToolRequest, db: AsyncSession = Depends(get_db)):
    # Get user
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get Google Token
    result = await db.execute(select(OAuthToken).where(OAuthToken.user_id == user.id, OAuthToken.provider == "google"))
    token_record = result.scalars().first()
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Google Drive not connected")
        
    # Inject token into arguments
    arguments = request.arguments.copy()
    arguments["token"] = token_record.access_token
    
    # Call MCP
    response = await call_google_drive_tool(request.tool_name, arguments)
    
    return {"response": response}

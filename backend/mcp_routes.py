from typing import Any

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from mcp_client import call_github_tool, call_google_drive_tool, call_slack_tool
from models import OAuthToken, User
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.oauth import refresh_google_token

router = APIRouter(prefix="/mcp", tags=["mcp"])

class MCPToolRequest(BaseModel):
    username: str
    tool_name: str
    arguments: dict[str, Any] = {}

@router.post("/google-drive/execute")
async def execute_tool(request: MCPToolRequest, db: AsyncSession = Depends(get_db)):
    # Get user
    result = await db.execute(select(User).where(User.username == request.username))
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
    
    # Refresh token if needed
    access_token = await refresh_google_token(token_record, db)
        
    # Inject token into arguments
    arguments = request.arguments.copy()
    arguments["token"] = access_token
    
    # Call MCP
    response = await call_google_drive_tool(request.tool_name, arguments)
    
    return {"response": response}

@router.post("/github/execute")
async def execute_github_tool(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db),
):
    # Get user
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get GitHub Token
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "github",
        )
    )
    token_record = result.scalars().first()
    
    if not token_record:
        raise HTTPException(status_code=400, detail="GitHub not connected")
        
    # Inject token into arguments
    arguments = request.arguments.copy()
    arguments["token"] = token_record.access_token
    
    # Call MCP
    response = await call_github_tool(request.tool_name, arguments)
    
    return {"response": response}

@router.post("/slack/execute")
async def execute_slack_tool(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db),
):
    # Get user
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get Slack Token
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == "slack",
        )
    )
    token_record = result.scalars().first()
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Slack not connected")
        
    # Inject token into arguments
    arguments = request.arguments.copy()
    arguments["token"] = token_record.access_token
    
    # Call MCP
    response = await call_slack_tool(request.tool_name, arguments)
    
    return {"response": response}

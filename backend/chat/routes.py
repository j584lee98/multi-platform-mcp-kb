from auth.deps import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from mcp_agent import create_mcp_agent
from models import User
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/chat", tags=["chat"])

class AgentRequest(BaseModel):
    query: str

@router.post("/agent")
async def run_agent(
    data: AgentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        agent_executor = await create_mcp_agent(user_id=user.id, db=db)
        result = await agent_executor.ainvoke(
            {"messages": [{"role": "user", "content": data.query}]}
        )
        return {"response": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


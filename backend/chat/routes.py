from fastapi import APIRouter, HTTPException
from mcp_agent import create_mcp_agent
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class AgentRequest(BaseModel):
    query: str

@router.post("/agent")
async def run_agent(data: AgentRequest):
    try:
        agent_executor = await create_mcp_agent()
        result = await agent_executor.ainvoke({"input": data.query})
        return {"response": result["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


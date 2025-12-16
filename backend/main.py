from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from chat.routes import router as chat_router
from auth.auth import authenticate
from database import engine, Base

app = FastAPI(
    title="Multi-Platform MCP KB API",
    description="Backend API for the Multi-Platform MCP Knowledge Base",
    version="0.1.0",
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include auth routes
app.include_router(auth_router)
app.include_router(chat_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(user: str = Depends(authenticate)):
    return {"message": f"Welcome {user} to the Multi-Platform MCP KB API"}


@app.get("/health")
async def health_check(user: str = Depends(authenticate)):
    return {"status": "healthy", "user": user}

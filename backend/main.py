from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from backend.auth.auth import authenticate

app = FastAPI(
    title="Multi-Platform MCP KB API",
    description="Backend API for the Multi-Platform MCP Knowledge Base",
    version="0.1.0",
)


# Include auth routes
app.include_router(auth_router)

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

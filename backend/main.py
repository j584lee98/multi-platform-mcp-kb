from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Multi-Platform MCP KB API",
    description="Backend API for the Multi-Platform MCP Knowledge Base",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Platform MCP KB API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

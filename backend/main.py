import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from backend.routers import dashboard, robot, webhook

app = FastAPI(
    title="CruzrTwin ASEAN - Unified Backend API",
    description="Backend API for Dashboard, Cruzr Robot Interface, and FIWARE Webhooks (T-014, T-015, T-016)",
    version="1.0.0"
)

# Configure CORS for Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard (T-015)"])
app.include_router(robot.router, prefix="/api/robot", tags=["Cruzr Robot (T-014)"])
app.include_router(webhook.router, prefix="/webhook", tags=["FIWARE Webhook (T-016)"])

@app.get("/", tags=["Health"])
def health_check():
    """Check if the API is running."""
    return {"status": "ok", "service": "CruzrTwin Unified Backend API"}

if __name__ == "__main__":
    # Run server locally (for testing without docker)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

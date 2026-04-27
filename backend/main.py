from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from api import sensors, risk, energy, webhook, health
from websocket.ws_handler import websocket_handler

app = FastAPI(
    title="CruzrTwin ASEAN Backend API",
    description="REST API for dashboard",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INCLUDE ROUTERS ====================
api_routers = [sensors.router, risk.router, energy.router, webhook.router, health.router]
for router in api_routers:
    app.include_router(router)

# ==================== ROOT ENDPOINT ====================
@app.get("/")
def root():
    return {
        "service": "CruzrTwin ASEAN Backend API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/health",
            "/ws",
            "/api/sensors",
            "/api/risk",
            "/api/energy/stats",
            "/api/webhook/anomaly",
        ]
    }

# ==================== WEBSOCKET ENDPOINT ====================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)

# ==================== RUN SERVER ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
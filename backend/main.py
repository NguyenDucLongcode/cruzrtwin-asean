from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os

from api import sensors, risk, energy, webhook, health, alerts
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
api_routers = [sensors.router, risk.router, energy.router, webhook.router, health.router, alerts.router]
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
            "/api/alerts",
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
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
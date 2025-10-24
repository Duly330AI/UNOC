"""
UNOC Backend - FastAPI Application

Clean, Simple, Tested.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from backend.api.routes import api_router
from backend.db import init_db, get_session_context
from backend.services.seed import seed_if_empty


# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:5173', 'http://localhost:5174']  # Vite dev server (both ports)
)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup/shutdown"""
    # Startup
    print("🚀 Starting UNOC Backend...")
    await init_db()
    print("✅ Database initialized")
    
    # Seed demo data if database is empty
    async with get_session_context() as session:
        await seed_if_empty(session)
    print("✅ Seed check complete")
    
    yield
    
    # Shutdown
    print("👋 Shutting down UNOC Backend...")


# Create FastAPI app
app = FastAPI(
    title="UNOC API",
    version="2.0.0",
    description="Network Operations Center - Clean Architecture",
    lifespan=lifespan,
)

# CORS - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite dev server (both ports)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount Socket.IO app at standard path
app.mount("/socket.io", socket_app)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEBSOCKET EVENTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@sio.event
async def connect(sid, environ):
    """Client connected"""
    print(f"🔌 Client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Client disconnected"""
    print(f"🔌 Client disconnected: {sid}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER: Emit to all clients
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def emit_to_all(event: str, data: dict):
    """Emit event to all connected clients"""
    await sio.emit(event, data)
    print(f"📡 Emitted '{event}' to all clients: {data}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unoc-backend",
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
    )

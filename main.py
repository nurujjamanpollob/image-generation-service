import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api.admin_endpoints import router as admin_router
from api.endpoints import router as image_router
from core.security import initialize_api_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load model at startup

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Initialize API keys system
    initialize_api_keys()
    logger.info("API keys system initialized")
    
    yield
    
    # Cleanup can be added here if needed
    
app = FastAPI(
    title="Image Generation Service",
    description="A secure image generation API using Hugging Face diffusers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_router, prefix="")
app.include_router(admin_router, prefix="")

# Serve static files (for CSS/JS if needed)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    # Return the main HTML page
    try:
        with open("frontend/templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {"message": "Image Generation Service API", "version": "1.0.0"}

@app.get("/documentation", response_class=HTMLResponse)
async def documentation():
    try:
        with open("frontend/templates/documentation.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Documentation not found")

@app.get("/admin", response_class=HTMLResponse)
async def admin_login():
    try:
        with open("frontend/templates/admin_login.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Admin login page not found")

@app.get("/admin/management", response_class=HTMLResponse)
async def admin_management():
    try:
        with open("frontend/templates/admin_management.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Admin management page not found")

@app.get("/client-test", response_class=HTMLResponse)
async def client_test():
    try:
        with open("frontend/templates/client_test.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Client test page not found")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
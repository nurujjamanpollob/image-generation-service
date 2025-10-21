#!/usr/bin/env python3
"""
Frontend Server for Image Generation Service
This file serves as a demo server to show the frontend pages.
In production, this would be replaced with the main.py server.
"""

import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Image Generation Service - Frontend Demo")

# Serve static files (CSS, JS if needed)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main homepage"""
    try:
        with open("frontend/templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {"message": "Image Generation Service API - Frontend Demo"}

@app.get("/documentation", response_class=HTMLResponse)
async def documentation():
    """Serve the documentation page"""
    try:
        with open("frontend/templates/documentation.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Documentation not found")

@app.get("/admin", response_class=HTMLResponse)
async def admin_login():
    """Serve the admin login page"""
    try:
        with open("frontend/templates/admin_login.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Admin login page not found")

@app.get("/admin/management", response_class=HTMLResponse)
async def admin_management():
    """Serve the admin management page"""
    try:
        with open("frontend/templates/admin_management.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Admin management page not found")

@app.get("/client-test", response_class=HTMLResponse)
async def client_test():
    """Serve the client test page"""
    try:
        with open("frontend/templates/client_test.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Client test page not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting frontend demo server...")
    print("Available endpoints:")
    print("  / - Homepage")
    print("  /documentation - Documentation")
    print("  /admin - Admin Login")
    print("  /admin/management - Admin Management")
    print("  /client-test - Client Test Page")
    print("\nStarting server on http://localhost:8000...")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
#!/usr/bin/env python3
"""
Quick start script for running the image generation service.
"""

import os
import sys
import subprocess

def main():
    print("Image Generation Service")
    print("=" * 30)
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import diffusers
        import torch
        print("✓ All required dependencies are installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return 1
    
    # Set default environment variables if not set
    if not os.getenv("MODEL_ID"):
        os.environ["MODEL_ID"] = "stabilityai/stable-diffusion-3.5-large"
        print(f"✓ Set MODEL_ID to default: {os.environ['MODEL_ID']}")
    
    if not os.getenv("ADMIN_API_KEY"):
        # Generate a simple admin key for demo purposes
        import secrets
        admin_key = secrets.token_urlsafe(32)
        os.environ["ADMIN_API_KEY"] = admin_key
        print(f"✓ Generated temporary ADMIN_API_KEY (use this to manage keys):")
        print(f"  {admin_key}")
        print("  NOTE: This is only for demo purposes. In production, set it securely.")
    
    # Check if the setup was run
    if not os.path.exists("api_keys.json"):
        print("✓ Creating initial API keys file...")
        with open("api_keys.json", "w") as f:
            import json
            json.dump({"api_keys": [os.environ["ADMIN_API_KEY"]]}, f)
    
    print("\nStarting service...")
    print("Service will be available at: http://localhost:8000")
    print("API endpoints:")
    print("  - POST /v1/generate/text-to-image")
    print("  - POST /v1/generate/image-to-image") 
    print("  - POST /v1/upscale/image")
    print("  - GET /downloads/{filename}")
    print("  - Admin endpoints: /admin/keys (requires ADMIN_API_KEY)")
    
    try:
        # Run the service
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Service failed to start: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nService stopped by user")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
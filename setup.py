#!/usr/bin/env python3
"""
Setup script for Image Generation Service.
This script helps with initial configuration, especially setting up the admin key.
"""

import json
import os
import secrets
import sys


def generate_secure_key():
    """Generate a cryptographically secure API key."""
    return secrets.token_urlsafe(32)

def setup_admin_key():
    """Setup or check admin key configuration."""
    # Check if ADMIN_API_KEY is already set in environment
    admin_key = os.getenv("ADMIN_API_KEY")
    
    if admin_key:
        print(f"✓ Admin key already configured (first 8 chars: {admin_key[:8]}...)")
        return True
    
    # Check if we have an api_keys.json file with keys
    if os.path.exists("api_keys.json"):
        try:
            with open("api_keys.json", "r") as f:
                data = json.load(f)
                if "api_keys" in data and len(data["api_keys"]) > 0:
                    print("✓ Found existing API keys in api_keys.json")
                    # Use the first key as admin key (for backwards compatibility)
                    admin_key = data["api_keys"][0]
                    os.environ["ADMIN_API_KEY"] = admin_key
                    print(f"✓ Using existing key as admin key: {admin_key[:8]}...")
                    return True
        except Exception as e:
            print(f"Error reading api_keys.json: {e}")
    
    # Generate new admin key
    print("No admin API key configured. Generating a new one...")
    admin_key = generate_secure_key()
    os.environ["ADMIN_API_KEY"] = admin_key
    
    print("\n" + "="*60)
    print("ADMIN API KEY GENERATED")
    print("="*60)
    print(f"Your new admin API key is:")
    print(admin_key)
    print("\nPlease set this as an environment variable:")
    print("export ADMIN_API_KEY=\"" + admin_key + "\"")
    print("\nThis key will be used to manage API keys.")
    print("="*60)
    
    # Save the key to a file for reference
    try:
        with open("admin_key.txt", "w") as f:
            f.write(admin_key)
        print("\nKey also saved to 'admin_key.txt' (keep this secure!)")
    except Exception as e:
        print(f"Warning: Could not save admin key to file: {e}")
    
    return True

def main():
    print("Image Generation Service Setup")
    print("="*40)
    
    # Create necessary directories
    os.makedirs("generated_images", exist_ok=True)
    print("✓ Created generated_images directory")
    
    # Setup admin key
    if setup_admin_key():
        print("\nSetup complete!")
        print("You can now run the service with:")
        print("python main.py")
        return 0
    else:
        print("Setup failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
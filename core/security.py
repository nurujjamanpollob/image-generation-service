import os
import json
import secrets
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# API keys file path
API_KEYS_FILE = "api_keys.json"

def load_api_keys() -> List[str]:
    """Load existing API keys from file."""
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('api_keys', [])
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            return []
    return []

def save_api_keys(api_keys: List[str]) -> None:
    """Save API keys to file."""
    try:
        with open(API_KEYS_FILE, 'w') as f:
            json.dump({'api_keys': api_keys}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving API keys: {e}")

def generate_api_key() -> str:
    """Generate a cryptographically secure API key."""
    return secrets.token_urlsafe(32)

def add_api_key(api_key: str) -> None:
    """Add a new API key to the system."""
    api_keys = load_api_keys()
    if api_key not in api_keys:
        api_keys.append(api_key)
        save_api_keys(api_keys)
        logger.info(f"Added new API key: {api_key[:8]}...")

def remove_api_key(api_key: str) -> bool:
    """Remove an existing API key from the system."""
    api_keys = load_api_keys()
    if api_key in api_keys:
        api_keys.remove(api_key)
        save_api_keys(api_keys)
        logger.info(f"Removed API key: {api_key[:8]}...")
        return True
    return False

def is_valid_api_key(api_key: str) -> bool:
    """Check if an API key is valid."""
    api_keys = load_api_keys()
    return api_key in api_keys

def get_admin_key() -> Optional[str]:
    """Get the admin key from environment variable or None if not set."""
    return os.getenv("ADMIN_API_KEY")

def create_admin_key() -> str:
    """Generate and set a new admin key."""
    admin_key = generate_api_key()
    os.environ["ADMIN_API_KEY"] = admin_key
    logger.info(f"New admin key generated: {admin_key[:8]}...")
    return admin_key

def initialize_api_keys() -> None:
    """Initialize API keys system with default admin key if needed."""
    api_keys = load_api_keys()
    
    # If no keys exist, create a default admin key
    if not api_keys:
        admin_key = create_admin_key()
        add_api_key(admin_key)
        logger.info("Created new admin key and initialized API keys system")
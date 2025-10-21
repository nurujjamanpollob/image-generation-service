from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from core.security import is_valid_api_key, get_admin_key

def validate_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Validate API key from X-API-KEY header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required in X-API-KEY header"
        )
    
    if not is_valid_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return x_api_key

def validate_admin_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Validate admin API key from X-API-KEY header."""
    admin_key = get_admin_key()
    if not admin_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin key not configured"
        )
    
    if not x_api_key or x_api_key != admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )
    
    return x_api_key
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status, Body
from fastapi.responses import JSONResponse

from core.security import (
    generate_api_key,
    add_api_key,
    remove_api_key,
    get_admin_key,
    load_api_keys,
)
from setting_api.settings_management import (
    add_or_update_setting,
    get_setting,
    get_all_settings,
)

router = APIRouter()


def validate_admin_key(x_api_key: Optional[str] = Header(None, alias="X-API-KEY")) -> str:
    """Validate admin API key from X-API-KEY header."""
    admin_key = get_admin_key()

    if not admin_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request Failed with Error Code 0x0",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request Failed with Error Code 0x1",
        )

    if x_api_key != admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request Failed with Error Code 0x2",
        )

    return x_api_key


@router.post("/admin/keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(admin_key: str = Depends(validate_admin_key)) -> JSONResponse:
    """Generate a new API key."""
    try:
        new_key = generate_api_key()
        add_api_key(new_key)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "API key created successfully", "api_key": new_key},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {e}",
        )


@router.delete("/admin/keys/{api_key}")
async def revoke_api_key(api_key: str, admin_key: str = Depends(validate_admin_key)) -> JSONResponse:
    """Revoke (delete) an existing API key."""
    try:
        if remove_api_key(api_key):
            return JSONResponse(content={"message": "API key revoked successfully"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {e}",
        )


@router.get("/admin/keys")
async def list_api_keys(admin_key: str = Depends(validate_admin_key)) -> JSONResponse:
    """List all active API keys."""
    try:
        api_keys: List[str] = load_api_keys()
        return JSONResponse(content={"api_keys": api_keys})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve API keys: {e}",
        )


@router.get("/admin/validate-key")
async def validate_admin_key_endpoint(admin_key: str = Depends(validate_admin_key)) -> JSONResponse:
    """Validate admin key (for testing purposes)."""
    return JSONResponse(content={"message": "Admin key is valid"})


# Settings endpoints
@router.get("/admin/settings")
async def get_all_settings_endpoint(admin_key: str = Depends(validate_admin_key)) -> JSONResponse:
    """Get all application settings."""
    try:
        settings: Dict[str, Any] = get_all_settings()
        return JSONResponse(content=settings)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve settings: {e}",
        )


@router.post("/admin/settings/{key}")
async def set_setting(
    key: str,
    value: Dict[str, Any] = Body(...),
    admin_key: str = Depends(validate_admin_key),
) -> JSONResponse:
    """Set a specific application setting."""
    try:
        # Validate the value based on key
        if key == "use_cpu_offloading":
            if value.get("value") not in [True, False]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid value for use_cpu_offloading. Must be true or false.",
                )
        elif key == "model_load_retentation_strategy":
            if value.get("value") not in ["keep", "reload"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid value for model_load_retentation_strategy. Must be 'keep' or 'reload'.",
                )

        add_or_update_setting(key, value.get("value"))
        return JSONResponse(content={"message": f"Setting {key} updated successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update setting: {e}",
        )


@router.get("/admin/settings/{key}")
async def get_setting_endpoint(key: str, admin_key: str = Depends(validate_admin_key)) -> JSONResponse:
    """Get a specific application setting."""
    try:
        value = get_setting(key)
        if value is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting {key} not found")
        return JSONResponse(content={key: value})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve setting: {e}",
        )

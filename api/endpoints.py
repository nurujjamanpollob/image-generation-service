import io
import logging
import os
import uuid
from datetime import datetime

from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse

from api.dependencies import validate_api_key
from api.schemas import (
    TextToImageRequest,
    TextToImageResponse,
    ImageToImageResponse,
    UpscaleImageResponse
)
from core.ml_models import (
    generate_text_to_image,
    generate_image_to_image,
    upscale_image
)
from core.security import is_valid_api_key

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
GENERATED_IMAGES_DIR = "generated_images"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def save_image(image: Image.Image, filename: str) -> str:
    """Save image to disk and return the full path."""
    filepath = os.path.join(GENERATED_IMAGES_DIR, filename)
    # Ensure the directory exists
    os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
    image.save(filepath)
    return filepath

def get_image_url(filename: str, api_key: str) -> str:
    """Generate a secure URL for downloading an image with API key."""
    return f"{BASE_URL}/downloads/{filename}?api_key={api_key}"

@router.post("/v1/generate/text-to-image", response_model=TextToImageResponse)
async def text_to_image(
    request: TextToImageRequest,
    api_key: str = Depends(validate_api_key)
):
    """Generate images from text prompt."""
    try:
        # Generate images
        images = generate_text_to_image(
            model_id=os.getenv("MODEL_ID", "stabilityai/stable-diffusion-3.5-large"),
            prompt=request.prompt,
            num_images=request.num_images,
            negative_prompt=request.negative_prompt,
            guidance_scale=request.guidance_scale
        )
        
        # Save images and collect URLs
        image_urls = []
        for i, image in enumerate(images):
            filename = f"{uuid.uuid4()}.png"
            save_image(image, filename)
            url = get_image_url(filename, api_key)
            image_urls.append(url)
        
        return TextToImageResponse(
            status="success",
            image_urls=image_urls,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in text-to-image generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate images: {str(e)}"
        )

@router.post("/v1/generate/image-to-image", response_model=ImageToImageResponse)
async def image_to_image(
    prompt: str = Form(...),
    reference_image: UploadFile = File(...),
    num_images: int = Form(1),
    strength: float = Form(0.8),
    api_key: str = Depends(validate_api_key)
):
    """Modify an existing image based on a text prompt."""
    try:
        # Read the uploaded image
        image_content = await reference_image.read()
        image = Image.open(io.BytesIO(image_content)).convert("RGB")
        
        # Generate images
        images = generate_image_to_image(
            model_id=os.getenv("MODEL_ID", "stabilityai/stable-diffusion-3.5-large"),
            prompt=prompt,
            reference_image=image,
            num_images=num_images,
            strength=strength
        )
        
        # Save images and collect URLs
        image_urls = []
        for i, image in enumerate(images):
            filename = f"{uuid.uuid4()}.png"
            save_image(image, filename)
            url = get_image_url(filename, api_key)
            image_urls.append(url)
        
        return ImageToImageResponse(
            status="success",
            image_urls=image_urls,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in image-to-image generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate images: {str(e)}"
        )

@router.post("/v1/upscale/image", response_model=UpscaleImageResponse)
async def upscale_image_endpoint(
    image_to_upscale: UploadFile = File(...),
    api_key: str = Depends(validate_api_key),
    prompt: str = Form("Make the image ultra high res")
):
    """Upscale an image to higher resolution."""
    try:
        # Read the uploaded image
        image_content = await image_to_upscale.read()
        original_image = Image.open(io.BytesIO(image_content)).convert("RGB")
        
        # Get original dimensions
        original_width, original_height = original_image.size
        
        # Upscale the image
        upscaled_image = upscale_image(image=original_image, prompt=prompt)
        
        # Save the upscaled image
        filename = f"{uuid.uuid4()}.png"
        save_image(upscaled_image, filename)
        
        # Get new dimensions
        new_width, new_height = upscaled_image.size
        
        return UpscaleImageResponse(
            status="success",
            image_url=get_image_url(filename, api_key),
            original_resolution=f"{original_width}x{original_height}",
            new_resolution=f"{new_width}x{new_height}",
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in image upscaling: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upscale image: {str(e)}"
        )

@router.get("/downloads/{filename}")
async def download_image(filename: str, api_key: str):
    """Secure endpoint to download generated images."""
    # Validate API key
    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    filepath = os.path.join(GENERATED_IMAGES_DIR, filename)

    # Make sure the path is safe and prevent directory traversal
    generated_dir_real = os.path.realpath(GENERATED_IMAGES_DIR)
    filepath_real = os.path.realpath(filepath)

    try:
        # Check if the common path of the generated directory and the requested file is the generated directory itself
        if os.path.commonpath([generated_dir_real, filepath_real]) != generated_dir_real:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
    except ValueError:
        # This can happen on Windows if paths are on different drives
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )

    # Check if file exists
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    return FileResponse(filepath, media_type="image/png")

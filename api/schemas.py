from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TextToImageRequest(BaseModel):
    prompt: str
    num_images: int = 1
    negative_prompt: Optional[str] = None
    guidance_scale: float = 7.5

class TextToImageResponse(BaseModel):
    status: str
    image_urls: List[str]
    generated_at: datetime

class ImageToImageRequest(BaseModel):
    prompt: str
    num_images: int = 1
    strength: float = 0.8

class ImageToImageResponse(BaseModel):
    status: str
    image_urls: List[str]
    generated_at: datetime

class UpscaleImageResponse(BaseModel):
    status: str
    image_url: str
    original_resolution: str
    new_resolution: str
    generated_at: datetime
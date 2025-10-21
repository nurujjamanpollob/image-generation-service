import logging
import torch
from PIL import Image
from diffusers import StableDiffusionUpscalePipeline
from diffusers import AutoPipelineForImage2Image as img_2_img

from . import models_loader

logger = logging.getLogger(__name__)

def generate_text_to_image(
    model_id: str,
    prompt: str,
    num_images: int = 1,
    negative_prompt: str = None,
    guidance_scale: float = 7.5
):
    """Generate images from a text prompt."""
    _model = models_loader.get_or_load_model(model_id)

    if _model is None:
        raise RuntimeError("Model not initialized")

    # Create args for generation
    try:
        # Prepare arguments for the model pipeline
        pipeline_args = {
            "prompt": prompt,
            "num_images_per_prompt": num_images,
            "guidance_scale": guidance_scale,
        }

        # Add negative_prompt only if it has a value
        if negative_prompt:
            pipeline_args["negative_prompt"] = negative_prompt

        # Generate images
        images = _model(**pipeline_args).images

        # Cleanup model if preference is set
        if models_loader.is_model_retentation_reload():
            models_loader.unload_model(model=_model)

        return images
    except Exception as e:
        # Log the error details
        logger.error(f"Error in text-to-image generation: {str(e)}")
        raise

# Image-to-Image generation function
def generate_image_to_image(
    model_id: str,
    prompt: str,
    reference_image: Image.Image,
    num_images: int = 1,
    strength: float = 0.8,
    guidance_scale: float = 7.5,
    negative_prompt: str = None
):
    """Modify an existing image based on a text prompt."""
    _model = models_loader.get_or_load_image_editing_model(model_id)

    if _model is None:
        raise RuntimeError("Model not initialized. Please call initialize_model first.")

    try:
        # Convert Image to RGB if not already in that mode and resize to expected size
        if reference_image.mode != "RGB":
            reference_image = reference_image.convert("RGB")
        reference_image = reference_image.resize((512, 512))
        pipeline_args = {
            "prompt": prompt,
            "image": reference_image,
            "num_images_per_prompt": num_images,
            "strength": strength,
            "guidance_scale": guidance_scale,
        }

        if negative_prompt:
            pipeline_args["negative_prompt"] = negative_prompt

        images = _model(**pipeline_args).images

        # Cleanup model if preference is set
        if models_loader.is_model_retentation_reload():
            models_loader.unload_model(model=_model)

        return images

    except Exception as e:
        logger.error(f"Error in image-to-image generation: {str(e)}")
        raise

# Upscale image function
def upscale_image(image: Image.Image, prompt: str ="Make the image ultra high res") -> Image.Image:
    """Upscale an image to a higher resolution."""
    try:
        device = models_loader.get_device()
        # Create upscaler pipeline
        upscaler = models_loader.get_or_load_upscaler_model("stabilityai/stable-diffusion-x4-upscaler").to(device)

        # Convert the image to the 512x512 size expected by the upscaler
        image = image.resize((512, 512))

        # Upscale image args
        args = {
            "image": image,
            "prompt": prompt,
        }

        upscaled_image = upscaler(**args).images[0]

        # Cleanup model if preference is set
        if models_loader.is_model_retentation_reload():
            models_loader.unload_model(model=upscaler)

        return upscaled_image

    except Exception as e:
        logger.error(f"Error in image upscaling: {str(e)}")
        raise



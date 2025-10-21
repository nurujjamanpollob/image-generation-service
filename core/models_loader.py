import logging
import os
from typing import Optional

import torch
from diffusers import AutoPipelineForText2Image
from diffusers import StableDiffusionUpscalePipeline
from diffusers import AutoPipelineForImage2Image as img_2_img
from setting_api.settings_management import (
    get_setting,
)
from diffusers import BitsAndBytesConfig, SD3Transformer2DModel
# Configure logger
logger = logging.getLogger(__name__)

# Global variables for the text-to-image model
_model = None
_model_id = None

# Global variables for the image-editing model
_image_editing_model = None
_image_editing_model_id = None

# Global variables for the upscaler model
_upscaler_model = None
_upscaler_model_id = None

"""Get the best available device (CUDA, XPU, or CPU)."""
def get_device():
    """Detect and return the best available device (CUDA, XPU, or CPU)."""
    if torch.cuda.is_available():
        device = "cuda"
        logger.info("Using CUDA device")
    elif hasattr(torch, "xpu") and torch.xpu.is_available():
        device = "xpu"
        logger.info("Using XPU device")
    else:
        device = "cpu"
        logger.info("Using CPU device")
    return device

# Helper function to resolve Hugging Face token
def resolve_hf_token(hf_token: Optional[str]) -> Optional[str]:
    """Resolve Hugging Face token from parameter or common environment variables."""
    if hf_token:
        return hf_token
    for env_var in ("HUGGINGFACE_HUB_TOKEN", "HF_HUB_TOKEN", "HF_TOKEN", "HUGGINGFACE_TOKEN"):
        val = os.environ.get(env_var)
        if val:
            logger.info(f"Using Hugging Face token from env var '{env_var}'")
            return val
    return None

# Used to get or load the image editing model, which is image-to-image
def get_or_load_image_editing_model(model_id: str, hf_token: Optional[str] = None):
    """
    Loads an image editing model if not already loaded, or if a different model is requested.
    Optionally uses a Hugging Face access token when downloading private models.
    Returns the model instance.
    """
    global _image_editing_model, _image_editing_model_id

    if _image_editing_model is not None and _image_editing_model_id == model_id:
        logger.info(f"Image editing model '{model_id}' is already loaded. Returning existing instance.")
        return _image_editing_model

    if _image_editing_model is not None and _image_editing_model_id != model_id:
        logger.info(f"Switching image editing model from '{_image_editing_model_id}' to '{model_id}'.")
        _image_editing_model = None

    try:
        device = get_device()
        logger.info(f"Loading image editing model '{model_id}' onto device '{device}'.")

        token = resolve_hf_token(hf_token)

        _inner_model = None

        # Use AutoPipelineForImage2Image for image-to-image tasks
        _inner_model = img_2_img.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            token=token,
            use_safetensors=True,
            transformer=create_sd3_transformer_2d_model_4bit(model_id, hf_token)
        )

        # If you use cpu offloading is enabled in settings, apply it
        if is_use_cpu_offload_enabled():
            logger.info(f"Enabling CPU offloading for the image editing model with Id '{model_id}'.")
            _inner_model.enable_model_cpu_offload()
            _inner_model.to("cpu") # Move model to CPU initially, for better memory management and gain
        else:

            _inner_model.to(device)

        _image_editing_model_id = model_id

        # Assign the loaded model to the global variable if retention strategy is not 'reload'
        if not is_model_retentation_reload():

            logger.info(f"Image editing model '{model_id}' loaded successfully.")
            # Cache the loaded model
            _image_editing_model = _inner_model
            return _image_editing_model
        else:
            logger.info(f"Image editing model '{model_id}' loaded successfully with 'reload' retention strategy. Which means after use it will be unloaded from memory.")
            _image_editing_model = None # Force reload next time
            return _inner_model

    except Exception as e:
        logger.error(f"Failed to load image editing model '{model_id}': {e}")
        _image_editing_model = None
        _image_editing_model_id = None
        raise RuntimeError(f"Could not load image editing model '{model_id}'.") from e


# Used to get or load the upscaler model

def get_or_load_upscaler_model(model_id: str = "stabilityai/stable-diffusion-x4-upscaler", hf_token: Optional[str] = None):
    """
    Loads an upscaler model if not already loaded, or if a different model is requested.
    Optionally uses a Hugging Face access token when downloading private models.
    Returns the model instance.
    """
    global _upscaler_model, _upscaler_model_id

    if _upscaler_model is not None and _upscaler_model_id == model_id:
        logger.info(f"Upscaler model '{model_id}' is already loaded. Returning existing instance.")
        return _upscaler_model

    if _upscaler_model is not None and _upscaler_model_id != model_id:
        logger.info(f"Switching upscaler model from '{_upscaler_model_id}' to '{model_id}'.")
        _upscaler_model = None

    try:
        device = get_device()
        logger.info(f"Loading upscaler model '{model_id}' onto device '{device}'.")

        token = resolve_hf_token(hf_token)

        _inner_model = None

        # Define common arguments for from_pretrained
        pretrained_args = {
            "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
            "token": token,
            "use_safetensors": True,
        }

        # Conditionally add the transformer for SD3 models
        if "sd3" in model_id.lower():
            pretrained_args["transformer"] = create_sd3_transformer_2d_model_4bit(model_id, hf_token)

        # Use StableDiffusionUpscalePipeline for upscaling tasks
        _inner_model = StableDiffusionUpscalePipeline.from_pretrained(
            model_id,
            **pretrained_args
        )

        _inner_model.enable_vae_tiling()
        _inner_model.enable_vae_slicing()

        # Move model to the target device
        _inner_model.to(device)

        _upscaler_model_id = model_id

        # Assign the loaded model to the global variable if retention strategy is not 'reload'
        if not is_model_retentation_reload():

            logger.info(f"Upscaler model '{model_id}' loaded successfully.")
            # Cache the loaded model
            _upscaler_model = _inner_model
            return _upscaler_model
        else:
            logger.info(f"Upscaler model '{model_id}' loaded successfully with 'reload' retention strategy. Which means after use it will be unloaded from memory.")
            _upscaler_model = None # Force reload next time
            return _inner_model

    except Exception as e:
        logger.error(f"Failed to load upscaler model '{model_id}': {e}")
        _upscaler_model = None
        _upscaler_model_id = None
        raise RuntimeError(f"Could not load upscaler model '{model_id}'.") from e


# Used to get or load the base image generation model, which is text-to-image
def get_or_load_model(model_id: str, hf_token: Optional[str] = None):
    """
    Loads a model if not already loaded, or if a different model is requested.
    Optionally uses a Hugging Face access token when downloading private models.
    Returns the model instance.
    """
    global _model, _model_id

    if _model is not None and _model_id == model_id:
        logger.info(f"Model '{model_id}' is already loaded. Returning existing instance.")
        return _model

    if _model is not None and _model_id != model_id:
        logger.info(f"Switching model from '{_model_id}' to '{model_id}'.")
        _model = None

    try:
        device = get_device()
        logger.info(f"Loading model '{model_id}' onto device '{device}'.")

        token = resolve_hf_token(hf_token)

        _inner_model = None

        # Use AutoPipelineForText2Image for text-to-image and image-to-image tasks
        _inner_model = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            token=token,
            use_safetensors=True,
            transformer = create_sd3_transformer_2d_model_4bit(model_id, hf_token)
        )

        # If you use cpu offloading is enabled in settings, apply it
        if is_use_cpu_offload_enabled():
            logger.info(f"Enabling CPU offloading for the model with Id '{model_id}'.")
            _inner_model.enable_model_cpu_offload()
            _inner_model.to("cpu") # Move model to CPU initially, for better memory management and gain
        else:

            _inner_model.to(device)

        _model_id = model_id

        # Assign the loaded model to the global variable if retention strategy is not 'reload'
        if not is_model_retentation_reload():

            logger.info(f"Model '{model_id}' loaded successfully.")
            # Cache the loaded model
            _model = _inner_model
            return _model
        else:
            logger.info(f"Model '{model_id}' loaded successfully with 'reload' retention strategy. Which means after use it will be unloaded from memory.")
            _model = None # Force reload next time
            return _inner_model

    except Exception as e:
        logger.error(f"Failed to load model '{model_id}': {e}")
        _model = None
        _model_id = None
        raise RuntimeError(f"Could not load model '{model_id}'.") from e


def is_use_cpu_offload_enabled() -> bool:
    """Check if CPU offloading is enabled in settings."""
    return get_setting("use_cpu_offloading") == True

def is_model_retentation_reload() -> bool:
    """Check if model load retention strategy is set to 'reload'."""
    return get_setting("model_load_retentation_strategy") == "reload"

# Unload instantiated models from memory
def unload_models():
    """Unload all loaded models from memory."""
    global _model, _model_id
    global _image_editing_model, _image_editing_model_id
    global _upscaler_model, _upscaler_model_id

    if _model is not None:
        logger.info(f"Unloading model '{_model_id}' from memory.")
        _model = None
        _model_id = None

    if _image_editing_model is not None:
        logger.info(f"Unloading image editing model '{_image_editing_model_id}' from memory.")
        _image_editing_model = None
        _image_editing_model_id = None

    if _upscaler_model is not None:
        logger.info(f"Unloading upscaler model '{_upscaler_model_id}' from memory.")
        _upscaler_model = None
        _upscaler_model_id = None

    logger.info("All models have been unloaded from memory.")

# Unload a specific model from memory
def unload_model(model) -> None:
    """Unload a specific model from memory."""
    global _model, _model_id
    global _image_editing_model, _image_editing_model_id
    global _upscaler_model, _upscaler_model_id

    if model == _model:
        logger.info(f"Unloading model '{_model_id}' from memory.")
        _model = None
        _model_id = None
    elif model == _image_editing_model:
        logger.info(f"Unloading image editing model '{_image_editing_model_id}' from memory.")
        _image_editing_model = None
        _image_editing_model_id = None
    elif model == _upscaler_model:
        logger.info(f"Unloading upscaler model '{_upscaler_model_id}' from memory.")
        _upscaler_model = None
        _upscaler_model_id = None
    else:
        # If model object is none of the known models, still clean the passed reference
        logger.info("Unloading unknown model reference from memory.")
        model = None
    logger.info("Specified model has been unloaded from memory.")



# Model bits and bytes config for 4-bit quantization
def get_bnb_4bit_config():
    """Get BitsAndBytesConfig for 4-bit quantization."""
    bnb_config = None

    # If nvidia gou, use double quantization for better performance
    if torch.cuda.is_available():

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_type=torch.float16
        )
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=False,
            bnb_4bit_compute_type=torch.float32
        )
    return bnb_config

# create SD3Transformer2DModel with 4-bit quantization
def create_sd3_transformer_2d_model_4bit(model_id: str, hf_token: Optional[str] = None):
    """Create SD3Transformer2DModel with 4-bit quantization."""
    token = resolve_hf_token(hf_token)

    model = SD3Transformer2DModel.from_pretrained(
        model_id,
        quantization_config=get_bnb_4bit_config(),
        subfolder="transformer",
        token=token,
        torch_dtype= get_device() == "cuda" and torch.float16 or torch.float32,
        use_safetensors=True
    )
    return model
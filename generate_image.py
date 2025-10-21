import argparse
import logging
import os
from PIL import Image
from core.models_loader import get_or_load_model as get_model
from core.ml_models import (
    generate_text_to_image,
    generate_image_to_image,
    upscale_image
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to parse arguments and perform the selected generative task.
    """
    parser = argparse.ArgumentParser(
        description="Generate or modify an image using a pre-trained model."
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="text-to-image",
        choices=["text-to-image", "image-to-image", "upscale"],
        help="The generative mode to use."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="The text prompt. Required for text-to-image and image-to-image."
    )
    parser.add_argument(
        "--input-image",
        type=str,
        help="Path to the input image. Required for image-to-image and upscale."
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="generated_image.png",
        help="The file path to save the generated image."
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="stabilityai/stable-diffusion-3.5-large",
        help="The Hugging Face model ID for text-to-image and image-to-image."
    )
    parser.add_argument(
        "--negative-prompt",
        type=str,
        help="An optional negative prompt for text-to-image."
    )
    parser.add_argument(
        "--guidance-scale",
        type=float,
        default=7.5,
        help="Guidance scale for text-to-image."
    )
    parser.add_argument(
        "--strength",
        type=float,
        default=0.8,
        help="Strength for image-to-image generation."
    )

    args = parser.parse_args()

    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        if args.mode == "text-to-image":
            if not args.prompt:
                parser.error("--prompt is required for text-to-image mode.")

            logger.info(f"Initializing model: {args.model_id}")
            if not get_model(args.model_id):
                logger.error("Model initialization failed. Exiting.")
                return

            # Log the parameters being used
            logger.info(f"Generation parameters: prompt='{args.prompt}', "
                        f"negative_prompt='{args.negative_prompt}', "
                        f"guidance_scale={args.guidance_scale}")

            logger.info(f"Generating image for prompt: '{args.prompt}'")
            images = generate_text_to_image(
                model_id=args.model_id,
                prompt=args.prompt,
                negative_prompt=args.negative_prompt,
                guidance_scale=args.guidance_scale
            )
            if images:
                images[0].save(args.output_path)
                logger.info(f"Image successfully saved to '{args.output_path}'")

        elif args.mode == "image-to-image":
            if not args.prompt or not args.input_image:
                parser.error("--prompt and --input-image are required for image-to-image mode.")

            logger.info(f"Initializing model: {args.model_id}")
            if not get_model(args.model_id):
                logger.error("Model initialization failed. Exiting.")
                return

            logger.info(f"Loading reference image from '{args.input_image}'")
            reference_image = Image.open(args.input_image).convert("RGB")

            logger.info("Generating image from image...")
            images = generate_image_to_image(
                model_id=args.model_id,
                prompt=args.prompt,
                reference_image=reference_image,
                strength=args.strength
            )
            if images:
                images[0].save(args.output_path)
                logger.info(f"Image successfully saved to '{args.output_path}'")

        elif args.mode == "upscale":
            if not args.input_image:
                parser.error("--input-image is required for upscale mode.")

            logger.info(f"Loading image to upscale from '{args.input_image}'")
            input_image = Image.open(args.input_image).convert("RGB")

            logger.info("Upscaling image...")
            # The upscale_image function in ml_models.py has a hardcoded scale_factor=4
            # in the pipeline call, so we don't pass it here.
            upscaled_image = upscale_image(image=input_image)
            if upscaled_image:
                upscaled_image.save(args.output_path)
                logger.info(f"Upscaled image successfully saved to '{args.output_path}'")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()

# python
import argparse
import logging
import os
import shlex
import sys
from datetime import datetime
from PIL import Image
from core.models_loader import get_or_load_model as get_model
from core.ml_models import (
    generate_text_to_image,
    generate_image_to_image,
    upscale_image
)

DEFAULT_MODEL_ID = "stabilityai/stable-diffusion-3.5-large"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_output_dir(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def parse_kv(tokens):
    out = {}
    for t in tokens:
        if "=" in t:
            k, v = t.split("=", 1)
            out[k.strip().lower()] = v
    return out

def default_output(prefix="generated", ext="png"):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}.{ext}"

def do_text_to_image(model_id, params):
    prompt = params.get("prompt")
    if not prompt:
        print("error: missing `prompt`")
        return
    output = params.get("output", default_output("text2img"))
    ensure_output_dir(output)
    neg = params.get("negative") or params.get("negative_prompt")
    guidance = float(params.get("guidance", 7.5))
    logger.info("Generating text-to-image...")
    imgs = generate_text_to_image(model_id=model_id, prompt=prompt, negative_prompt=neg, guidance_scale=guidance)
    if imgs:
        imgs[0].save(output)
        print(f"saved: {output}")
    else:
        print("error: generation returned no image")

def do_image_to_image(model_id, params):
    prompt = params.get("prompt")
    inp = params.get("input") or params.get("input_image")
    if not prompt or not inp:
        print("error: missing `prompt` or `input`")
        return
    output = params.get("output", default_output("img2img"))
    ensure_output_dir(output)
    try:
        ref = Image.open(inp).convert("RGB")
    except FileNotFoundError:
        print(f"error: input file not found: {inp}")
        return
    strength = float(params.get("strength", 0.8))
    logger.info("Generating image-to-image...")
    imgs = generate_image_to_image(model_id=model_id, prompt=prompt, reference_image=ref, strength=strength)
    if imgs:
        imgs[0].save(output)
        print(f"saved: {output}")
    else:
        print("error: generation returned no image")

def do_upscale(params):
    inp = params.get("input") or params.get("input_image")
    if not inp:
        print("error: missing `input`")
        return
    output = params.get("output", default_output("upscaled"))
    ensure_output_dir(output)
    try:
        img = Image.open(inp).convert("RGB")
    except FileNotFoundError:
        print(f"error: input file not found: {inp}")
        return
    logger.info("Upscaling...")
    out_img = upscale_image(image=img)
    if out_img:
        out_img.save(output)
        print(f"saved: {output}")
    else:
        print("error: upscaler returned no image")

def print_help():
    print(r"""Commands (simple key=value pairs):
  text-to-image prompt="..." [output=path] [negative="..."] [guidance=7.5]
  image-to-image input=path prompt="..." [output=path] [strength=0.8]
  upscale input=path [output=path]
  load-model id=MODEL_ID    (not allowed: model is static in this script)
  help
  quit

Examples:
  text-to-image prompt="A sunny beach" output=./out/beach.png
  image-to-image input=./in/photo.jpg prompt="Watercolor" strength=0.6
  upscale input=./in/small.png output=./out/large.png
""")

def main():
    parser = argparse.ArgumentParser(description="Interactive image generation REPL (static model load).")
    parser.add_argument("--model-id", type=str, default=DEFAULT_MODEL_ID, help="Model id to load once at startup.")
    args = parser.parse_args()

    # Static model load
    logger.info(f"Loading model: {args.model_id} (this happens once)")
    model_obj = get_model(args.model_id)
    if not model_obj:
        logger.error("Model initialization failed. Exiting.")
        sys.exit(1)
    model_id = args.model_id

    print(f"Interactive image generator (model: {model_id}). Type `help` for commands, `quit` to exit.")
    try:
        while True:
            try:
                line = input("cmd> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            if line.lower() in ("quit", "exit"):
                break
            if line.lower() in ("help", "h", "?"):
                print_help()
                continue

            try:
                tokens = shlex.split(line)
            except ValueError as e:
                print(f"parse error: {e}")
                continue
            cmd = tokens[0].lower()
            params = parse_kv(tokens[1:])

            if cmd in ("text-to-image", "text2img", "txt2img"):
                do_text_to_image(model_id, params)
            elif cmd in ("image-to-image", "img2img"):
                do_image_to_image(model_id, params)
            elif cmd == "upscale":
                do_upscale(params)
            elif cmd == "load-model":
                print("error: model is static in this script and cannot be reloaded at runtime")
            else:
                print(f"unknown command: {cmd}. Type `help`.")
    except Exception as e:
        logger.exception("fatal error")
    print("exiting.")

if __name__ == "__main__":
    main()

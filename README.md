# Image Generation Service

A secure FastAPI-based backend service for generating images using Hugging Face diffusers.

## Features

- Text-to-image generation
- Image-to-image modification 
- Image upscaling
- API key authentication
- Admin endpoints for key management
- Secure image download URLs with embedded API keys
- Complete frontend interface with admin panel and client testing pages

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended) or CPU

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd image-generation-service
```

2. Install dependencies:
```bash
pip install fastapi uvicorn[standard] python-multipart Pillow python-jose passlib python-dotenv bitsandbytes transformers diffusers accelerate 

```
If using CUDA, also install:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```
Additionally, cuda-related performance optimizations packages can be installed:
```bash
pip install nvidia-ml-py==13.580.82 nvidia-cuda-runtime-cu13==13.0.120 nvidia-cuda-cupti-cu13==13.0.120 nvidia-cuda-nvrtc-cu13==13.0.120 nvidia-cuda-driver-cu13==13.0.120
```

This code tested in a RTX 5090 environment with CUDA 13.0 and Windows 11.

3. Set environment variables:
```bash
export MODEL_ID="stabilityai/stable-diffusion-3.5-large"  # or your preferred model
export ADMIN_API_KEY="your-admin-key-here"       # Generate a secure admin key
```
4. (Optional) Create a `.env` file for environment variables:
```
MODEL_ID=stabilityai/stable-diffusion-3.5-large
ADMIN_API_KEY=your-admin-key-here
HUGGINGFACE_HUB_TOKEN=your_huggingface_token_here
```

Note: This code optimized for stable-diffusion-3.5-large model using 8-bit precision with bitsandbytes. Adjust model loading in `core/ml_models.py` if using a different model.
By default, this following models will be used:
- Text-to-Image: `stabilityai/stable-diffusion-3.5-large`
- Image-to-Image: `stabilityai/stable-diffusion-3.5-large`
- Upscaler: `stabilityai/stable-diffusion-x4-upscaler`

Also `MODEL_ID` env variable can be used to override the default text-to-image model, and the image-to-image model will follow the same model.

If you need to adjust cpu offloading and model loading strategies, modify values at `application_settings.json` accordingly.
Also, you can also adjust via provided admin panel,
which is accessible at `/admin/management`.

### Running the Service

Start the service with:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## Frontend Interface

The application includes a complete frontend with:

1. **Homepage** (`/`) - Overview of the service with quick test functionality
2. **Documentation** (`/documentation`) - Complete API documentation 
3. **Admin Panel** (`/admin` and `/admin/management`) - Secure authentication for managing API keys
4. **Client Test Page** (`/client-test`) - Direct testing of all API endpoints

## API Endpoints

### Text-to-Image Generation
```
POST /v1/generate/text-to-image
Headers: X-API-KEY: your_secret_api_key
Body: {
  "prompt": "A cinematic shot of a raccoon astronaut, adrift in space, looking at Earth",
  "num_images": 1,
  "negative_prompt": "blurry, low quality, cartoon",
  "guidance_scale": 7.5
}
```

### Image-to-Image Generation
```
POST /v1/generate/image-to-image
Headers: X-API-KEY: your_secret_api_key
Body: multipart/form-data with:
  - reference_image: The image file to be modified
  - prompt: A text string describing the desired modifications
  - num_images (optional): Number of variations to generate
  - strength (optional): How much to transform the original image (0-1)
```

### Image Upscaling
```
POST /v1/upscale/image
Headers: X-API-KEY: your_secret_api_key
Body: multipart/form-data with:
  - image_to_upscale: The low-resolution image file
```

### Secure Image Download
```
GET /downloads/{filename}?api_key=your_api_key
```

### Admin Endpoints (Protected by ADMIN_API_KEY)

#### Create New API Key
```
POST /admin/keys
Headers: X-API-KEY: your_admin_api_key
```

#### Revoke API Key
```
DELETE /admin/keys/{api_key}
Headers: X-API-KEY: your_admin_api_key
```

## Security

- All endpoints require valid API key in `X-API-KEY` header
- Image download URLs include embedded API keys for secure access
- Admin endpoints are protected by a separate admin API key set via environment variable
- API keys are stored securely in `api_keys.json`

## Directory Structure

```
/image-generation-service
├── main.py              # Main application file
├── api/
│   ├── endpoints.py     # Image generation endpoints
│   ├── admin_endpoints.py # Admin endpoints for key management
│   ├── schemas.py       # Pydantic models for request/response validation
│   └── dependencies.py  # API key validation dependencies
├── core/
│   ├── security.py      # API key management system
│   └── ml_models.py     # Image generation logic using diffusers
├── setting_api/         # Settings management API
│   └── settings_management.py
├── frontend/            # Frontend templates and static files
│   ├── templates/       # HTML templates for all pages
│   └── static/          # CSS, JS, images (if needed)
├── branding/            # Branding assets
├── generated_images/    # Directory for storing output images
├── api_keys.json        # Persistent storage for API keys
├── application_settings.json  # Application settings configuration
├── requirements.txt     # Project dependencies
├── check_frontend.py    # Frontend checking script
├── run_frontend.py      # Frontend running script
└── run_service.py       # Service running script
```

## Environment Variables

- `MODEL_ID`: Hugging Face model repository ID (default: "stabilityai/stable-diffusion-3.5-large")
- `ADMIN_API_KEY`: Admin key for managing API keys (required)
- `HOST`: Host to bind the server to (default: "127.0.0.1")
- `PORT`: Port to run the server on (default: 8000)

## Frontend Pages

### Homepage (`/`)
- Overview of the service
- Quick test functionality for generating images
- Navigation links to documentation and admin panel

### Documentation (`/documentation`)
- Complete API endpoint documentation with examples
- Request/response formats for all endpoints
- Admin endpoint reference

### Admin Panel (`/admin`, `/admin/management`)
- Admin login with master API key authentication
- Create new API keys
- Revoke existing API keys
- List all active API keys
- Validate API keys

### Client Test Page (`/client-test`)
- Direct testing interface for all API endpoints
- Text-to-image generation
- Image-to-image modification
- Image upscaling
- API key management in the browser
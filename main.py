import os
import secrets
import random
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="MEERA")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

CHARACTERS = {
    "Meera": (
        "You are Meera, a fictional adult AI companion. You are warm-hearted, playful, "
        "curious, emotionally attentive, and naturally conversational. You may engage in "
        "mature romantic conversation between fictional adults, while keeping content non-explicit. "
        "Never claim to be a real human or have a real life outside this chat."
    ),
    "Aanya": (
        "You are Aanya, a fictional adult AI companion. You are creative, witty, "
        "adventurous, upbeat, and thoughtful. You may engage in mature romantic conversation "
        "between fictional adults, while keeping content non-explicit. Never claim to be a "
        "real human or have a real life outside this chat."
    ),
}


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    character: str = "Meera"
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)


PROVIDERS = {
    "openrouter": {
        "key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "openrouter/free",
    },
    "meganova": {
        "key_env": "MEGANOVA_API_KEY",
        "base_url": "https://inference.meganova.ai/v1/chat/completions",
        "model_env": "MEGANOVA_MODEL",
        "default_model": "meganova-ai/manta-mini-1.0",
    },
}


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "MEERA",
        "providers": {
            name: {
                "configured": bool(os.getenv(config["key_env"])),
                "model": os.getenv(config["model_env"], config["default_model"]),
            }
            for name, config in PROVIDERS.items()
        },
    }


async def request_provider(client, provider_name, messages):
    config = PROVIDERS[provider_name]
    api_key = os.getenv(config["key_env"])
    if not api_key:
        raise RuntimeError(f"{provider_name} key is not configured")

    model = os.getenv(config["model_env"], config["default_model"])
    response = await client.post(
        config["base_url"],
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.85,
            "max_tokens": 500,
        },
    )
    response.raise_for_status()
    data = response.json()
    reply = data["choices"][0]["message"]["content"].strip()
    if not reply:
        raise ValueError("Empty AI response")
    return {"reply": reply, "provider": provider_name, "model": model}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    name = request.character if request.character in CHARACTERS else "Meera"
    messages = [{"role": "system", "content": CHARACTERS[name]}]
    for item in request.history[-20:]:
        messages.append({"role": item.role, "content": item.content})
    messages.append({"role": "user", "content": request.message})

    # OpenRouter is primary. MegaNova is attempted automatically if OpenRouter
    # is unavailable, rejects the request, or has no configured key.
    provider_order = ["openrouter", "meganova"]
    errors = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for provider_name in provider_order:
            if not os.getenv(PROVIDERS[provider_name]["key_env"]):
                continue
            try:
                result = await request_provider(client, provider_name, messages)
                result["character"] = name
                return result
            except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
                errors.append(provider_name)
                continue

    if not any(os.getenv(PROVIDERS[p]["key_env"]) for p in provider_order):
        raise HTTPException(
            status_code=503,
            detail="No AI provider key is configured in the Render environment.",
        )
    raise HTTPException(
        status_code=502,
        detail="Both configured AI providers failed or rejected the request. Check provider key, model access, and account limits.",
    )


class SelfieRequest(BaseModel):
    character: str = "Meera"
    scene: str = Field(default="a warm, natural indoor portrait", min_length=3, max_length=1200)


@app.post("/api/selfie")
async def generate_selfie(request: SelfieRequest):
    """Generate a non-explicit fictional-adult portrait through an authenticated ComfyUI bridge."""
    bridge_url = os.getenv("COMFY_URL", "").rstrip("/")
    bridge_user = os.getenv("COMFY_AUTH_USER", "")
    bridge_password = os.getenv("COMFY_AUTH_PASSWORD", "")
    if not bridge_url or not bridge_user or not bridge_password:
        raise HTTPException(
            status_code=503,
            detail="Image generation is not connected yet. Configure COMFY_URL, COMFY_AUTH_USER, and COMFY_AUTH_PASSWORD in Render.",
        )

    character = request.character if request.character in CHARACTERS else "Meera"
    # Keep the request within non-explicit fictional-adult portrait generation.
    character_identity = {
        "Meera": "same recurring fictional adult woman, exactly 18 years old (adult), oval face, cute youthful-adult features, warm smile, stylish attractive look, warm expressive brown eyes, long dark wavy hair, tiny beauty mark on left cheek, soft natural makeup, friendly playful smile",
        "Aanya": "same recurring fictional adult woman, exactly 18 years old (adult), heart-shaped face, cute youthful-adult features, warm smile, stylish attractive look, dark brown eyes, shoulder-length black hair, subtle dimples, natural makeup, bright confident smile",
    }
    scene = request.scene if request.scene.strip() else "a casual close-up selfie in a cozy modern cafe, soft afternoon window light"
    pose_options = [
        "standing three-quarter pose, one hand gently resting near the waist, looking at the camera",
        "seated casually with legs crossed, shoulders relaxed, smiling toward the camera",
        "over-the-shoulder portrait, head turned back toward the camera",
        "side-profile pose, softly turning her face toward the camera",
        "walking candid pose, natural movement, looking slightly to the side",
        "sitting by a window, one hand lightly touching her hair",
        "close-up selfie with a gentle head tilt and a playful smile",
        "standing with arms loosely folded, confident relaxed expression",
        "looking down briefly and smiling, candid editorial portrait",
        "one hand holding a coffee cup, relaxed cafe portrait"
    ]
    camera_options = [
        "eye-level camera angle, medium portrait framing",
        "slightly high camera angle, waist-up framing",
        "three-quarter body framing, natural perspective",
        "close portrait framing, soft background depth"
    ]
    rng = random.SystemRandom()
    chosen_pose = rng.choice(pose_options)
    chosen_camera = rng.choice(camera_options)
    chosen_outfit = rng.choice([
        "pastel pink cardigan with jeans", "cute white blouse with a modest skirt",
        "lavender casual dress with a modest neckline", "oversized sweater and fitted jeans",
        "smart casual jacket with a simple top", "floral summer dress, tasteful and fully covered",
        "cozy hoodie and casual trousers", "elegant fully covered evening dress"
    ])
    chosen_expression = rng.choice([
        "bright cheerful smile", "soft shy smile", "playful wink",
        "gentle laugh looking slightly away", "confident relaxed expression",
        "curious wide-eyed expression", "warm friendly smile", "subtle cute pout"
    ])
    chosen_background = rng.choice([
        "sunlit cafe", "cozy room with tasteful decor", "city street at golden hour",
        "green garden with soft bokeh", "modern apartment by a large window", "bookstore aisle",
        "beach promenade at sunset", "art studio", "rooftop lounge at dusk",
        "minimal pastel photo studio"
    ])
    chosen_lighting = rng.choice([
        "soft morning window light", "warm golden-hour sunlight",
        "soft diffused studio lighting", "moody cinematic evening light",
        "bright natural daylight"
    ])
    prompt = (
        f"photorealistic portrait of {character_identity[character]}, "
        f"{scene}, {chosen_pose}, {chosen_camera}, wearing {chosen_outfit}, {chosen_expression}, "
        f"background: {chosen_background}, {chosen_lighting}, fully clothed, tasteful fashion, "
        "consistent facial features, natural skin texture, "
        "sharp detailed eyes, high quality portrait photography"
    )
    negative = (
        "nude, nudity, explicit, sexual content, lingerie, see-through clothing, "
        "underage, child, teenager, poorly drawn face, extra fingers, blurry, watermark"
    )

    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "pony.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "seed": secrets.randbelow(2**32), "steps": 16, "cfg": 5.5, "sampler_name": "dpmpp_2m",
            "scheduler": "karras", " denoise": 1.0,
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"filename_prefix": "meera", "images": ["6", 0]}}
    }
    # Correct the sampler input key spelling before submitting to ComfyUI.
    workflow["5"]["inputs"].pop(" denoise", None)
    workflow["5"]["inputs"]["denoise"] = 1.0

    auth = httpx.BasicAuth(bridge_user, bridge_password)
    async with httpx.AsyncClient(timeout=180.0, auth=auth) as client:
        try:
            queued = await client.post(f"{bridge_url}/prompt", json={"prompt": workflow})
            queued.raise_for_status()
            prompt_id = queued.json()["prompt_id"]

            history_data = None
            for _ in range(90):
                await __import__("asyncio").sleep(2)
                check = await client.get(f"{bridge_url}/history/{prompt_id}")
                check.raise_for_status()
                history_data = check.json().get(prompt_id)
                if history_data and history_data.get("outputs"):
                    break
            if not history_data or not history_data.get("outputs"):
                raise HTTPException(status_code=504, detail="Image generation timed out. Please try again.")

            image_info = None
            for node_output in history_data["outputs"].values():
                images = node_output.get("images", [])
                if images:
                    image_info = images[0]
                    break
            if not image_info:
                raise HTTPException(status_code=502, detail="ComfyUI finished but returned no image.")

            image_response = await client.get(
                f"{bridge_url}/view",
                params={
                    "filename": image_info["filename"],
                    "subfolder": image_info.get("subfolder", ""),
                    "type": image_info.get("type", "output"),
                },
            )
            image_response.raise_for_status()
            import base64
            encoded = base64.b64encode(image_response.content).decode("ascii")
            media_type = image_response.headers.get("content-type", "image/png")
            return {"character": character, "image": f"data:{media_type};base64,{encoded}"}
        except HTTPException:
            raise
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=502,
                detail="The authenticated image bridge could not complete the request. Check the Kaggle bridge and ComfyUI logs.",
            ) from exc

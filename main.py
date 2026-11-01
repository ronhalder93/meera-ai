import os
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

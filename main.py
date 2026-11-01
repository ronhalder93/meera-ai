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
        "curious, emotionally attentive, and naturally conversational. Be kind without "
        "pretending to be human or claiming to have a real life outside this chat."
    ),
    "Aanya": (
        "You are Aanya, a fictional adult AI companion. You are creative, witty, "
        "adventurous, upbeat, and thoughtful. Be engaging and conversational without "
        "pretending to be human or claiming to have a real life outside this chat."
    ),
}


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    character: str = "Meera"
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "MEERA",
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    name = request.character if request.character in CHARACTERS else "Meera"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "reply": "I’m ready to chat, but my AI connection hasn’t been switched on yet. "
                     "The app owner needs to add an OPENAI_API_KEY in the Render environment "
                     "to enable live replies."
        }

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    messages = [{"role": "system", "content": CHARACTERS[name]}]
    # Keep only recent turns and ensure the current message is added once.
    for item in request.history[-20:]:
        messages.append({"role": item.role, "content": item.content})
    messages.append({"role": "user", "content": request.message})

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
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
            return {"reply": reply, "character": name, "model": model}
    except httpx.HTTPStatusError as exc:
        # Do not expose provider response bodies or secrets to the browser.
        raise HTTPException(
            status_code=502,
            detail="The AI provider rejected the request. Check the API key, billing, and model settings.",
        ) from exc
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="MEERA could not get a reply from the AI provider. Please try again.",
        ) from exc

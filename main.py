from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="MEERA")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

class ChatRequest(BaseModel):
    message: str
    character: str = "Meera"

@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "app": "MEERA"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    name = request.character if request.character in {"Meera", "Aanya"} else "Meera"
    reply = (
        f"Hey, I'm {name}. I’m glad you told me that. "
        "Tell me a little more — I’m listening. (Demo reply; connect an AI provider for live conversation.)"
    )
    return {"reply": reply}

# MEERA

An original, responsive AI-companion web app starter with a warm, premium dark interface.

## Included in this first build
- Responsive companion discovery page
- Two fictional adult companion demo profiles
- Interactive chat panel and message composer
- FastAPI backend with health check and demo chat endpoint
- Render-ready Python start command

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000

## Deploy on Render
Create a **Web Service** connected to this repository:
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

No paid API key is required for this demo. The chat endpoint currently returns an illustrative demo response; connect a chosen language-model provider before treating it as a real AI chat product.

## Next milestones
1. Persistent accounts and conversation history
2. Character editor and per-character memory
3. Secure AI provider integration
4. Private image gallery and non-explicit fictional-adult portrait generation
5. Optional non-explicit talking-avatar/video workflow

## Safety and privacy
Do not put API keys in frontend files or commit them to Git. Use Render environment variables for secrets. Do not expose an unauthenticated ComfyUI instance to the public internet. Character portraits and experiences should depict fictional adults (18+) and remain non-explicit.


## Self-hosted GLM configuration

Set these environment variables on the hosting service:

- `GLM_API_KEY`: bearer token accepted by your inference server.
- `GLM_BASE_URL`: OpenAI-compatible API base URL (for example, a server's `/v1` base, or its full `/v1/chat/completions` endpoint).
- `GLM_MODEL`: model name exposed by that server. Defaults to `zandenAI/GLM-5.2-FP8-Uncensored`; override it if your server uses a different served-model alias.

The model must already be running and reachable from the MEERA backend. This integration connects MEERA's chat replies to GLM; it does **not** turn the chat into a repository-editing coding agent. A separate sandboxed coding-agent service and narrowly scoped GitHub authorization are still required for that capability.

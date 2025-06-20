from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
import uuid
import os
from agents.tech_logo.workflow import LogoDesignOrchestrator
import dotenv
dotenv.load_dotenv()
app = FastAPI()
orchestrator = LogoDesignOrchestrator()

# -------------------------
# Serve Frontend Static HTML
# -------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

print("--------------------------------------------------")
print(os.getenv("OPENAI_API_KEY"))
print("--------------------------------------------------")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    html_path = Path("static/index.html")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

# -------------------------
# Session Start Endpoint
# -------------------------
@app.get("/tech_logo")
async def start_session():
    session_id = str(uuid.uuid4())
    result = orchestrator.start_session(session_id)
    return {
        "session_id": session_id,
        "message": result["message"]
    }

# -------------------------
# Message Endpoint
# -------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    result = await orchestrator.process_user_message(
        session_id=request.session_id,
        user_message=request.message
    )
    return result
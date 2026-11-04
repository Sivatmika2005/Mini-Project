"""FastAPI Backend Server for AI Mental Wellness Companion.
Connects the React frontend directly with existing Python backend modules.
"""
import os
import sys

# Configure UTF-8 stdout/stderr for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from typing import Optional, List
from dotenv import load_dotenv

# Load env variables early
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils import auth, db, llm, translations, tts
from utils.emotion_classifier import predict_emotion

# Initialize database
try:
    db.init_db()
except Exception as e:
    print(f"Warning: db initialization note: {e}")

app = FastAPI(title="AI Mental Wellness Companion API", version="1.0.0")

# CORS middleware for React Vite frontend (allowing all localhost/127.0.0.1 ports with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )


# ---------- Pydantic Request Models ----------

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class ConfirmResetRequest(BaseModel):
    oob_code: str
    new_password: str

class UpdateNameRequest(BaseModel):
    new_name: str

class SettingsRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None

class CheckInRequest(BaseModel):
    mood: str
    emotion_note: Optional[str] = ""
    stress_level: int = 5
    energy_level: int = 5
    sleep_quality: str = "Fair"
    journal_note: Optional[str] = ""

class JournalRequest(BaseModel):
    title: Optional[str] = ""
    content: str
    mood: Optional[str] = "😌 Calm"
    category: Optional[str] = "General"

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Chat"

class ConversationTitleRequest(BaseModel):
    title: str

class ChatMessageRequest(BaseModel):
    message: str

class CompanionChatRequest(BaseModel):
    message: str


# ---------- Authentication Helper Dependency ----------

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1].strip()
    if not token or len(token) < 32:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed or invalid session token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get_user_by_session_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired, invalid, or revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ---------- API Routes ----------

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "AI Mental Wellness Companion"}


# --- Auth Routes ---

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    username = (req.username or "").strip()
    email = (req.email or "").strip()
    password = req.password or ""

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email, and password cannot be empty.")

    success, msg = auth.register_user(username, email, password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    # Auto-login after registration
    user = auth.authenticate_user(email, password)
    token = None
    if user and user != "NETWORK_ERROR":
        token = db.create_user_session(user["id"])
    return {"success": True, "message": msg, "token": token, "user": user if token else None}


@app.post("/api/auth/login")
def login(req: LoginRequest):
    identifier = (req.username_or_email or "").strip()
    password = req.password or ""

    if not identifier or not password:
        raise HTTPException(status_code=400, detail="Username/email and password cannot be empty.")

    user = auth.authenticate_user(identifier, password)
    if user == "NETWORK_ERROR":
        raise HTTPException(status_code=503, detail="Could not reach authentication server. Please try again.")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password.")
    
    token = db.create_user_session(user["id"])
    settings = db.get_user_settings(user["id"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        },
        "settings": settings,
    }


@app.post("/api/auth/logout")
def logout(current_user: dict = Depends(get_current_user), authorization: Optional[str] = Header(None)):
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            db.delete_user_session(parts[1].strip())
    return {"success": True, "message": "Successfully logged out and session revoked."}


@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    settings = db.get_user_settings(current_user["id"])
    return {
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
        },
        "settings": settings,
    }


@app.post("/api/auth/reset-password-request")
def reset_password_request(req: PasswordResetRequest):
    success, msg = auth.send_password_reset_request(req.email)
    return {"success": success, "message": msg}


@app.post("/api/auth/confirm-reset")
def confirm_password_reset(req: ConfirmResetRequest):
    success, msg = auth.confirm_password_reset_with_code(req.oob_code, req.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


# --- User Settings & Profile ---

@app.get("/api/user/settings")
def get_settings(current_user: dict = Depends(get_current_user)):
    return db.get_user_settings(current_user["id"])


@app.post("/api/user/settings")
def save_settings(req: SettingsRequest, current_user: dict = Depends(get_current_user)):
    settings = db.save_user_settings(current_user["id"], theme=req.theme, language=req.language)
    return {"success": True, "settings": settings}


@app.post("/api/user/update-name")
def update_user_name(req: UpdateNameRequest, current_user: dict = Depends(get_current_user)):
    success, msg = db.update_user_username(current_user["id"], req.new_name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "username": req.new_name.strip()}


# --- Check-In Routes ---

@app.get("/api/checkins/latest")
def get_latest_checkin(current_user: dict = Depends(get_current_user)):
    latest = db.get_latest_checkin(current_user["id"])
    return {"latest": latest}


@app.get("/api/checkins")
def get_all_checkins(limit: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    checkins = db.get_checkins(current_user["id"], limit=limit)
    return {"checkins": checkins}


@app.post("/api/checkins")
def submit_checkin(req: CheckInRequest, current_user: dict = Depends(get_current_user)):
    checkin_id = db.add_checkin(
        user_id=current_user["id"],
        mood=req.mood,
        emotion_note=req.emotion_note or "",
        stress_level=req.stress_level,
        energy_level=req.energy_level,
        sleep_quality=req.sleep_quality,
        journal_note=req.journal_note or "",
    )
    if req.journal_note and req.journal_note.strip():
        db.add_journal_entry(
            user_id=current_user["id"],
            title=f"Check-In Note: {req.mood}",
            content=req.journal_note.strip(),
            mood=req.mood,
            category="Check-In",
        )
    return {"success": True, "id": checkin_id}


# --- Journal Routes ---

@app.get("/api/journals")
def get_journals(current_user: dict = Depends(get_current_user)):
    entries = db.get_journal_entries(current_user["id"])
    # Enhance entries with emotion predictions
    for e in entries:
        try:
            emo = predict_emotion(e.get("content", ""))
            e["emotion"] = emo.get("emotion", "Neutral")
            e["confidence"] = emo.get("confidence", 0.7)
        except Exception:
            e["emotion"] = "Neutral"
            e["confidence"] = 0.5
    return {"entries": entries}


@app.post("/api/journals")
def create_journal_entry(req: JournalRequest, current_user: dict = Depends(get_current_user)):
    title = req.title.strip() if req.title and req.title.strip() else f"{req.category or 'General'} Entry"
    journal_id = db.add_journal_entry(
        user_id=current_user["id"],
        title=title,
        content=req.content.strip(),
        mood=req.mood or "😌 Calm",
        category=req.category or "General",
    )
    return {"success": True, "id": journal_id}


@app.delete("/api/journals/{entry_id}")
def delete_journal(entry_id: int, current_user: dict = Depends(get_current_user)):
    success = db.delete_journal_entry(entry_id, current_user["id"])
    return {"success": success}


@app.post("/api/journals/summarize")
def summarize_journals(current_user: dict = Depends(get_current_user)):
    entries = db.get_journal_entries(current_user["id"])
    if not entries:
        return {"summary": "No journal entries found to summarize."}
    
    recent_text = "\n".join([f"- {e['title']}: {e['content'][:120]}" for e in entries[:5]])
    summary = llm.get_chat_response(
        user_message=f"Summarize these journal entries and provide 2 gentle insights:\n{recent_text}",
        history=[],
    )
    return {"summary": summary}


# --- Chat & Conversation Routes ---

@app.get("/api/chat/conversations")
def get_conversations(current_user: dict = Depends(get_current_user)):
    convs = db.get_conversations(current_user["id"])
    return {"conversations": convs}


@app.post("/api/chat/conversations")
def create_conversation(req: ConversationCreateRequest, current_user: dict = Depends(get_current_user)):
    conv_id = db.create_conversation(current_user["id"], title=req.title or "New Chat")
    return {"id": conv_id, "title": req.title or "New Chat"}


@app.put("/api/chat/conversations/{conv_id}")
def update_conversation_title(conv_id: int, req: ConversationTitleRequest, current_user: dict = Depends(get_current_user)):
    success = db.update_conversation_title(conv_id, current_user["id"], req.title)
    return {"success": success}


@app.delete("/api/chat/conversations/{conv_id}")
def delete_conversation(conv_id: int, current_user: dict = Depends(get_current_user)):
    success = db.delete_conversation(conv_id, current_user["id"])
    return {"success": success}


@app.get("/api/chat/conversations/{conv_id}/messages")
def get_conversation_messages(conv_id: int, current_user: dict = Depends(get_current_user)):
    messages = db.get_conversation_messages(conv_id, current_user["id"])
    return {"messages": messages}


@app.post("/api/chat/conversations/{conv_id}/messages")
def send_chat_message(conv_id: int, req: ChatMessageRequest, current_user: dict = Depends(get_current_user)):
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # 1. Fetch conversation history
    history = db.get_conversation_messages(conv_id, current_user["id"])
    history_formatted = [{"role": m["role"], "content": m["content"]} for m in history]

    # 2. Context from latest checkin & journals
    latest_checkin = db.get_latest_checkin(current_user["id"])
    stress_lvl = latest_checkin["stress_level"] if latest_checkin else None
    mood_context = f"Most recent mood: {latest_checkin['mood']}, stress {latest_checkin['stress_level']}/10" if latest_checkin else ""
    
    journals = db.get_journal_entries(current_user["id"])
    journal_sum = journals[0].get("title") or journals[0].get("content", "")[:60] if journals else ""

    # 3. Emotion classification on user message
    try:
        emo_data = predict_emotion(user_msg)
        emotion = emo_data.get("emotion", "Neutral")
    except Exception:
        emotion = "Neutral"

    # 4. Save user message
    db.add_conversation_message(conv_id, current_user["id"], "user", user_msg)

    # 5. Call External AI API
    ai_reply = llm.get_external_ai_chat_response(
        user_message=user_msg,
        history=history_formatted,
        mood_context=mood_context,
        stress_level=stress_lvl,
        journal_summary=journal_sum,
    )

    # 6. Save assistant message
    db.add_conversation_message(conv_id, current_user["id"], "assistant", ai_reply)

    # 7. If this is the first message in the conversation, auto-generate title
    new_title = None
    if len(history) == 0:
        new_title = llm.generate_chat_title(user_msg)
        db.update_conversation_title(conv_id, current_user["id"], new_title)

    return {
        "reply": ai_reply,
        "emotion": emotion,
        "new_title": new_title,
    }


# --- Dashboard Voice & Text Robot Companion Endpoint (Isolated from AI Chat) ---

@app.post("/api/companion/chat")
def companion_chat(req: CompanionChatRequest, current_user: dict = Depends(get_current_user)):
    user_prompt = req.message.strip()
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # 1. Context from latest checkin & journals for emotional grounding
    latest_checkin = db.get_latest_checkin(current_user["id"])
    stress_lvl = latest_checkin["stress_level"] if latest_checkin else None
    mood_context = f"Most recent mood: {latest_checkin['mood']}, stress {latest_checkin['stress_level']}/10" if latest_checkin else ""
    
    journals = db.get_journal_entries(current_user["id"])
    journal_sum = journals[0].get("title") or journals[0].get("content", "")[:60] if journals else ""

    # 2. Call Dashboard Robot Companion independently
    ai_reply = llm.get_companion_response(
        user_message=user_prompt,
        mood_context=mood_context,
        stress_level=stress_lvl,
        journal_summary=journal_sum,
    )

    clean_speech_text = tts.clean_text_for_speech(ai_reply)

    return {
        "reply": ai_reply,
        "clean_speech_text": clean_speech_text,
    }


# --- Translations ---

@app.get("/api/translations")
def get_all_translations():
    return {
        "current_lang": translations.get_current_language(),
        "available_languages": list(translations.TRANSLATIONS.keys()),
        "dictionary": translations.TRANSLATIONS,
    }


# --- Static Frontend Serving for Cloud Deployment ---

frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import FileResponse

    assets_path = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)

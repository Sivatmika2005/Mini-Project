"""Firebase Cloud Firestore database layer for AI Wellness app.
Handles all CRUD operations isolatable per user_id, maintaining 100% exact public API
compatibility with the original SQLite interface so zero UI code changes are needed.
"""

import os
import secrets
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

def _find_key_path():
    env_path = os.getenv("FIREBASE_KEY_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(project_root, "firebase-key.json"),
        os.path.join(os.path.dirname(project_root), "firebase-key.json"),
        os.path.join(os.getcwd(), "firebase-key.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

KEY_PATH = _find_key_path()


def _now():
    return datetime.now().isoformat()


def get_firestore_client():
    key_file = _find_key_path()
    if not os.path.exists(key_file):
        raise FileNotFoundError(
            f"Missing Firebase credentials key at {key_file}. "
            "Please ensure firebase-key.json is present in the project root."
        )
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_file)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def init_db():
    """Initialize Firebase client. Safe to call on app startup."""
    get_firestore_client()


def _get_next_id(db_fs, counter_name: str) -> int:
    """Atomic counter generator for integer IDs compatible with original schema."""
    counter_ref = db_fs.collection("counters").document(counter_name)

    @firestore.transactional
    def update_in_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        new_val = 1
        if snapshot.exists:
            data = snapshot.to_dict() or {}
            new_val = data.get("last_id", 0) + 1
        transaction.set(ref, {"last_id": new_val}, merge=True)
        return new_val

    transaction = db_fs.transaction()
    return update_in_transaction(transaction, counter_ref)


# ---------- User operations ----------

def create_user(username, email, firebase_uid="", password_hash=""):
    db_fs = get_firestore_client()
    user_id = _get_next_id(db_fs, "users")
    now_str = _now()
    user_data = {
        "id": user_id,
        "username": (username or "").strip(),
        "email": (email or "").strip().lower(),
        "created_at": now_str,
    }
    # Sanitize firebase_uid to prevent accidental plaintext password leakage
    if firebase_uid and not any(c in firebase_uid for c in "!@#$%^&*() ="):
        user_data["firebase_uid"] = firebase_uid
    if password_hash:
        user_data["password_hash"] = password_hash
    db_fs.collection("users").document(str(user_id)).set(user_data)
    return user_id


def update_user_password_hash(user_id, password_hash):
    """Updates password hash securely in Firestore and clears any legacy plain fields."""
    if not user_id or not password_hash:
        return False
    db_fs = get_firestore_client()
    doc_ref = db_fs.collection("users").document(str(user_id))
    doc = doc_ref.get()
    if not doc.exists:
        return False
    update_data = {
        "password_hash": password_hash,
        "password_updated_at": _now(),
    }
    # Remove legacy salt if it existed
    user_dict = doc.to_dict() or {}
    if "salt" in user_dict:
        update_data["salt"] = firestore.DELETE_FIELD
    # Also clean up legacy plaintext passwords if they were inadvertently saved in firebase_uid
    fb_uid = str(user_dict.get("firebase_uid", ""))
    if fb_uid and any(c in fb_uid for c in "!@#$%^&*() ="):
        update_data["firebase_uid"] = ""
    doc_ref.update(update_data)
    return True



def update_user_username(user_id, new_username):
    new_username = (new_username or "").strip()
    if not new_username or len(new_username) < 2:
        return False, "Name must be at least 2 characters."
    db_fs = get_firestore_client()
    query = db_fs.collection("users").where(filter=FieldFilter("username", "==", new_username)).get()
    for doc in query:
        if doc.to_dict().get("id") != user_id:
            return False, "That username is already taken by another account."
    db_fs.collection("users").document(str(user_id)).update({"username": new_username})
    return True, "Name updated successfully!"


def get_user_settings(user_id):
    db_fs = get_firestore_client()
    doc = db_fs.collection("user_settings").document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        return {"theme": data.get("theme", "Light"), "language": data.get("language", "English")}
    return {"theme": "Light", "language": "English"}


def save_user_settings(user_id, theme=None, language=None):
    current = get_user_settings(user_id)
    new_theme = theme if theme is not None else current["theme"]
    new_lang = language if language is not None else current["language"]
    db_fs = get_firestore_client()
    db_fs.collection("user_settings").document(str(user_id)).set(
        {"user_id": user_id, "theme": new_theme, "language": new_lang, "updated_at": _now()},
        merge=True,
    )


def get_user_by_username(username):
    clean_name = (username or "").strip()
    if not clean_name:
        return None
    db_fs = get_firestore_client()
    docs = db_fs.collection("users").where(filter=FieldFilter("username", "==", clean_name)).limit(1).get()
    for doc in docs:
        return doc.to_dict()
    all_users = db_fs.collection("users").get()
    for doc in all_users:
        u_dict = doc.to_dict()
        if (u_dict.get("username") or "").strip().lower() == clean_name.lower():
            return u_dict
    return None


def get_user_by_email(email):
    clean_email = (email or "").strip().lower()
    if not clean_email:
        return None
    db_fs = get_firestore_client()
    docs = db_fs.collection("users").where(filter=FieldFilter("email", "==", clean_email)).limit(1).get()
    for doc in docs:
        return doc.to_dict()
    all_users = db_fs.collection("users").get()
    for doc in all_users:
        u_dict = doc.to_dict()
        if (u_dict.get("email") or "").strip().lower() == clean_email:
            return u_dict
    return None



def update_user_password(email, password_hash=None, salt=None):
    """Deprecated: Firebase Authentication is the sole source of truth for passwords."""
    return True


def get_user_by_id(user_id):
    db_fs = get_firestore_client()
    doc = db_fs.collection("users").document(str(user_id)).get()
    if doc.exists:
        u = doc.to_dict()
        return {
            "id": u.get("id"),
            "username": u.get("username"),
            "email": u.get("email"),
            "created_at": u.get("created_at"),
        }
    return None


# ---------- Session operations ----------

DEFAULT_SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))


def create_user_session(user_id, ttl_hours=None):
    """Generates a cryptographically secure 256-bit session token with an enforceable expiration timestamp."""
    token = secrets.token_hex(32)
    now_dt = datetime.now()
    hours = ttl_hours if ttl_hours is not None else DEFAULT_SESSION_TTL_HOURS
    created_at = now_dt.isoformat()
    expires_at = (now_dt + timedelta(hours=hours)).isoformat()
    db_fs = get_firestore_client()
    db_fs.collection("user_sessions").document(token).set(
        {
            "token": token,
            "user_id": user_id,
            "created_at": created_at,
            "expires_at": expires_at,
            "revoked": False,
        }
    )
    return token


def get_user_by_session_token(token):
    """Validates session token: checks existence, revocation status, and expiration.
    Automatically purges expired sessions from the database.
    """
    if not token or not isinstance(token, str) or len(token) < 32:
        return None
    db_fs = get_firestore_client()
    doc = db_fs.collection("user_sessions").document(token).get()
    if not doc.exists:
        return None
    session_data = doc.to_dict() or {}
    if session_data.get("revoked", False):
        return None

    now_str = _now()
    expires_at = session_data.get("expires_at", "")
    if expires_at and expires_at > now_str:
        user_id = session_data.get("user_id")
        return get_user_by_id(user_id)
    else:
        # Expired session cleanup
        try:
            db_fs.collection("user_sessions").document(token).delete()
        except Exception:
            pass
        return None


def delete_user_session(token):
    """Permanently revokes and removes session token."""
    if not token or not isinstance(token, str):
        return
    db_fs = get_firestore_client()
    try:
        db_fs.collection("user_sessions").document(token).delete()
    except Exception:
        pass


def delete_all_user_sessions(user_id):
    """Revokes all active sessions for a user across all devices."""
    if not user_id:
        return
    db_fs = get_firestore_client()
    try:
        docs = db_fs.collection("user_sessions").where(filter=FieldFilter("user_id", "==", user_id)).get()
        for d in docs:
            d.reference.delete()
    except Exception:
        pass


# ---------- Check-in operations ----------

def add_checkin(user_id, mood, emotion_note, stress_level, energy_level, sleep_quality, journal_note):
    db_fs = get_firestore_client()
    checkin_id = _get_next_id(db_fs, "checkins")
    data = {
        "id": checkin_id,
        "user_id": user_id,
        "mood": mood,
        "emotion_note": emotion_note,
        "stress_level": stress_level,
        "energy_level": energy_level,
        "sleep_quality": sleep_quality,
        "journal_note": journal_note,
        "created_at": _now(),
    }
    db_fs.collection("checkins").document(str(checkin_id)).set(data)
    return checkin_id


def get_checkins(user_id, limit=None):
    db_fs = get_firestore_client()
    docs = db_fs.collection("checkins").where(filter=FieldFilter("user_id", "==", user_id)).get()
    items = [doc.to_dict() for doc in docs]
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    if limit:
        items = items[: int(limit)]
    return items


def get_latest_checkin(user_id):
    checkins = get_checkins(user_id, limit=1)
    return checkins[0] if checkins else None


# ---------- Journal operations ----------

def get_journal_entry(entry_id: int):
    """Return a single journal entry dict or None."""
    db_fs = get_firestore_client()
    doc = db_fs.collection("journal_entries").document(str(entry_id)).get()
    if doc.exists:
        return doc.to_dict()
    return None


def add_journal_entry(user_id, title, content, mood="Calm", category="General"):
    db_fs = get_firestore_client()
    journal_id = _get_next_id(db_fs, "journal_entries")
    data = {
        "id": journal_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "mood": mood,
        "category": category,
        "created_at": _now(),
    }
    db_fs.collection("journal_entries").document(str(journal_id)).set(data)
    return journal_id


def get_journal_entries(user_id):
    db_fs = get_firestore_client()
    docs = db_fs.collection("journal_entries").where(filter=FieldFilter("user_id", "==", user_id)).get()
    items = [doc.to_dict() for doc in docs]
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items


def delete_journal_entry(entry_id, user_id):
    db_fs = get_firestore_client()
    doc_ref = db_fs.collection("journal_entries").document(str(entry_id))
    snapshot = doc_ref.get()
    if snapshot.exists and snapshot.to_dict().get("user_id") == user_id:
        doc_ref.delete()
        return True
    return False


# ---------- Legacy chat operations ----------

def add_chat_message(user_id, role, content):
    db_fs = get_firestore_client()
    msg_id = _get_next_id(db_fs, "chat_messages")
    data = {
        "id": msg_id,
        "user_id": user_id,
        "role": role,
        "content": content,
        "created_at": _now(),
    }
    db_fs.collection("chat_messages").document(str(msg_id)).set(data)


def get_chat_messages(user_id, limit=50):
    db_fs = get_firestore_client()
    docs = db_fs.collection("chat_messages").where(filter=FieldFilter("user_id", "==", user_id)).get()
    items = [doc.to_dict() for doc in docs]
    items.sort(key=lambda x: x.get("created_at", ""))
    return items[:limit]


# ---------- Conversation operations ----------

def create_conversation(user_id, title="New Chat"):
    db_fs = get_firestore_client()
    conv_id = _get_next_id(db_fs, "conversations")
    now_str = _now()
    data = {
        "id": conv_id,
        "user_id": user_id,
        "title": title,
        "created_at": now_str,
        "updated_at": now_str,
    }
    db_fs.collection("conversations").document(str(conv_id)).set(data)
    return conv_id


def get_conversations(user_id):
    db_fs = get_firestore_client()
    docs = db_fs.collection("conversations").where(filter=FieldFilter("user_id", "==", user_id)).get()
    items = [doc.to_dict() for doc in docs]
    items.sort(key=lambda x: (x.get("updated_at", ""), x.get("created_at", "")), reverse=True)
    return items


def get_conversation_messages(conversation_id, user_id):
    db_fs = get_firestore_client()
    conv_doc = db_fs.collection("conversations").document(str(conversation_id)).get()
    if not conv_doc.exists or conv_doc.to_dict().get("user_id") != user_id:
        return []
    docs = conv_doc.reference.collection("messages").get()
    items = [doc.to_dict() for doc in docs]
    items.sort(key=lambda x: x.get("created_at", ""))
    return items


def add_conversation_message(conversation_id, user_id, role, content):
    db_fs = get_firestore_client()
    conv_ref = db_fs.collection("conversations").document(str(conversation_id))
    conv_doc = conv_ref.get()
    if not conv_doc.exists or conv_doc.to_dict().get("user_id") != user_id:
        return None
    msg_id = _get_next_id(db_fs, "conversation_messages")
    now_str = _now()
    msg_data = {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": now_str,
    }
    conv_ref.collection("messages").document(str(msg_id)).set(msg_data)
    conv_ref.update({"updated_at": now_str})
    return msg_id


def update_conversation_title(conversation_id, user_id, title):
    db_fs = get_firestore_client()
    conv_ref = db_fs.collection("conversations").document(str(conversation_id))
    conv_doc = conv_ref.get()
    if not conv_doc.exists or conv_doc.to_dict().get("user_id") != user_id:
        return False
    conv_ref.update({"title": title})
    return True


def delete_conversation(conversation_id, user_id):
    db_fs = get_firestore_client()
    conv_ref = db_fs.collection("conversations").document(str(conversation_id))
    conv_doc = conv_ref.get()
    if not conv_doc.exists or conv_doc.to_dict().get("user_id") != user_id:
        return False
    msgs = conv_ref.collection("messages").get()
    for m in msgs:
        m.reference.delete()
    conv_ref.delete()
    return True


def get_latest_conversation(user_id):
    convs = get_conversations(user_id)
    return convs[0] if convs else None

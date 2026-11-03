"""SQLite to Firebase Cloud Firestore Migration Script.
Transfers all users, check-ins, journals, sessions, and chat conversations
from data/wellness.db into Firebase Cloud Firestore while maintaining ID integrity.
"""

import os
import sys
import sqlite3

# Reconfigure stdout/stderr for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "data", "wellness.db")
KEY_PATH = os.path.join(PROJECT_ROOT, "firebase-key.json")

import firebase_admin
from firebase_admin import credentials, firestore


def init_firebase():
    if not os.path.exists(KEY_PATH):
        raise FileNotFoundError(f"Missing {KEY_PATH}! Please ensure your Firebase service account key is saved at {KEY_PATH}.")
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def update_counter(db_fs, counter_name, max_id):
    if max_id is not None and max_id > 0:
        doc_ref = db_fs.collection("counters").document(counter_name)
        existing = doc_ref.get()
        current_val = existing.to_dict().get("last_id", 0) if existing.exists else 0
        if max_id > current_val:
            doc_ref.set({"last_id": max_id}, merge=True)


def migrate():
    print("Starting migration from SQLite to Firebase Firestore...")

    if not os.path.exists(DB_PATH):
        print(f"No local SQLite database found at {DB_PATH}. Ready for clean Firebase setup.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    db_fs = init_firebase()

    # 1. Migrate Users
    users = conn.execute("SELECT * FROM users").fetchall()
    max_user_id = 0
    for u in users:
        u_dict = dict(u)
        user_id = u_dict["id"]
        max_user_id = max(max_user_id, user_id)
        db_fs.collection("users").document(str(user_id)).set(u_dict)
    update_counter(db_fs, "users", max_user_id)
    print(f"Migrated {len(users)} users.")

    # 2. Migrate User Settings
    settings = conn.execute("SELECT * FROM user_settings").fetchall()
    for s in settings:
        s_dict = dict(s)
        user_id = s_dict["user_id"]
        db_fs.collection("user_settings").document(str(user_id)).set(s_dict)
    print(f"Migrated {len(settings)} user settings.")

    # 3. Migrate User Sessions
    sessions = conn.execute("SELECT * FROM user_sessions").fetchall()
    for s in sessions:
        s_dict = dict(s)
        token = s_dict["token"]
        db_fs.collection("user_sessions").document(token).set(s_dict)
    print(f"Migrated {len(sessions)} active user sessions.")

    # 4. Migrate Check-ins
    checkins = conn.execute("SELECT * FROM checkins").fetchall()
    max_checkin_id = 0
    for c in checkins:
        c_dict = dict(c)
        checkin_id = c_dict["id"]
        max_checkin_id = max(max_checkin_id, checkin_id)
        db_fs.collection("checkins").document(str(checkin_id)).set(c_dict)
    update_counter(db_fs, "checkins", max_checkin_id)
    print(f"Migrated {len(checkins)} check-ins.")

    # 5. Migrate Journal Entries
    journals = conn.execute("SELECT * FROM journal_entries").fetchall()
    max_journal_id = 0
    for j in journals:
        j_dict = dict(j)
        entry_id = j_dict["id"]
        max_journal_id = max(max_journal_id, entry_id)
        db_fs.collection("journal_entries").document(str(entry_id)).set(j_dict)
    update_counter(db_fs, "journal_entries", max_journal_id)
    print(f"Migrated {len(journals)} journal entries.")

    # 6. Migrate Legacy Chat Messages
    chats = conn.execute("SELECT * FROM chat_messages").fetchall()
    max_chat_id = 0
    for cm in chats:
        cm_dict = dict(cm)
        msg_id = cm_dict["id"]
        max_chat_id = max(max_chat_id, msg_id)
        db_fs.collection("chat_messages").document(str(msg_id)).set(cm_dict)
    update_counter(db_fs, "chat_messages", max_chat_id)
    print(f"Migrated {len(chats)} legacy chat messages.")

    # 7. Migrate Conversations & Messages
    convs = conn.execute("SELECT * FROM conversations").fetchall()
    max_conv_id = 0
    max_conv_msg_id = 0
    for conv in convs:
        conv_dict = dict(conv)
        conv_id = conv_dict["id"]
        max_conv_id = max(max_conv_id, conv_id)
        db_fs.collection("conversations").document(str(conv_id)).set(conv_dict)

        msgs = conn.execute(
            "SELECT * FROM conversation_messages WHERE conversation_id = ?", (conv_id,)
        ).fetchall()
        for msg in msgs:
            msg_dict = dict(msg)
            msg_id = msg_dict["id"]
            max_conv_msg_id = max(max_conv_msg_id, msg_id)
            db_fs.collection("conversations").document(str(conv_id)).collection("messages").document(str(msg_id)).set(msg_dict)

    update_counter(db_fs, "conversations", max_conv_id)
    update_counter(db_fs, "conversation_messages", max_conv_msg_id)
    print(f"Migrated {len(convs)} chat conversations with all messages.")

    conn.close()
    print("SQLite to Firebase Firestore Migration completed successfully!")


if __name__ == "__main__":
    migrate()

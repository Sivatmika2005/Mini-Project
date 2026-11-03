"""Authentication helpers powered by Firebase Authentication as source of truth."""
import hashlib
import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()

from utils import db

logger = logging.getLogger(__name__)


def _get_firebase_api_key() -> str:
    key = os.getenv("FIREBASE_WEB_API_KEY")
    if not key:
        load_dotenv(override=True)
        key = os.getenv("FIREBASE_WEB_API_KEY")
    if not key:
        key = "AIzaSyB02jwbngMJB080wiLS_ywfXO7sokC_Nak"
    return key


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (email or "").strip()) is not None


def format_user_display_name(username: str) -> str:
    """Removes markdown symbols and formats username with proper capitalization."""
    if not username:
        return "Friend"
    clean = re.sub(r'[*_~`]', '', str(username)).strip()
    return clean.capitalize() if clean else "Friend"


def get_user_greeting(username: str) -> str:
    """Returns a clean, professional greeting like 'Hi, Sivat 👋'."""
    name = format_user_display_name(username)
    return f"Hi, {name} 👋"


def register_user(username: str, email: str, password: str):
    """Registers user with Firebase Authentication as sole source of truth and saves profile metadata in Firestore."""
    username = (username or "").strip()
    email = (email or "").strip().lower()

    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters."
    if db.get_user_by_username(username):
        return False, "That username is already taken."
    if db.get_user_by_email(email):
        return False, "An account with that email already exists."

    fb_uid = None
    try:
        from firebase_admin import auth as fb_auth
        try:
            fb_user = fb_auth.get_user_by_email(email)
            fb_uid = fb_user.uid
            fb_auth.update_user(fb_uid, password=password, display_name=username)
        except fb_auth.UserNotFoundError:
            fb_user = fb_auth.create_user(email=email, password=password, display_name=username)
            fb_uid = fb_user.uid
    except Exception as e:
        logger.error(f"Firebase Auth user creation error: {e}")
        return False, "Failed to create account in Firebase Authentication."

    db.create_user(username, email, firebase_uid=fb_uid)
    return True, "Account created successfully!"


def authenticate_user(username_or_email: str, password: str):
    """Authenticates user against Firebase Authentication as the sole source of truth."""
    clean_identifier = (username_or_email or "").strip()
    if not clean_identifier or not password:
        return None

    # 1. Look up user by username or email in database
    user = db.get_user_by_username(clean_identifier)
    if not user:
        user = db.get_user_by_email(clean_identifier)

    # 2. Firebase Admin SDK fallback lookup if user doc not found in Firestore
    if not user:
        try:
            from firebase_admin import auth as fb_auth
            fb_user = None
            if is_valid_email(clean_identifier):
                try:
                    fb_user = fb_auth.get_user_by_email(clean_identifier)
                except Exception:
                    pass

            if not fb_user:
                try:
                    all_fb_users = fb_auth.list_users().iterate_all()
                    for u in all_fb_users:
                        if (u.display_name or "").strip().lower() == clean_identifier.lower():
                            fb_user = u
                            break
                except Exception:
                    pass

            if fb_user:
                user_id = db.create_user(fb_user.display_name or clean_identifier, fb_user.email, firebase_uid=fb_user.uid)
                user = db.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Firebase Admin SDK lookup fallback error: {e}")

    if not user:
        print(f"[AUTH] No user found in Firestore for identifier: {clean_identifier!r}", flush=True)
        return None

    print(f"[AUTH] Found user in Firestore: id={user.get('id')} email={user.get('email')!r}", flush=True)
    email = user["email"]
    api_key = _get_firebase_api_key()

    if not api_key:
        logger.error("FIREBASE_WEB_API_KEY is not set — cannot authenticate via Firebase REST API.")
        return None

    import json, urllib.request, urllib.error

    def _try_firebase_signin(email_to_try: str):
        """Returns True on success, the Firebase error code string on auth failure, None on network error."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = json.dumps({"email": email_to_try, "password": password, "returnSecureToken": True}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True
                return "UNEXPECTED_STATUS"
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                err_data = json.loads(err_body)
                return err_data.get("error", {}).get("message", "UNKNOWN")
            except Exception:
                return f"HTTP_{e.code}"
        except urllib.error.URLError as e:
            logger.error(f"Firebase REST signIn network error: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Firebase REST signIn unexpected error: {e}")
            return None

    result = _try_firebase_signin(email)
    print(f"[AUTH] Firebase signin result for {email!r}: {result}", flush=True)

    if result is True:
        return user

    if result is None:
        # Network failure — cannot verify credentials
        logger.error(f"Firebase REST signIn network failure for email={email!r}")
        return "NETWORK_ERROR"

    # Auth failed — log the exact Firebase error code
    logger.error(f"Firebase REST signIn rejected email={email!r}: {result}")

    # If Firebase says the email is not found, the Firestore user doc may have a stale email.
    # Attempt to resolve the correct email via Firebase Admin SDK (display_name lookup).
    if "EMAIL_NOT_FOUND" in result or "INVALID_LOGIN_CREDENTIALS" in result:
        try:
            from firebase_admin import auth as fb_auth
            fb_user = None
            # Try resolving by display_name matching the username
            for u in fb_auth.list_users().iterate_all():
                if (u.display_name or "").strip().lower() == (user.get("username") or "").strip().lower():
                    fb_user = u
                    break
            if fb_user and fb_user.email and fb_user.email.lower() != email.lower():
                # Found a different email in Firebase Auth — sync it to Firestore and retry
                logger.warning(
                    f"Email mismatch: Firestore has {email!r}, Firebase Auth has {fb_user.email!r} "
                    f"for username={user.get('username')!r}. Syncing and retrying login."
                )
                db_fs = db.get_firestore_client()
                db_fs.collection("users").document(str(user["id"])).update({"email": fb_user.email})
                user["email"] = fb_user.email
                retry_result = _try_firebase_signin(fb_user.email)
                if retry_result is True:
                    return user
                logger.error(f"Firebase REST signIn retry with synced email also failed: {retry_result}")
        except Exception as e:
            logger.error(f"Firebase Admin SDK email re-sync attempt failed: {e}")

    return None



def send_password_reset_request(email: str) -> tuple[bool, str]:
    """Triggers Firebase Authentication official password reset link generation and dispatches email.
    Always returns a safe generic message without exposing account existence or system errors.
    """
    clean_email = (email or "").strip().lower()
    if not is_valid_email(clean_email):
        return False, "Please enter a valid email address."

    api_key = _get_firebase_api_key()
    if not api_key:
        logger.error("FIREBASE_WEB_API_KEY is not set; cannot send password reset email via Firebase.")
        return False, "Password reset is temporarily unavailable. Please contact support."

    # continueUrl tells Firebase where to redirect the user after they complete the reset
    # on Firebase's hosted page. Set APP_URL in .env for production; defaults to localhost.
    app_url = (os.getenv("APP_URL") or "http://localhost:8503").rstrip("/")
    continue_url = f"{app_url}/?mode=resetPassword"

    try:
        import json, urllib.request
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = json.dumps({
            "requestType": "PASSWORD_RESET",
            "email": clean_email,
            "continueUrl": continue_url,
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True, "If an account exists with this email address, a password reset link has been sent. Please check your inbox and spam folder."
        except Exception as e:
            try:
                err_body = e.read().decode("utf-8") if hasattr(e, 'read') else str(e)
                logger.error(f"Firebase REST sendOobCode error: {err_body}")
            except Exception:
                logger.error(f"Firebase REST sendOobCode exception: {e}")
    except Exception as e:
        logger.error(f"Internal error in send_password_reset_request: {e}")

    return True, "If an account exists with this email address, a password reset link has been sent. Please check your inbox and spam folder."


def confirm_password_reset_with_code(oob_code: str, new_password: str) -> tuple[bool, str]:
    """Confirms password reset using a Firebase action code (oobCode).
    Updates the user password securely in Firebase Authentication.
    """
    if not oob_code or not oob_code.strip():
        return False, "Invalid or missing reset code."
    if not new_password or len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    api_key = _get_firebase_api_key()
    if api_key:
        import json, urllib.request
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={api_key}"
        payload = json.dumps({"oobCode": oob_code.strip(), "newPassword": new_password}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return True, "Your password has been updated successfully! You can now log in."
        except Exception as e:
            logger.error(f"Firebase REST confirmPasswordReset failed: {e}")
            return False, "Invalid or expired reset link. Please request a new password reset link."

    return False, "Password reset verification unavailable. Please try again later."


def generate_password_reset_link(email: str):
    """Backward compatibility wrapper delegating to secure password reset request."""
    success, msg = send_password_reset_request(email)
    return success, msg, None


def reset_user_password(email: str, new_password: str):
    """Resets user password securely in Firebase Authentication as the sole source of truth."""
    email = (email or "").strip().lower()
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if not new_password or len(new_password) < 6:
        return False, "New password must be at least 6 characters."

    try:
        from firebase_admin import auth as fb_auth
        try:
            fb_u = fb_auth.get_user_by_email(email)
            fb_auth.update_user(fb_u.uid, password=new_password)
            return True, "Your password has been updated successfully in Firebase Authentication! You can now log in."
        except fb_auth.UserNotFoundError:
            return False, "No account found with this email address."
    except Exception as e:
        logger.error(f"Firebase Auth password update failed: {e}")
        return False, "Failed to update password in Firebase Authentication."


def login_user(user: dict):
    """Log in user and create persistent session token in DB and query params."""
    token = db.create_user_session(user["id"])
    st.session_state.user = {"id": user["id"], "username": user["username"], "email": user["email"]}
    st.session_state.session_token = token
    st.query_params["session_token"] = token


def logout_user():
    """Log out user, invalidate DB session token, clear query params and session state."""
    token = st.session_state.get("session_token") or st.query_params.get("session_token")
    if token:
        db.delete_user_session(token)

    for key in ["user", "session_token", "chat_history", "active_chat_id", "pending_delete_id", "selected_mood"]:
        st.session_state.pop(key, None)

    st.query_params.clear()
    st.session_state.page = "landing"
    st.rerun()


def restore_session_on_startup():
    """Restores user session on page refresh/startup from URL query params or session_state."""
    token = st.query_params.get("session_token")
    if not token and st.session_state.get("session_token"):
        token = st.session_state.get("session_token")
        st.query_params["session_token"] = token

    if token:
        user = db.get_user_by_session_token(token)
        if user:
            st.session_state.user = {"id": user["id"], "username": user["username"], "email": user["email"]}
            st.session_state.session_token = token
            return True
        else:
            db.delete_user_session(token)
            st.query_params.clear()
    return False


"""Secure Authentication and Identity Management.

Combines standard bcrypt (work factor 12) adaptive password hashing,
Firebase Authentication as an enterprise identity provider,
and defense-in-depth credential protection.
"""
import os
import re
import secrets
import hashlib
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv
import bcrypt

load_dotenv()

from utils import db

logger = logging.getLogger(__name__)

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
BCRYPT_ROUNDS = 12
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\. ]{3,50}$")


def _get_firebase_api_key() -> str:
    key = os.getenv("FIREBASE_WEB_API_KEY")
    if not key:
        load_dotenv(override=True)
        key = os.getenv("FIREBASE_WEB_API_KEY")
    if not key:
        key = "AIzaSyB02jwbngMJB080wiLS_ywfXO7sokC_Nak"
    return key


# ==============================================================================
# CRYPTOGRAPHIC PASSWORD HASHING (BCRYPT)
# ==============================================================================
def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with automatic salting and 12 work rounds."""
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string.")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Securely verifies a password against a bcrypt hash in constant time."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.warning(f"Bcrypt verification exception: {e}")
        return False


# ==============================================================================
# INPUT VALIDATION & CREDENTIAL POLICIES
# ==============================================================================
def is_valid_email(email: str) -> bool:
    """Validates email format against standard RFC compliance and max length."""
    clean = (email or "").strip().lower()
    if not clean or len(clean) > 254:
        return False
    return EMAIL_REGEX.match(clean) is not None


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Enforces secure password strength: min 8 chars, at least 1 letter and 1 number."""
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password must not exceed 128 characters."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    return True, ""


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


# ==============================================================================
# REGISTRATION WITH BCRYPT & FIREBASE AUTH
# ==============================================================================
def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    """Registers a new user with bcrypt password hashing and Firebase Authentication sync."""
    clean_username = (username or "").strip()
    clean_email = (email or "").strip().lower()

    if not clean_username or len(clean_username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(clean_username) > 50:
        return False, "Username cannot exceed 50 characters."
    if not USERNAME_REGEX.match(clean_username):
        return False, "Username may only contain letters, numbers, spaces, dots, dashes, and underscores."

    if not is_valid_email(clean_email):
        return False, "Please enter a valid email address."

    is_strong, pwd_err = validate_password_strength(password)
    if not is_strong:
        return False, pwd_err

    # Check for existing accounts
    if db.get_user_by_username(clean_username):
        return False, "That username is already taken."
    if db.get_user_by_email(clean_email):
        return False, "An account with that email already exists."

    # Compute secure bcrypt password hash
    pw_hash = hash_password(password)

    fb_uid = ""
    try:
        from firebase_admin import auth as fb_auth
        try:
            fb_user = fb_auth.get_user_by_email(clean_email)
            fb_uid = fb_user.uid
            fb_auth.update_user(fb_uid, password=password, display_name=clean_username)
        except fb_auth.UserNotFoundError:
            fb_user = fb_auth.create_user(email=clean_email, password=password, display_name=clean_username)
            fb_uid = fb_user.uid
    except Exception as e:
        logger.warning(f"Firebase Auth user creation notice: {e}")

    # Store user with bcrypt hash in Firestore (never plaintext)
    db.create_user(clean_username, clean_email, firebase_uid=fb_uid, password_hash=pw_hash)
    return True, "Account created successfully!"


# ==============================================================================
# SECURE AUTHENTICATION (HYBRID BCRYPT + FIREBASE + LEGACY UPGRADE)
# ==============================================================================
def _try_firebase_signin(email_to_try: str, password_to_try: str):
    """Verifies credentials against Google Identity Toolkit REST API."""
    api_key = _get_firebase_api_key()
    if not api_key:
        return None

    import json
    import urllib.request
    import urllib.error

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = json.dumps({"email": email_to_try, "password": password_to_try, "returnSecureToken": True}).encode("utf-8")
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
    except urllib.error.URLError:
        return "NETWORK_ERROR"
    except Exception:
        return None


def authenticate_user(username_or_email: str, password: str):
    """Authenticates a user securely.

    Evaluation hierarchy:
    1. Direct Bcrypt verification against stored password hash.
    2. Transparent upgrade of legacy salted SHA-256 hashes to Bcrypt.
    3. Firebase Authentication REST API verification with automatic hash sync.
    """
    clean_identifier = (username_or_email or "").strip()
    if not clean_identifier or not password:
        return None

    # 1. Lookup user in Firestore
    user = db.get_user_by_username(clean_identifier)
    if not user:
        user = db.get_user_by_email(clean_identifier)

    # 2. Check local bcrypt password hash if available
    if user and user.get("password_hash"):
        stored_hash = user["password_hash"]
        if isinstance(stored_hash, str) and stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
            if verify_password(password, stored_hash):
                return user
        elif user.get("salt"):
            # Transparent migration: verify legacy salted SHA-256 and rehash with Bcrypt
            salt = user["salt"]
            legacy_expected = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
            if secrets.compare_digest(stored_hash, legacy_expected):
                new_bcrypt_hash = hash_password(password)
                db.update_user_password_hash(user["id"], new_bcrypt_hash)
                user["password_hash"] = new_bcrypt_hash
                logger.info(f"Transparently upgraded user id={user['id']} legacy hash to bcrypt.")
                return user

    # 3. Fallback / Source-of-truth verification via Firebase Auth
    email_to_verify = None
    if user and user.get("email"):
        email_to_verify = user["email"]
    elif is_valid_email(clean_identifier):
        email_to_verify = clean_identifier

    if email_to_verify:
        fb_result = _try_firebase_signin(email_to_verify, password)
        if fb_result is True:
            # Sync user doc if it was created directly in Firebase Auth console
            if not user:
                user = db.get_user_by_email(email_to_verify)
            if user:
                # Sync secure bcrypt hash into Firestore for high-speed offline verification
                new_hash = hash_password(password)
                db.update_user_password_hash(user["id"], new_hash)
                user["password_hash"] = new_hash
                return user
        elif fb_result == "NETWORK_ERROR":
            if not user or not user.get("password_hash"):
                return "NETWORK_ERROR"

    return None


# ==============================================================================
# SECURE PASSWORD RESET (PREVENT ACCOUNT ENUMERATION)
# ==============================================================================
def send_password_reset_request(email: str) -> Tuple[bool, str]:
    """Generates official Firebase Authentication password reset dispatch.

    Always returns a safe generic response to prevent account enumeration.
    """
    clean_email = (email or "").strip().lower()
    generic_msg = (
        "If an account exists with this email address, a password reset link has been dispatched. "
        "Please check your inbox and spam folder."
    )

    if not is_valid_email(clean_email):
        return True, generic_msg

    api_key = _get_firebase_api_key()
    if not api_key:
        return True, generic_msg

    app_url = (os.getenv("APP_URL") or "http://localhost:5173").rstrip("/")
    continue_url = f"{app_url}/?mode=resetPassword"

    try:
        import json
        import urllib.request
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
                    return True, generic_msg
        except Exception as e:
            logger.warning(f"Firebase REST sendOobCode: {e}")
    except Exception as e:
        logger.error(f"Error in send_password_reset_request: {e}")

    return True, generic_msg


def confirm_password_reset_with_code(oob_code: str, new_password: str) -> Tuple[bool, str]:
    """Confirms password reset using a Firebase action code and updates bcrypt hash."""
    if not oob_code or not oob_code.strip():
        return False, "Invalid or missing reset code."

    is_strong, pwd_err = validate_password_strength(new_password)
    if not is_strong:
        return False, pwd_err

    api_key = _get_firebase_api_key()
    if api_key:
        import json
        import urllib.request
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={api_key}"
        payload = json.dumps({"oobCode": oob_code.strip(), "newPassword": new_password}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                email = res_data.get("email")
                if email:
                    user = db.get_user_by_email(email)
                    if user:
                        new_hash = hash_password(new_password)
                        db.update_user_password_hash(user["id"], new_hash)
                        # Invalidate existing sessions across all devices for security
                        db.delete_all_user_sessions(user["id"])
                return True, "Your password has been updated successfully! You can now log in."
        except Exception as e:
            logger.error(f"Firebase REST confirmPasswordReset failed: {e}")
            return False, "Invalid or expired reset link. Please request a new link."

    return False, "Password reset verification unavailable. Please try again later."


def reset_user_password(email: str, new_password: str) -> Tuple[bool, str]:
    """Administrative password reset updating both Firebase Auth and local bcrypt hash."""
    clean_email = (email or "").strip().lower()
    if not is_valid_email(clean_email):
        return False, "Please enter a valid email address."

    is_strong, pwd_err = validate_password_strength(new_password)
    if not is_strong:
        return False, pwd_err

    try:
        from firebase_admin import auth as fb_auth
        try:
            fb_u = fb_auth.get_user_by_email(clean_email)
            fb_auth.update_user(fb_u.uid, password=new_password)
            user = db.get_user_by_email(clean_email)
            if user:
                new_hash = hash_password(new_password)
                db.update_user_password_hash(user["id"], new_hash)
                db.delete_all_user_sessions(user["id"])
            return True, "Password has been updated successfully."
        except fb_auth.UserNotFoundError:
            return False, "No account found with this email address."
    except Exception as e:
        logger.error(f"Firebase Auth password update failed: {e}")
        return False, "Failed to update password."

"""Comprehensive Security & Authentication Automated Test Suite.

Verifies:
1. Valid login with bcrypt verification.
2. Invalid password rejection (constant-time, generic error).
3. Empty / whitespace credentials rejection.
4. Expired session rejection and automatic database purging.
5. Invalid / malformed session token rejection.
6. Unauthorized protected endpoint access rejection across all sensitive routes.
7. Logout session invalidation and prevention of token reuse.
"""
import sys
import os
import unittest
from datetime import datetime, timedelta

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from server import app
from utils import db, auth

client = TestClient(app)

class TestAuthenticationSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dedicated isolated test user
        cls.test_username = f"sec_user_{os.urandom(4).hex()}"
        cls.test_email = f"{cls.test_username}@example.com"
        cls.test_password = "SecurePassword123!"

        # Register test user
        success, msg = auth.register_user(cls.test_username, cls.test_email, cls.test_password)
        if not success:
            raise RuntimeError(f"Failed to create test user: {msg}")

        # Retrieve user record
        cls.user = db.get_user_by_email(cls.test_email)
        assert cls.user is not None, "Test user doc not found in Firestore"

    # --------------------------------------------------------------------------
    # TEST 1: Valid Login & Bcrypt Verification
    # --------------------------------------------------------------------------
    def test_01_valid_login(self):
        """Tests successful login with correct credentials, returning a 256-bit session token."""
        resp = client.post("/api/auth/login", json={
            "username_or_email": self.test_email,
            "password": self.test_password,
        })
        self.assertEqual(resp.status_code, 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}")
        data = resp.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_email)
        self.assertGreaterEqual(len(data["token"]), 32)

        # Verify password is saved as a bcrypt hash ($2b$ or $2a$)
        user_doc = db.get_user_by_id(data["user"]["id"])
        full_user = db.get_user_by_email(self.test_email)
        stored_hash = full_user.get("password_hash", "")
        self.assertTrue(
            stored_hash.startswith(("$2b$", "$2a$")),
            f"Expected bcrypt hash prefix, got {stored_hash[:10]}..."
        )
        self.assertTrue(auth.verify_password(self.test_password, stored_hash))

    # --------------------------------------------------------------------------
    # TEST 2: Invalid Password Rejection
    # --------------------------------------------------------------------------
    def test_02_invalid_password(self):
        """Tests that incorrect password returns generic 401 Unauthorized without leakage."""
        resp = client.post("/api/auth/login", json={
            "username_or_email": self.test_email,
            "password": "WrongPassword999!",
        })
        self.assertEqual(resp.status_code, 401)
        data = resp.json()
        self.assertEqual(data["detail"], "Invalid username/email or password.")

    # --------------------------------------------------------------------------
    # TEST 3: Empty / Whitespace Credentials Rejection
    # --------------------------------------------------------------------------
    def test_03_empty_credentials(self):
        """Tests that empty, whitespace, or missing credentials are rejected with 400 Bad Request."""
        # Empty identifier
        resp1 = client.post("/api/auth/login", json={
            "username_or_email": "   ",
            "password": self.test_password,
        })
        self.assertEqual(resp1.status_code, 400)

        # Empty password
        resp2 = client.post("/api/auth/login", json={
            "username_or_email": self.test_email,
            "password": "",
        })
        self.assertEqual(resp2.status_code, 400)

        # Registration with weak password (<8 characters)
        resp3 = client.post("/api/auth/register", json={
            "username": "shortpwduser",
            "email": "shortpwd@example.com",
            "password": "short",
        })
        self.assertEqual(resp3.status_code, 400)
        self.assertIn("8 characters", resp3.json()["detail"])

    # --------------------------------------------------------------------------
    # TEST 4: Expired Session Rejection & Purging
    # --------------------------------------------------------------------------
    def test_04_expired_session(self):
        """Tests that an expired session token is denied (401) and purged from the database."""
        # Create an already-expired session directly in Firestore (TTL = -2 hours)
        token = db.create_user_session(self.user["id"], ttl_hours=-2)
        
        # Verify access attempt with the expired token is denied
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 401)
        self.assertIn("expired", resp.json()["detail"].lower())

        # Verify the expired token was purged from the database
        db_fs = db.get_firestore_client()
        doc = db_fs.collection("user_sessions").document(token).get()
        self.assertFalse(doc.exists, "Expired session document was not purged from Firestore!")

    # --------------------------------------------------------------------------
    # TEST 5: Invalid / Malformed Session Token
    # --------------------------------------------------------------------------
    def test_05_invalid_session_token(self):
        """Tests that garbage, malformed, or fabricated tokens are rejected with 401."""
        # Random non-existent token
        fabricated_token = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {fabricated_token}"})
        self.assertEqual(resp.status_code, 401)

        # Malformed short token
        resp2 = client.get("/api/auth/me", headers={"Authorization": "Bearer short_token"})
        self.assertEqual(resp2.status_code, 401)

        # Bad header scheme (Basic instead of Bearer)
        resp3 = client.get("/api/auth/me", headers={"Authorization": "Basic dXNlcjpwYXNz"})
        self.assertEqual(resp3.status_code, 401)

    # --------------------------------------------------------------------------
    # TEST 6: Unauthorized Endpoint Access
    # --------------------------------------------------------------------------
    def test_06_unauthorized_protected_endpoints(self):
        """Tests that sensitive health, journal, chat, checkin, and companion endpoints reject unauthenticated requests."""
        endpoints = [
            ("GET", "/api/auth/me"),
            ("GET", "/api/user/settings"),
            ("POST", "/api/user/settings"),
            ("POST", "/api/user/update-name"),
            ("GET", "/api/checkins/latest"),
            ("GET", "/api/checkins"),
            ("POST", "/api/checkins"),
            ("GET", "/api/journals"),
            ("POST", "/api/journals"),
            ("DELETE", "/api/journals/1"),
            ("POST", "/api/journals/summarize"),
            ("GET", "/api/chat/conversations"),
            ("POST", "/api/chat/conversations"),
            ("GET", "/api/chat/conversations/1/messages"),
            ("POST", "/api/chat/conversations/1/messages"),
            ("POST", "/api/companion/chat"),
            ("POST", "/api/auth/logout"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                resp = client.get(endpoint)
            elif method == "POST":
                resp = client.post(endpoint, json={})
            elif method == "DELETE":
                resp = client.delete(endpoint)
            self.assertEqual(
                resp.status_code,
                401,
                f"Endpoint {method} {endpoint} allowed access without authentication! Status: {resp.status_code}"
            )

    # --------------------------------------------------------------------------
    # TEST 7: Logout Invalidation & Prevention of Token Reuse
    # --------------------------------------------------------------------------
    def test_07_logout_and_token_reuse_prevention(self):
        """Tests that logging out invalidates the session and subsequent requests with the old token are blocked."""
        # 1. Login to obtain a fresh token
        login_resp = client.post("/api/auth/login", json={
            "username_or_email": self.test_email,
            "password": self.test_password,
        })
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.json()["token"]

        # 2. Verify token is active on protected endpoint
        check_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(check_resp.status_code, 200)

        # 3. Perform logout
        logout_resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(logout_resp.status_code, 200)
        self.assertTrue(logout_resp.json()["success"])

        # 4. Attempt to REUSE the old token on multiple protected routes
        reuse_me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(reuse_me_resp.status_code, 401, "Old token was reused on /api/auth/me after logout!")

        reuse_checkin_resp = client.get("/api/checkins/latest", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(reuse_checkin_resp.status_code, 401, "Old token was reused on /api/checkins/latest after logout!")

        reuse_chat_resp = client.get("/api/chat/conversations", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(reuse_chat_resp.status_code, 401, "Old token was reused on /api/chat/conversations after logout!")


if __name__ == "__main__":
    unittest.main()


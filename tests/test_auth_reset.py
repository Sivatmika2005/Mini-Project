"""Unit tests for secure Firebase Authentication password reset flow."""
import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils import auth


class TestAuthPasswordReset(unittest.TestCase):
    def test_email_validation(self):
        self.assertTrue(auth.is_valid_email("user@example.com"))
        self.assertTrue(auth.is_valid_email("sivat.mika@domain.co.in"))
        self.assertFalse(auth.is_valid_email("invalid-email"))
        self.assertFalse(auth.is_valid_email("user@"))
        self.assertFalse(auth.is_valid_email(""))
        self.assertFalse(auth.is_valid_email(None))

    def test_send_password_reset_invalid_email(self):
        success, msg = auth.send_password_reset_request("bademail")
        self.assertFalse(success)
        self.assertEqual(msg, "Please enter a valid email address.")

    def test_send_password_reset_valid_email_privacy(self):
        # Must return uniform generic success message without leaking existence or system errors
        success, msg = auth.send_password_reset_request("random_nonexistent_user_12345@example.com")
        self.assertTrue(success)
        self.assertIn("If an account exists with this email address", msg)

    def test_confirm_password_reset_short_password(self):
        success, msg = auth.confirm_password_reset_with_code("fake_code", "123")
        self.assertFalse(success)
        self.assertEqual(msg, "Password must be at least 6 characters.")

    def test_confirm_password_reset_invalid_code(self):
        success, msg = auth.confirm_password_reset_with_code("invalid_oob_code", "NewSecretPassword123")
        self.assertFalse(success)
        self.assertTrue("Invalid or expired" in msg or "unavailable" in msg)

    def test_reset_user_password_validation(self):
        success, msg = auth.reset_user_password("invalid_email", "newpass123")
        self.assertFalse(success)
        self.assertEqual(msg, "Please enter a valid email address.")

        success, msg = auth.reset_user_password("user@example.com", "123")
        self.assertFalse(success)
        self.assertEqual(msg, "New password must be at least 6 characters.")


if __name__ == "__main__":
    unittest.main()

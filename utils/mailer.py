"""Mailer module for sending email notifications and password reset links via SMTP."""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_link: str = "") -> tuple[bool, str]:
    """Sends a password reset email to the recipient via SMTP if configured.
    Falls back gracefully if SMTP credentials are not present in .env.
    """
    to_email = (to_email or "").strip()
    if not to_email:
        return False, "Target email address is required."

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    sender_email = os.getenv("SENDER_EMAIL", smtp_username or "noreply@mentalwellness.app")

    if smtp_username and smtp_password:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Reset Your Password - AI Mental Wellness Companion"
            msg["From"] = f"AI Mental Wellness <{sender_email}>"
            msg["To"] = to_email

            text_content = f"""Hello,

You requested a password reset for your AI Mental Wellness Companion account.

Please use the following link to reset your password:
{reset_link}

If you did not request this, please ignore this email.

Best regards,
AI Mental Wellness Team
"""
            html_content = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 12px;">
                <h2 style="color: #4F46E5; margin-bottom: 16px;">Reset Your Password 🔑</h2>
                <p>Hello,</p>
                <p>We received a request to reset your password for your <strong>AI Mental Wellness Companion</strong> account.</p>
                <div style="margin: 24px 0;">
                    <a href="{reset_link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Reset Password →</a>
                </div>
                <p style="font-size: 0.85rem; color: #666;">Or copy and paste this link in your browser:</p>
                <p style="font-size: 0.85rem; word-break: break-all; color: #4F46E5;">{reset_link}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
                <p style="font-size: 0.8rem; color: #888;">If you did not request this password reset, please ignore this email.</p>
            </div>
            """

            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, [to_email], msg.as_string())

            logger.info(f"Password reset email successfully sent via SMTP to {to_email}")
            return True, f"Password reset email sent to {to_email}. Please check your inbox and spam folder."
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False, f"Failed to send email via SMTP: {e}"

    logger.info(f"SMTP not configured. Password reset link generated for {to_email}: {reset_link}")
    return True, "Password reset link generated. Check email or Firebase settings."

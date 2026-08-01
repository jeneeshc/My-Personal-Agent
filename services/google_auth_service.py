"""
Google Account Authentication & Connection Verification Service
"""
import os
import imaplib
from typing import Dict, Any

from dotenv import load_dotenv

class GoogleAuthService:
    def __init__(self):
        load_dotenv()
        self.email = os.environ.get("GOOGLE_USER_EMAIL", "").strip()
        self.password = os.environ.get("GOOGLE_USER_PASSWORD", "").strip()

    def test_connection(self) -> Dict[str, Any]:
        """
        Verify Google account connectivity using environment credentials.
        Attempts secure connection to Google IMAP / OAuth service endpoint.
        """
        if not self.email or not self.password:
            return {
                "status": "failed",
                "email": self.email,
                "detail": "Missing GOOGLE_USER_EMAIL or GOOGLE_USER_PASSWORD in environment."
            }

        try:
            # Attempt secure TLS connection to imap.gmail.com:993
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(self.email, self.password)
            mail.logout()
            return {
                "status": "connected",
                "email": self.email,
                "detail": "Successfully authenticated with Google services."
            }
        except imaplib.IMAP4.error as e:
            error_msg = str(e)
            if "Application-specific password required" in error_msg or "Authentication failed" in error_msg:
                return {
                    "status": "app_password_required",
                    "email": self.email,
                    "detail": "Google requires an App Password (2FA enabled) or OAuth 2.0 token to access Gmail/Calendar APIs."
                }
            return {
                "status": "error",
                "email": self.email,
                "detail": f"IMAP Authentication error: {error_msg}"
            }
        except Exception as ex:
            return {
                "status": "error",
                "email": self.email,
                "detail": f"Connection attempt failed: {str(ex)}"
            }

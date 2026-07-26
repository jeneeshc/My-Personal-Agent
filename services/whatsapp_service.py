"""
WhatsApp Service Implementation for outbound API message dispatching
"""
import os
import httpx
from typing import Optional

class WhatsAppService:
    def __init__(self):
        self.api_url = os.environ.get("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0/").strip()
        self.phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "test_id").strip()
        self.access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "test_token").strip()
        
    async def send_message(self, recipient_id: str, text: str) -> bool:
        """
        Send text message back to WhatsApp user via Graph API.
        """
        url = f"{self.api_url}{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": text}
        }

        if self.access_token != "test_token":
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                    if response.status_code != 200:
                        print(f"[WhatsApp API Error]: HTTP {response.status_code} - {response.text}")
                    return response.status_code == 200
            except Exception as e:
                print(f"[WhatsApp API Error]: {e}")
                return False

        print(f"[WhatsApp Mock Dispatch] To {recipient_id}: {text}")
        return True

import os
import httpx

class WhatsAppService:
    def __init__(self):
        self.api_url = os.environ.get("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0/")
        self.phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "test_id")
        self.access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "test_token")
        
    async def send_message(self, recipient_id: str, text: str) -> bool:
        """
        Send a text message back to the user via WhatsApp API.
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
        
        # In a real scenario, uncomment the HTTP call:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(url, headers=headers, json=payload)
        #     return response.status_code == 200
        
        print(f"[Mock] Sent message to {recipient_id}: {text}")
        return True

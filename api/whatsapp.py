from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])

@router.get("/")
async def verify_webhook(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    # This endpoint is used by WhatsApp to verify the webhook
    # In a real app, verify the token against your environment variable
    if hub_mode == "subscribe" and hub_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/")
async def receive_message(request: Request) -> Dict[str, Any]:
    # Receives incoming WhatsApp messages
    payload = await request.json()
    
    # Simple extraction logic for the incoming message
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            messages = value.get("messages", [])
            for message in messages:
                sender_id = message.get("from")
                text_content = message.get("text", {}).get("body", "")
                
                # Here we would invoke the Secretary Agent
                print(f"Received message from {sender_id}: {text_content}")
                
        return {"status": "success"}
    except (IndexError, KeyError) as e:
        # Invalid payload structure
        print(f"Error parsing payload: {e}")
        return {"status": "ignored"}

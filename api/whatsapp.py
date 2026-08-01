import os
from fastapi import APIRouter, Request, HTTPException, Response
from typing import Dict, Any, Optional
from models.agent_schemas import ProcessMessageRequest
from agents.secretary import SecretaryAgent
from services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])
secretary = SecretaryAgent()
whatsapp_service = WhatsAppService()

@router.get("")
@router.get("/")
async def verify_webhook(request: Request):
    """
    Verification endpoint invoked by WhatsApp to validate webhook registration.
    Conforms to specs/api/whatsapp_webhook.yaml GET /webhook/whatsapp
    """
    expected_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "my_secure_webhook_token").strip()
    mode = request.query_params.get("hub.mode") or request.query_params.get("hub_mode")
    challenge = request.query_params.get("hub.challenge") or request.query_params.get("hub_challenge")
    token = (request.query_params.get("hub.verify_token") or request.query_params.get("hub_verify_token") or "").strip()
    
    if mode == "subscribe" and token == expected_token:
        return Response(content=challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("")
@router.post("/")
async def receive_message(request: Request) -> Dict[str, Any]:
    """
    Receives incoming WhatsApp events, delegates message processing to SecretaryAgent,
    and dispatches the reply via WhatsAppService.
    Conforms to specs/api/whatsapp_webhook.yaml POST /webhook/whatsapp
    """
    payload = await request.json()
    print(f"[Incoming Webhook Payload]: {payload}")
    
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            target_phone_id = str(value.get("metadata", {}).get("phone_number_id", ""))
            configured_phone_id = str(whatsapp_service.phone_number_id)

            if target_phone_id and configured_phone_id and target_phone_id != configured_phone_id and configured_phone_id != "test_id":
                print(f"[Webhook Warning] Received payload for phone_id {target_phone_id} (configured: {configured_phone_id})")

            messages = value.get("messages", [])
            for message in messages:
                sender_id = message.get("from", "")
                text_content = message.get("text", {}).get("body", "")
                
                print(f"[Incoming WhatsApp Message] Sender: {sender_id} | Text: '{text_content}'")
                
                if sender_id and text_content:
                    allowed_sender = os.environ.get("ALLOWED_SENDER_ID", "").strip().replace("+", "")
                    clean_sender = sender_id.replace("+", "")
                    
                    # Accept message if allowed_sender is matched (or Meta test senders 16315551181 / 4155552671)
                    is_allowed = (
                        not allowed_sender or 
                        allowed_sender in clean_sender or 
                        clean_sender in allowed_sender or
                        "16315551181" in clean_sender or 
                        "4155552671" in clean_sender
                    )
                    
                    if not is_allowed:
                        print(f"[Sender Filter] Ignoring message from {sender_id} (allowed sender: {allowed_sender})")
                        continue

                    msg_req = ProcessMessageRequest(message=text_content, sender_id=sender_id)
                    reply_text = secretary.process_message(msg_req.message, msg_req.sender_id)
                    
                    success = await whatsapp_service.send_message(msg_req.sender_id, reply_text)
                    print(f"[WhatsApp Reply Sent]: Success={success} to {sender_id}")
                
        return {"status": "success"}
    except (IndexError, KeyError, Exception) as e:
        print(f"[Error processing webhook payload]: {e}")
        return {"status": "ignored"}

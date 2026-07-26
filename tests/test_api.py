import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_whatsapp_end_to_end_tech_news():
    """Test end-to-end WhatsApp message payload for tech news request."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "+14155552671",
                                    "id": "wamid.1001",
                                    "timestamp": "1670000000",
                                    "type": "text",
                                    "text": {"body": "Tell me latest tech news"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_whatsapp_end_to_end_receipt_extract():
    """Test end-to-end WhatsApp message payload for receipt extraction."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "+14155552671",
                                    "id": "wamid.1002",
                                    "timestamp": "1670000000",
                                    "type": "text",
                                    "text": {"body": "Paid $45.00 at Walmart"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_whatsapp_end_to_end_greeting(capsys, monkeypatch):
    """Test end-to-end WhatsApp message payload for a simple greeting to see the agent response."""
    from api import whatsapp
    monkeypatch.setattr(whatsapp.whatsapp_service, "access_token", "test_token")
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "+14155552671",
                                    "id": "wamid.1005",
                                    "timestamp": "1670000000",
                                    "type": "text",
                                    "text": {"body": "Hello, how are you?"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    # Capture the print output from the WhatsApp mock dispatch
    captured = capsys.readouterr()
    assert "[WhatsApp Mock Dispatch] To +14155552671:" in captured.out


def test_whatsapp_end_to_end_calendar_schedule():
    """Test end-to-end WhatsApp message payload for calendar event scheduling."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "+14155552671",
                                    "id": "wamid.1003",
                                    "timestamp": "1670000000",
                                    "type": "text",
                                    "text": {"body": "Schedule meeting with team tomorrow at 3pm"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_whatsapp_webhook_handles_worker_crash(monkeypatch):
    """Test WhatsApp webhook endpoint returns 200 success without crashing when worker fails 5 consecutive times."""
    from api import whatsapp

    class CrashingWorker:
        def execute_task(self, payload):
            raise RuntimeError("Fatal process crash")

    whatsapp.secretary.process_manager.register_agent("NewsCollector", lambda: CrashingWorker())

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "+14155552671",
                                    "id": "wamid.1004",
                                    "timestamp": "1670000000",
                                    "type": "text",
                                    "text": {"body": "Give me news"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    state = whatsapp.secretary.process_manager.get_process_state("NewsCollector")
    assert state.status == "FAILED_MAX_RETRIES"
    assert state.consecutive_crashes == 5



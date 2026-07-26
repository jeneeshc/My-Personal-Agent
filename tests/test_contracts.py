import pytest
import os
import yaml
from fastapi.testclient import TestClient
from main import app
from models.agent_schemas import (
    ProcessMessageRequest,
    IntentClassification,
    AgentDelegationPayload,
    AgentResponseSynthesis,
    UserProfile,
    ScheduledTaskConfig,
    ExpenseRecord,
    ScheduleEventRequest,
    RegionalNewsRequest,
    TechNewsRequest,
    NewsRequest,
    EmailSummaryRequest,
    DraftReplyRequest,
    StockPriceRequest,
    ExtractReceiptRequest,
    LogWorkoutRequest,
    GroceryItemRequest,
    SearchDriveRequest,
    AgentProcessState
)


client = TestClient(app)

def test_specs_files_exist_and_valid_yaml():
    """Verify that all required spec files exist in specs/ and are valid YAML."""
    spec_files = [
        "specs/api/whatsapp_webhook.yaml",
        "specs/api/internal_cron.yaml",
        "specs/agents/secretary_protocol.yaml",
        "specs/agents/worker_tools.yaml",
        "specs/domain/domain_models.yaml"
    ]
    for spec_path in spec_files:
        assert os.path.exists(spec_path), f"Spec file missing: {spec_path}"
        with open(spec_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            assert content is not None, f"Spec file is empty or invalid YAML: {spec_path}"

def test_process_message_request_model():
    """Test ProcessMessageRequest model validation."""
    req = ProcessMessageRequest(message="Hello Secretary", sender_id="123456789")
    assert req.message == "Hello Secretary"
    assert req.sender_id == "123456789"

def test_intent_classification_model():
    """Test IntentClassification model validation against spec constraints."""
    intent = IntentClassification(
        primary_intent="money_manager",
        target_agent="MoneyManager",
        confidence=0.95
    )
    assert intent.primary_intent == "money_manager"
    assert intent.target_agent == "MoneyManager"
    assert intent.confidence == 0.95

def test_agent_delegation_payload():
    """Test AgentDelegationPayload model validation."""
    payload = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_123",
        action="extract_receipt",
        payload={"text_content": "Paid $50 at Store"}
    )
    assert payload.target_agent == "MoneyManager"
    assert payload.delegation_id is not None

def test_whatsapp_webhook_get_verify(monkeypatch):
    """Test GET /webhook/whatsapp verification according to OpenAPI spec."""
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "test")
    response = client.get("/webhook/whatsapp?hub.mode=subscribe&hub.challenge=123456&hub.verify_token=test")
    assert response.status_code == 200
    assert response.text == '"123456"' or response.text == '123456'

def test_whatsapp_webhook_post_receive():
    """Test POST /webhook/whatsapp message receiving according to OpenAPI spec."""
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
                                    "id": "wamid.HBgL",
                                    "timestamp": "1670000000",
                                    "type": "text",
                                    "text": {"body": "Check my stocks"}
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

def test_news_agent_tool_contracts():
    """Test RegionalNewsRequest and TechNewsRequest models against contract requirements."""
    regional = RegionalNewsRequest(region="San Francisco, CA")
    assert regional.region == "San Francisco, CA"
    assert "local" in regional.categories
    assert regional.max_results == 5

    tech = TechNewsRequest(technologies=["AI/ML", "Python"])
    assert "AI/ML" in tech.technologies
    assert tech.timeframe == "last_24_hours"
    assert tech.max_results == 5

def test_agent_process_state_contract():
    """Test AgentProcessState model validation against secretary_protocol.yaml schema."""
    state = AgentProcessState(
        agent_name="NewsCollector",
        status="HEALTHY",
        consecutive_crashes=0,
        max_consecutive_crashes=5
    )
    assert state.agent_name == "NewsCollector"
    assert state.status == "HEALTHY"
    assert state.consecutive_crashes == 0
    assert state.max_consecutive_crashes == 5



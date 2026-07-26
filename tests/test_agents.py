import pytest
from agents.secretary import SecretaryAgent
from agents.news_collector import NewsCollectorAgent
from agents.money_manager import MoneyManagerAgent
from agents.task_travel_manager import TaskTravelManagerAgent
from models.agent_schemas import (
    ProcessMessageRequest,
    RegionalNewsRequest,
    TechNewsRequest,
    ExtractReceiptRequest,
    ScheduleEventRequest,
    SuggestItineraryRequest,
    SearchFlightsRequest,
    AgentDelegationPayload
)

def test_secretary_intent_classification():
    """Test Secretary intent classifier routing accuracy."""
    secretary = SecretaryAgent()

    calendar_intent = secretary.classify_intent("Schedule meeting tomorrow at 3 PM")
    assert calendar_intent.target_agent == "TaskTravelManager"

    tech_intent = secretary.classify_intent("Give me the latest tech articles")
    assert tech_intent.target_agent == "NewsCollector"

    regional_intent = secretary.classify_intent("Show me local regional news")
    assert regional_intent.target_agent == "NewsCollector"

    money_intent = secretary.classify_intent("Paid $45.00 at Starbucks receipt")
    assert money_intent.target_agent == "MoneyManager"

def test_task_travel_manager_tools():
    """Test TaskTravelManager tool capabilities (schedule, itinerary, flights)."""
    agent = TaskTravelManagerAgent()

    # Schedule event tool
    sched_payload = AgentDelegationPayload(
        target_agent="TaskTravelManager",
        user_id="user_123",
        action="schedule_event",
        payload={
            "title": "Design Review",
            "start_time": "2026-07-26T10:00:00Z",
            "end_time": "2026-07-26T11:00:00Z",
            "location": "Conference Room A"
        }
    )
    synthesis = agent.execute_task(sched_payload)
    assert synthesis.success is True
    assert "Design Review" in synthesis.final_reply_text

    # Suggest itinerary tool
    itin_payload = AgentDelegationPayload(
        target_agent="TaskTravelManager",
        user_id="user_123",
        action="suggest_itinerary",
        payload={"destination": "Tokyo", "days": 3}
    )
    itin_synth = agent.execute_task(itin_payload)
    assert itin_synth.success is True
    assert "Tokyo" in itin_synth.final_reply_text

    # Search flights tool
    flight_payload = AgentDelegationPayload(
        target_agent="TaskTravelManager",
        user_id="user_123",
        action="search_flights",
        payload={"origin": "SFO", "destination": "HND", "departure_date": "2026-09-01"}
    )
    flight_synth = agent.execute_task(flight_payload)
    assert flight_synth.success is True
    assert "Flights from SFO to HND" in flight_synth.final_reply_text

def test_news_collector_regional_and_tech_tools():
    """Test NewsCollector tool capabilities."""
    collector = NewsCollectorAgent()

    reg_req = RegionalNewsRequest(region="San Francisco")
    reg_articles = collector.get_regional_news(reg_req)
    assert len(reg_articles) > 0
    assert "San Francisco" in reg_articles[0]["title"]

    tech_req = TechNewsRequest(technologies=["AI/ML", "Python"])
    tech_articles = collector.get_tech_news(tech_req)
    assert len(tech_articles) > 0
    assert "AI" in tech_articles[0]["title"] or "Tech" in tech_articles[0]["title"]

from agents.base_worker import BaseWorkerAgent
from agents.process_manager import AgentProcessManager
from models.agent_schemas import AgentResponseSynthesis

class CrashingWorkerAgent(BaseWorkerAgent):
    def __init__(self, fail_count: int = 999, shared_tracker: dict = None):
        super().__init__("CrashingWorker")
        self.fail_count = fail_count
        self.tracker = shared_tracker if shared_tracker is not None else {"calls": 0}

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        self.tracker["calls"] += 1
        if self.tracker["calls"] <= self.fail_count:
            raise RuntimeError(f"Simulated crash execution #{self.tracker['calls']}")
        return AgentResponseSynthesis(
            delegation_id=payload.delegation_id,
            success=True,
            final_reply_text="Recovered from crash successfully"
        )



def test_money_manager_receipt_extraction():
    """Test MoneyManager receipt extraction logic."""
    money_agent = MoneyManagerAgent()
    payload = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_123",
        action="extract_receipt",
        payload={"text_content": "Paid $12.50 at Target"}
    )
    synthesis = money_agent.execute_task(payload)
    assert synthesis.success is True
    assert "$12.50" in synthesis.final_reply_text
    assert "Target" in synthesis.final_reply_text

def test_agent_process_manager_max_5_crashes_failure():
    """Test that agent process fails to restart after 5 consecutive crashes."""
    pm = AgentProcessManager(max_consecutive_crashes=5)
    pm.register_agent("CrashingWorker", lambda: CrashingWorkerAgent(fail_count=10))

    payload = AgentDelegationPayload(
        target_agent="CrashingWorker",
        user_id="user_123",
        action="test",
        payload={}
    )

    synthesis = pm.execute_task("CrashingWorker", payload)
    state = pm.get_process_state("CrashingWorker")

    assert synthesis.success is False
    assert synthesis.final_reply_text == "Agent process failed to restart after 5 consecutive crashes"
    assert state.status == "FAILED_MAX_RETRIES"
    assert state.consecutive_crashes == 5

    # Subsequent execution attempt while in FAILED_MAX_RETRIES state should be rejected
    rejected_synth = pm.execute_task("CrashingWorker", payload)
    assert rejected_synth.success is False
    assert rejected_synth.final_reply_text == "Agent process failed to restart after 5 consecutive crashes"

def test_agent_process_manager_recovery_before_5_crashes():
    """Test that agent process auto-restarts and recovers if crashes < 5."""
    pm = AgentProcessManager(max_consecutive_crashes=5)
    # Shared tracker across process restarts: crashes 2 times, then succeeds on 3rd attempt
    tracker = {"calls": 0}
    pm.register_agent("RecoveringWorker", lambda: CrashingWorkerAgent(fail_count=2, shared_tracker=tracker))

    payload = AgentDelegationPayload(
        target_agent="RecoveringWorker",
        user_id="user_123",
        action="test",
        payload={}
    )

    synthesis = pm.execute_task("RecoveringWorker", payload)
    state = pm.get_process_state("RecoveringWorker")

    assert synthesis.success is True
    assert synthesis.final_reply_text == "Recovered from crash successfully"
    assert state.status == "HEALTHY"
    assert state.consecutive_crashes == 0


def test_secretary_handles_5_consecutive_crashes_gracefully():
    """Test SecretaryAgent returns clear error response when worker process fails after 5 consecutive crashes."""
    secretary = SecretaryAgent()
    secretary.process_manager.register_agent("NewsCollector", lambda: CrashingWorkerAgent(fail_count=10))

    reply = secretary.process_message("Give me latest tech news", sender_id="user_999")
    assert reply == "Agent process failed to restart after 5 consecutive crashes"


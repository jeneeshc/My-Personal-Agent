import pytest
from agents.secretary import SecretaryAgent
from agents.news_collector import NewsCollectorAgent
from agents.money_manager import MoneyManagerAgent
from agents.task_travel_manager import TaskTravelManagerAgent
from agents.email_agent import EmailAgent
from agents.stock_agent import StockAgent
from agents.health_agent import HealthAgent
from agents.shopping_assistant import ShoppingAssistantAgent
from agents.document_manager import DocumentManagerAgent
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
    """Test Secretary intent classifier routing accuracy across all 8 domain agents."""
    secretary = SecretaryAgent()

    calendar_intent = secretary.classify_intent("Schedule meeting tomorrow at 3 PM")
    assert calendar_intent.target_agent == "TaskTravelManager"

    tech_intent = secretary.classify_intent("Give me the latest tech articles")
    assert tech_intent.target_agent == "NewsCollector"

    regional_intent = secretary.classify_intent("Show me local regional news")
    assert regional_intent.target_agent == "NewsCollector"

    money_intent = secretary.classify_intent("Paid $45.00 at Starbucks receipt")
    assert money_intent.target_agent == "MoneyManager"

    email_intent = secretary.classify_intent("Check my unread email inbox")
    assert email_intent.target_agent == "EmailAgent"

    stock_intent = secretary.classify_intent("What is the stock price for GOOGL")
    assert stock_intent.target_agent == "StockAgent"

    health_intent = secretary.classify_intent("Log my 30 min workout exercise")
    assert health_intent.target_agent == "HealthAgent"

    shopping_intent = secretary.classify_intent("Add organic milk to my grocery list")
    assert shopping_intent.target_agent == "ShoppingAssistant"

    doc_intent = secretary.classify_intent("Search drive for tax document pdf")
    assert doc_intent.target_agent == "DocumentManager"

def test_task_travel_manager_tools():
    """Test TaskTravelManager tool capabilities (schedule, itinerary, flights)."""
    agent = TaskTravelManagerAgent()

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

    itin_payload = AgentDelegationPayload(
        target_agent="TaskTravelManager",
        user_id="user_123",
        action="suggest_itinerary",
        payload={"destination": "Tokyo", "days": 3}
    )
    itin_synth = agent.execute_task(itin_payload)
    assert itin_synth.success is True
    assert "Tokyo" in itin_synth.final_reply_text

    flight_payload = AgentDelegationPayload(
        target_agent="TaskTravelManager",
        user_id="user_123",
        action="search_flights",
        payload={"origin": "SFO", "destination": "HND", "departure_date": "2026-09-01"}
    )
    flight_synth = agent.execute_task(flight_payload)
    assert flight_synth.success is True
    assert "Flights from SFO to HND" in flight_synth.final_reply_text

def test_news_collector_expanded_tools():
    """Test NewsCollector expanded tool capabilities."""
    collector = NewsCollectorAgent()

    reg_req = RegionalNewsRequest(region="San Francisco")
    reg_articles = collector.get_regional_news(reg_req)
    assert len(reg_articles) > 0

    tech_req = TechNewsRequest(technologies=["AI/ML", "Python"])
    tech_articles = collector.get_tech_news(tech_req)
    assert len(tech_articles) > 0

    weather_payload = AgentDelegationPayload(
        target_agent="NewsCollector",
        user_id="user_123",
        action="get_weather",
        payload={"location": "Seattle"}
    )
    w_synth = collector.execute_task(weather_payload)
    assert w_synth.success is True
    assert "Seattle" in w_synth.final_reply_text

def test_money_manager_expanded_tools():
    """Test MoneyManager receipt extraction, spending calculation, and subscriptions."""
    money_agent = MoneyManagerAgent()

    rec_payload = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_123",
        action="extract_receipt",
        payload={"text_content": "Paid $12.50 at Target"}
    )
    synthesis = money_agent.execute_task(rec_payload)
    assert synthesis.success is True
    assert "12.50" in synthesis.final_reply_text

    sub_payload = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_123",
        action="list_subscriptions",
        payload={}
    )
    sub_synth = money_agent.execute_task(sub_payload)
    assert sub_synth.success is True
    assert "Netflix" in sub_synth.final_reply_text

def test_money_manager_transaction_deduplication():
    """Test MoneyManager deduplication prevents duplicate expense logging."""
    money_agent = MoneyManagerAgent()
    payload1 = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_dedup",
        action="extract_receipt",
        payload={"text_content": "Paid Rs 450.00 to Swiggy via UPI Ref: 987654321"}
    )
    synthesis1 = money_agent.execute_task(payload1)
    assert synthesis1.success is True
    assert synthesis1.metadata["is_duplicate"] is False
    assert "Swiggy" in synthesis1.final_reply_text

    # Second invocation with same UPI Ref ID
    payload2 = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_dedup",
        action="extract_receipt",
        payload={"text_content": "Paid Rs 450.00 to Swiggy via UPI Ref: 987654321"}
    )
    synthesis2 = money_agent.execute_task(payload2)
    assert synthesis2.success is True
    assert synthesis2.metadata["is_duplicate"] is True
    assert "Duplicate Transaction Detected" in synthesis2.final_reply_text

def test_money_manager_hdfc_salary_credit():
    """Test MoneyManager parsing HDFC Bank Salary Credit alert emails."""
    money_agent = MoneyManagerAgent()
    payload = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_hdfc",
        action="extract_receipt",
        payload={"text_content": "HDFC Bank Alert: Rs 1,50,000.00 credited to A/C XX1234 on 01-AUG-26 towards SALARY. Avail Bal: Rs 2,45,000.00"}
    )
    synth = money_agent.execute_task(payload)
    assert synth.success is True
    assert synth.metadata["transaction_type"] == "credit"
    assert "SALARY / INCOME CREDIT RECORDED" in synth.final_reply_text
    assert "150,000.00" in synth.final_reply_text

def test_money_manager_financial_insights():
    """Test MoneyManager financial year insights, spending breakdown, and cost reduction tips."""
    money_agent = MoneyManagerAgent()
    payload = AgentDelegationPayload(
        target_agent="MoneyManager",
        user_id="user_insights",
        action="get_financial_insights",
        payload={"financial_year": "2026-2027"}
    )
    synth = money_agent.execute_task(payload)
    assert synth.success is True
    assert synth.metadata["financial_year"] == "2026-2027"
    assert "FINANCIAL INSIGHTS & SAVINGS ANALYSIS" in synth.final_reply_text
    assert "Highest Spending Category" in synth.final_reply_text
    assert "Cost-Reduction Recommendations" in synth.final_reply_text




def test_email_agent_tools():
    """Test EmailAgent tool execution."""
    agent = EmailAgent()
    payload = AgentDelegationPayload(
        target_agent="EmailAgent",
        user_id="user_123",
        action="fetch_unread_emails",
        payload={"max_results": 2}
    )
    synth = agent.execute_task(payload)
    assert synth.success is True
    assert "Unread Emails" in synth.final_reply_text

def test_stock_agent_tools():
    """Test StockAgent tool execution."""
    agent = StockAgent()
    payload = AgentDelegationPayload(
        target_agent="StockAgent",
        user_id="user_123",
        action="get_stock_price",
        payload={"ticker": "GOOGL"}
    )
    synth = agent.execute_task(payload)
    assert synth.success is True
    assert "GOOGL" in synth.final_reply_text

def test_health_agent_tools():
    """Test HealthAgent tool execution."""
    agent = HealthAgent()
    payload = AgentDelegationPayload(
        target_agent="HealthAgent",
        user_id="user_123",
        action="log_workout",
        payload={"activity_type": "Cycling", "duration_minutes": 45}
    )
    synth = agent.execute_task(payload)
    assert synth.success is True
    assert "Cycling" in synth.final_reply_text

def test_shopping_assistant_tools():
    """Test ShoppingAssistantAgent tool execution."""
    agent = ShoppingAssistantAgent()
    payload = AgentDelegationPayload(
        target_agent="ShoppingAssistant",
        user_id="user_123",
        action="check_product_price",
        payload={"product_name": "Wireless Headphones"}
    )
    synth = agent.execute_task(payload)
    assert synth.success is True
    assert "Wireless Headphones" in synth.final_reply_text

def test_document_manager_tools():
    """Test DocumentManagerAgent tool execution."""
    agent = DocumentManagerAgent()
    payload = AgentDelegationPayload(
        target_agent="DocumentManager",
        user_id="user_123",
        action="search_drive",
        payload={"query": "financials"}
    )
    synth = agent.execute_task(payload)
    assert synth.success is True
    assert "financials" in synth.final_reply_text

def test_secretary_routes_to_all_8_agents():
    """Test SecretaryAgent end-to-end delegation across all 8 worker agents."""
    secretary = SecretaryAgent()
    user = "user_test_8"

    r1 = secretary.process_message("Schedule a meeting tomorrow", user)
    assert "Event Scheduled" in r1 or "Calendar" in r1

    r2 = secretary.process_message("Get regional news", user)
    assert "REGIONAL" in r2 or "Regional" in r2

    r3 = secretary.process_message("Check my spent money and active subscriptions", user)
    assert "Subscriptions" in r3 or "Receipt" in r3

    r4 = secretary.process_message("Fetch my unread email inbox", user)
    assert "Unread Emails" in r4

    r5 = secretary.process_message("Check stock price for GOOGL", user)
    assert "GOOGL" in r5

    r6 = secretary.process_message("Log my 30 min running workout", user)
    assert "Workout Logged" in r6

    r7 = secretary.process_message("Check product price for noise cancelling headphones", user)
    assert "Price Drop Alert" in r7

    r8 = secretary.process_message("Search drive for tax documents", user)
    assert "Google Drive Search" in r8

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

    rejected_synth = pm.execute_task("CrashingWorker", payload)
    assert rejected_synth.success is False
    assert rejected_synth.final_reply_text == "Agent process failed to restart after 5 consecutive crashes"

def test_agent_process_manager_recovery_before_5_crashes():
    """Test that agent process auto-restarts and recovers if crashes < 5."""
    pm = AgentProcessManager(max_consecutive_crashes=5)
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

def test_secretary_greeting_and_capabilities_menu():
    """Test SecretaryAgent greeting recognition and interactive capability menu."""
    secretary = SecretaryAgent()
    greeting_reply = secretary.process_message("Hi", "user_greet_1")
    assert "Welcome to your AI Personal Assistant" in greeting_reply
    assert "1️⃣ 📰 *Today's News*" in greeting_reply
    assert "8️⃣ 📄 *Document Drive*" in greeting_reply

def test_news_collector_todays_news_4_tier_segregation():
    """Test NewsCollector 4-tier news feed segregation (Malayalam, Indian, Global, Tech/AI Data Science)."""
    collector = NewsCollectorAgent()
    payload = AgentDelegationPayload(
        target_agent="NewsCollector",
        user_id="user_123",
        action="get_todays_news",
        payload={"importance_threshold": "medium"}
    )
    synth = collector.execute_task(payload)
    assert synth.success is True
    assert "TODAY'S MAIN NEWS DIGEST" in synth.final_reply_text
    assert "LOCAL MALAYALAM NEWS" in synth.final_reply_text
    assert "REGIONAL INDIAN NEWS" in synth.final_reply_text
    assert "GLOBAL MAIN HEADLINES" in synth.final_reply_text
    assert "TECH, AI & DATA SCIENCE DIGEST" in synth.final_reply_text
    # Verify Malayalam news and Data Science content
    assert "കേരള" in synth.final_reply_text
    assert "PyTorch" in synth.final_reply_text or "Data Science" in synth.final_reply_text

def test_secretary_routes_todays_news_option_1():
    """Test user replying with option '1' or 'Today's News' routes to 4-tier news feed."""
    secretary = SecretaryAgent()
    r1 = secretary.process_message("1", "user_opt_1")
    assert "LOCAL MALAYALAM NEWS" in r1
    assert "REGIONAL INDIAN NEWS" in r1
    assert "GLOBAL MAIN HEADLINES" in r1
    assert "TECH, AI & DATA SCIENCE DIGEST" in r1

    r2 = secretary.process_message("Today's News", "user_opt_2")
    assert "TODAY'S MAIN NEWS DIGEST" in r2


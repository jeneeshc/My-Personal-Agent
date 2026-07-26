"""
Pydantic Schema Models implementing contracts defined in specs/
Single source of truth for python models reflecting JSON / OpenAPI contracts in specs/
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

# ==========================================
# 1. Secretary & Messaging Protocol Schemas
# ==========================================

class ProcessMessageRequest(BaseModel):
    message: str = Field(..., description="Raw text of incoming user message")
    sender_id: str = Field(..., description="Unique user sender identifier (WhatsApp ID)")
    context_overrides: Optional[Dict[str, Any]] = None

class IntentClassification(BaseModel):
    primary_intent: Literal[
        "calendar_travel",
        "news_info",
        "email_summarize",
        "stock_business",
        "money_manager",
        "health_wellness",
        "shopping",
        "document_drive",
        "general_conversation"
    ]
    target_agent: Literal[
        "TaskTravelManager",
        "NewsCollector",
        "EmailAgent",
        "StockAgent",
        "MoneyManager",
        "HealthAgent",
        "ShoppingAssistant",
        "DocumentManager",
        "DirectSecretary"
    ]
    confidence: float = Field(..., ge=0.0, le=1.0)

class AgentDelegationPayload(BaseModel):
    delegation_id: str = Field(default_factory=lambda: str(uuid4()))
    target_agent: str
    user_id: str
    action: str
    payload: Dict[str, Any]

class AgentResponseSynthesis(BaseModel):
    delegation_id: str
    success: bool
    final_reply_text: str
    metadata: Optional[Dict[str, Any]] = None

class AgentProcessStatus(str, Enum if 'Enum' in globals() else object):
    HEALTHY = "HEALTHY"
    RESTARTING = "RESTARTING"
    FAILED_MAX_RETRIES = "FAILED_MAX_RETRIES"

class AgentProcessState(BaseModel):
    agent_name: str
    status: Literal["HEALTHY", "RESTARTING", "FAILED_MAX_RETRIES"] = "HEALTHY"
    consecutive_crashes: int = 0
    max_consecutive_crashes: int = 5
    last_error: Optional[str] = None
    last_crash_timestamp: Optional[float] = None



# ==========================================
# 2. Domain Data Models
# ==========================================

class UserProfile(BaseModel):
    user_id: str
    phone_number: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_authenticated: bool = False
    google_oauth_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None

class ScheduledTaskConfig(BaseModel):
    task_id: str
    user_id: str
    task_type: Literal["daily_email_summary", "weekly_news_summary", "stock_update", "health_checkin"]
    cron_expression: str
    is_active: bool = True
    last_run_at: Optional[str] = None

class ExpenseRecord(BaseModel):
    record_id: str
    user_id: str
    merchant: str
    amount: float
    currency: str = "USD"
    category: Optional[str] = None
    date: str
    source_raw_text: Optional[str] = None


# ==========================================
# 3. Worker Agent Tool Request Models
# ==========================================

class ScheduleEventRequest(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = None
    location: Optional[str] = None

class GetCalendarEventsRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_results: int = 10

class SuggestItineraryRequest(BaseModel):
    destination: str
    days: int
    interests: Optional[List[str]] = Field(default_factory=lambda: ["culture", "sightseeing", "food"])

class SearchFlightsRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None

class RegionalNewsRequest(BaseModel):
    region: Optional[str] = Field(default=None, description="Target geographic region or city")
    categories: List[str] = Field(default_factory=lambda: ["local", "weather", "city_updates"])
    max_results: int = 5

class TechNewsRequest(BaseModel):
    technologies: List[str] = Field(default_factory=lambda: ["AI/ML", "Cloud Computing", "Software Engineering"])
    timeframe: str = "last_24_hours"
    max_results: int = 5

class NewsRequest(BaseModel):
    category: str = Field(default="general", description="News category e.g., tech, sports, business")
    topic_keywords: Optional[List[str]] = None

class EmailSummaryRequest(BaseModel):
    thread_id: str
    max_results: int = 5

class DraftReplyRequest(BaseModel):
    thread_id: str
    instructions: str

class StockPriceRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")

class ExtractReceiptRequest(BaseModel):
    text_content: str = Field(..., description="Raw text of SMS or email")
    source: Literal["email", "sms", "manual"] = "email"

class LogWorkoutRequest(BaseModel):
    activity_type: str
    duration_minutes: int
    calories_burned: Optional[int] = None

class GroceryItemRequest(BaseModel):
    item_name: str
    action: Literal["add", "remove", "check"]
    quantity: int = 1

class SearchDriveRequest(BaseModel):
    query: str
    file_type: Optional[str] = None

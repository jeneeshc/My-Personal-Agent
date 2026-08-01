"""
Secretary Agent Implementation (Supervisor Router & Delegator)
Conforms to specs/agents/secretary_protocol.yaml
"""
import os
from typing import Dict, Any, Optional
from models.agent_schemas import (
    ProcessMessageRequest,
    IntentClassification,
    AgentDelegationPayload,
    AgentResponseSynthesis
)
from agents.news_collector import NewsCollectorAgent
from agents.money_manager import MoneyManagerAgent
from agents.task_travel_manager import TaskTravelManagerAgent
from agents.email_agent import EmailAgent
from agents.stock_agent import StockAgent
from agents.health_agent import HealthAgent
from agents.shopping_assistant import ShoppingAssistantAgent
from agents.document_manager import DocumentManagerAgent
from agents.process_manager import AgentProcessManager

class SecretaryAgent:
    def __init__(self):
        # Register all 8 specialized worker agents with AgentProcessManager
        self.process_manager = AgentProcessManager(max_consecutive_crashes=5)
        self.process_manager.register_agent("NewsCollector", lambda: NewsCollectorAgent())
        self.process_manager.register_agent("MoneyManager", lambda: MoneyManagerAgent())
        self.process_manager.register_agent("TaskTravelManager", lambda: TaskTravelManagerAgent())
        self.process_manager.register_agent("EmailAgent", lambda: EmailAgent())
        self.process_manager.register_agent("StockAgent", lambda: StockAgent())
        self.process_manager.register_agent("HealthAgent", lambda: HealthAgent())
        self.process_manager.register_agent("ShoppingAssistant", lambda: ShoppingAssistantAgent())
        self.process_manager.register_agent("DocumentManager", lambda: DocumentManagerAgent())

    def get_capabilities_menu(self) -> str:
        """
        Generate interactive capabilities greeting menu formatted for WhatsApp UI delivery.
        """
        return (
            "👋 *Welcome to your AI Personal Assistant!*\n\n"
            "I can assist you across 8 specialized domain capabilities. "
            "Please click or reply with any option below:\n\n"
            "1️⃣ 📰 *Today's News* (Local Malayalam, Regional Indian, Global & AI/Data Science Digest)\n"
            "2️⃣ 📅 *Schedule & Travel* (Calendar events, meeting booking & flight searches)\n"
            "3️⃣ 💰 *Money & Expenses* (Receipt parsing, spending analytics & subscriptions)\n"
            "4️⃣ 📧 *Email Digest* (Unread Gmail inbox, thread summaries & draft replies)\n"
            "5️⃣ 📈 *Stocks & Markets* (Real-time ticker price quotes & market news)\n"
            "6️⃣ 🥗 *Health & Wellness* (Workout session logging & healthy meal planning)\n"
            "7️⃣ 🛒 *Shopping Assistant* (Grocery list management & price drop alerts)\n"
            "8️⃣ 📄 *Document Drive* (Google Drive search & PDF/Doc summaries)\n\n"
            "💡 *Tip:* Reply with a number (e.g. *1*) or type your request directly!"
        )

    def generate_morning_digest(self, user_id: str = "default_user") -> str:
        """
        Synthesize automated 6:00 AM IST Daily Morning Briefing:
        - Gmail receipt sync & spending check
        - 4-Tier News Digest (Malayalam, Indian, Global, AI/Data Science)
        - Today's Calendar Schedule
        """
        # 1. Today's News Digest
        news_payload = AgentDelegationPayload(
            target_agent="NewsCollector",
            user_id=user_id,
            action="get_todays_news",
            payload={"importance_threshold": "medium"}
        )
        news_synth = self.process_manager.execute_task("NewsCollector", news_payload)

        # 2. Calendar Schedule
        cal_payload = AgentDelegationPayload(
            target_agent="TaskTravelManager",
            user_id=user_id,
            action="get_calendar_events",
            payload={}
        )
        cal_synth = self.process_manager.execute_task("TaskTravelManager", cal_payload)

        # 3. Expense Summary
        money_payload = AgentDelegationPayload(
            target_agent="MoneyManager",
            user_id=user_id,
            action="calculate_spending",
            payload={"days": 1}
        )
        money_synth = self.process_manager.execute_task("MoneyManager", money_payload)

        return (
            f"☀️ *DAILY MORNING BRIEFING (6:00 AM IST)*\n"
            f"Good morning! Here is your personalized daily briefing:\n\n"
            f"{news_synth.final_reply_text}\n\n"
            f"{cal_synth.final_reply_text}\n\n"
            f"{money_synth.final_reply_text}\n\n"
            f"Have a productive day ahead! 🚀"
        )


    def classify_intent(self, message: str) -> IntentClassification:
        """
        Classify incoming user message intent into target agent routing contract.
        In production, this is driven by Gemini Pro structured JSON output.
        """
        msg_lower = message.strip().lower()

        # Direct greeting & menu keywords check
        if msg_lower in ["hi", "hello", "hey", "start", "menu", "capabilities", "options", "help", "/start"]:
            return IntentClassification(
                primary_intent="capabilities_greeting",
                target_agent="DirectSecretary",
                confidence=1.0
            )

        if msg_lower == "1" or any(w in msg_lower for w in ["today's news", "main news", "news headlines", "malayalam news", "regional news"]):
            return IntentClassification(
                primary_intent="news_info",
                target_agent="NewsCollector",
                confidence=0.98
            )
        elif msg_lower == "2" or any(w in msg_lower for w in ["calendar", "schedule", "meeting", "flight", "itinerary", "trip"]):
            return IntentClassification(
                primary_intent="calendar_travel",
                target_agent="TaskTravelManager",
                confidence=0.95
            )
        elif msg_lower == "3" or any(w in msg_lower for w in ["money", "receipt", "finance", "expense", "subscription", "spent", "$"]):
            return IntentClassification(
                primary_intent="money_manager",
                target_agent="MoneyManager",
                confidence=0.95
            )
        elif msg_lower == "4" or any(w in msg_lower for w in ["email", "unread", "inbox", "mail", "draft"]):
            return IntentClassification(
                primary_intent="email_summarize",
                target_agent="EmailAgent",
                confidence=0.95
            )
        elif msg_lower == "5" or any(w in msg_lower for w in ["stock", "ticker", "shares", "market", "nasdaq", "dow"]):
            return IntentClassification(
                primary_intent="stock_business",
                target_agent="StockAgent",
                confidence=0.95
            )
        elif msg_lower == "6" or any(w in msg_lower for w in ["workout", "exercise", "calories", "meal", "diet", "fitness"]):
            return IntentClassification(
                primary_intent="health_wellness",
                target_agent="HealthAgent",
                confidence=0.95
            )
        elif msg_lower == "7" or any(w in msg_lower for w in ["grocery", "shopping", "price", "buy", "store"]):
            return IntentClassification(
                primary_intent="shopping",
                target_agent="ShoppingAssistant",
                confidence=0.95
            )
        elif msg_lower == "8" or any(w in msg_lower for w in ["drive", "file", "document", "pdf", "docx"]):
            return IntentClassification(
                primary_intent="document_drive",
                target_agent="DocumentManager",
                confidence=0.95
            )
        elif any(w in msg_lower for w in ["news", "tech", "technology", "regional", "weather", "headline"]):
            return IntentClassification(
                primary_intent="news_info",
                target_agent="NewsCollector",
                confidence=0.90
            )
        else:
            return IntentClassification(
                primary_intent="general_conversation",
                target_agent="DirectSecretary",
                confidence=0.85
            )

    def process_message(self, message: str, sender_id: str) -> str:
        """
        Process incoming user message, classify intent, delegate to worker agent via
        AgentProcessManager, and synthesize response.
        """
        intent = self.classify_intent(message)
        print(f"[Secretary Router] Message from {sender_id} classified as {intent.primary_intent} -> {intent.target_agent}")

        if intent.primary_intent == "capabilities_greeting":
            return self.get_capabilities_menu()

        if intent.target_agent in self.process_manager.process_states:
            action = "default"
            payload_data = {}
            msg_lower = message.lower()

            if intent.target_agent == "NewsCollector":
                if message.strip() == "1" or any(w in msg_lower for w in ["today's news", "todays news", "main news", "headlines", "malayalam"]):
                    action = "get_todays_news"
                    payload_data = {"importance_threshold": "medium"}
                elif "tech" in msg_lower:
                    action = "get_tech_news"
                elif "weather" in msg_lower:
                    action = "get_weather"
                    payload_data = {"location": "San Francisco"}
                elif "search" in msg_lower:
                    action = "search_topic"
                    payload_data = {"topic": message}
                else:
                    action = "get_todays_news"
                    payload_data = {"importance_threshold": "medium"}

            elif intent.target_agent == "TaskTravelManager":
                if "flight" in msg_lower:
                    action = "search_flights"
                    payload_data = {"origin": "SFO", "destination": "JFK", "departure_date": "2026-08-10"}
                elif "trip" in msg_lower or "itinerary" in msg_lower:
                    action = "suggest_itinerary"
                    payload_data = {"destination": "Paris", "days": 3}
                elif "schedule" in msg_lower or "meeting" in msg_lower:
                    action = "schedule_event"
                    payload_data = {
                        "title": "Meeting from WhatsApp",
                        "start_time": "2026-08-05T15:00:00Z",
                        "end_time": "2026-08-05T16:00:00Z"
                    }
                else:
                    action = "get_calendar_events"

            elif intent.target_agent == "MoneyManager":
                if "subscription" in msg_lower:
                    action = "list_subscriptions"
                elif "spent" in msg_lower or "spending" in msg_lower:
                    action = "calculate_spending"
                else:
                    action = "extract_receipt"
                    payload_data = {"text_content": message}

            elif intent.target_agent == "EmailAgent":
                if "unread" in msg_lower or "inbox" in msg_lower:
                    action = "fetch_unread_emails"
                elif "draft" in msg_lower:
                    action = "draft_reply"
                    payload_data = {"thread_id": "thread_001", "instructions": message}
                else:
                    action = "summarize_thread"
                    payload_data = {"thread_id": "thread_001"}

            elif intent.target_agent == "StockAgent":
                if "news" in msg_lower:
                    action = "get_company_news"
                    payload_data = {"company_or_ticker": "GOOGL"}
                else:
                    action = "get_stock_price"
                    ticker_str = "GOOGL"
                    stop_words = {"CHECK", "STOCK", "PRICE", "FOR", "WHAT", "IS", "MY", "GET", "THE", "SHOW"}
                    words = message.upper().split()
                    for w in words:
                        if len(w) <= 5 and w.isalpha() and w not in stop_words:
                            ticker_str = w
                            break
                    payload_data = {"ticker": ticker_str}

            elif intent.target_agent == "HealthAgent":
                if "meal" in msg_lower or "diet" in msg_lower:
                    action = "suggest_meal_plan"
                else:
                    action = "log_workout"
                    payload_data = {"activity_type": "Running", "duration_minutes": 30}

            elif intent.target_agent == "ShoppingAssistant":
                if "price" in msg_lower:
                    action = "check_product_price"
                    payload_data = {"product_name": "Noise Cancelling Headphones"}
                else:
                    action = "manage_grocery_list"
                    payload_data = {"item_name": "Organic Milk", "action": "add", "quantity": 1}

            elif intent.target_agent == "DocumentManager":
                if "summarize" in msg_lower:
                    action = "summarize_document"
                    payload_data = {"file_id": "file_doc_101", "file_name": "Q3_Strategy.pdf"}
                else:
                    action = "search_drive"
                    payload_data = {"query": message}

            delegation = AgentDelegationPayload(
                target_agent=intent.target_agent,
                user_id=sender_id,
                action=action,
                payload=payload_data
            )
            
            synthesis: AgentResponseSynthesis = self.process_manager.execute_task(
                intent.target_agent, delegation
            )
            return synthesis.final_reply_text

        # Direct Secretary conversation fallback
        return self.get_capabilities_menu()

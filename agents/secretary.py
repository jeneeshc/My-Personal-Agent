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
from agents.process_manager import AgentProcessManager

class SecretaryAgent:
    def __init__(self):
        # Register available worker agents with AgentProcessManager
        self.process_manager = AgentProcessManager(max_consecutive_crashes=5)
        self.process_manager.register_agent("NewsCollector", lambda: NewsCollectorAgent())
        self.process_manager.register_agent("MoneyManager", lambda: MoneyManagerAgent())
        self.process_manager.register_agent("TaskTravelManager", lambda: TaskTravelManagerAgent())

    def classify_intent(self, message: str) -> IntentClassification:
        """
        Classify incoming user message intent into target agent routing contract.
        In production, this is driven by Gemini Pro structured JSON output.
        """
        msg_lower = message.lower()

        if "calendar" in msg_lower or "schedule" in msg_lower or "meeting" in msg_lower or "flight" in msg_lower or "itinerary" in msg_lower or "trip" in msg_lower:
            return IntentClassification(
                primary_intent="calendar_travel",
                target_agent="TaskTravelManager",
                confidence=0.95
            )
        elif "tech" in msg_lower or "technology" in msg_lower:
            return IntentClassification(
                primary_intent="news_info",
                target_agent="NewsCollector",
                confidence=0.95
            )
        elif "news" in msg_lower or "regional" in msg_lower or "weather" in msg_lower:
            return IntentClassification(
                primary_intent="news_info",
                target_agent="NewsCollector",
                confidence=0.90
            )
        elif "money" in msg_lower or "receipt" in msg_lower or "finance" in msg_lower or "$" in msg_lower:
            return IntentClassification(
                primary_intent="money_manager",
                target_agent="MoneyManager",
                confidence=0.92
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

        if intent.target_agent in self.process_manager.process_states:
            # Formulate payload based on action
            action = "default"
            payload_data = {}
            msg_lower = message.lower()

            if intent.target_agent == "TaskTravelManager":
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
                        "start_time": "2026-07-26T15:00:00Z",
                        "end_time": "2026-07-26T16:00:00Z"
                    }
                else:
                    action = "get_calendar_events"

            elif intent.target_agent == "NewsCollector":
                if "tech" in msg_lower:
                    action = "get_tech_news"
                elif "regional" in msg_lower or "local" in msg_lower:
                    action = "get_regional_news"

            elif intent.target_agent == "MoneyManager":
                action = "extract_receipt"
                payload_data = {"text_content": message}

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
        return f"Hello! I am your Personal Assistant Secretary. I received: '{message}'. How can I help you with your Calendar, News, Expenses, or Tasks?"


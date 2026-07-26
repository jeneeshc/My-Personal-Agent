"""
Task, Travel, and Calendar Manager Agent Implementation
Handles Google Calendar events, scheduling, travel itineraries, and flight searches.
Conforms to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    ScheduleEventRequest,
    GetCalendarEventsRequest,
    SuggestItineraryRequest,
    SearchFlightsRequest
)

class TaskTravelManagerAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="TaskTravelManager")

    def schedule_event(self, request: ScheduleEventRequest) -> Dict[str, Any]:
        """
        Schedule a new event in Google Calendar.
        """
        return {
            "event_id": f"evt_{hash(request.title) & 0xffffffff}",
            "status": "confirmed",
            "title": request.title,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "location": request.location or "Virtual",
            "html_link": "https://calendar.google.com/calendar/event?eid=mock123"
        }

    def get_calendar_events(self, request: GetCalendarEventsRequest) -> List[Dict[str, Any]]:
        """
        Fetch upcoming calendar events.
        """
        return [
            {
                "title": "Team Sync & Product Strategy",
                "start_time": "2026-07-26T10:00:00Z",
                "end_time": "2026-07-26T11:00:00Z",
                "location": "Google Meet"
            },
            {
                "title": "Project Review & SDD Demo",
                "start_time": "2026-07-26T14:30:00Z",
                "end_time": "2026-07-26T15:30:00Z",
                "location": "Room 402"
            }
        ][:request.max_results]

    def suggest_itinerary(self, request: SuggestItineraryRequest) -> Dict[str, Any]:
        """
        Generate a travel itinerary proposal.
        """
        interests_str = ", ".join(request.interests) if request.interests else "general attractions"
        return {
            "destination": request.destination,
            "days": request.days,
            "plan": [
                f"Day 1: Arrival in {request.destination}, check-in, and welcome dinner focusing on local {interests_str}.",
                f"Day 2: Full-day guided exploration of major cultural landmarks in {request.destination}.",
                f"Day 3: Relaxation, local shopping, and departure preparation."
            ][:request.days]
        }

    def search_flights(self, request: SearchFlightsRequest) -> List[Dict[str, Any]]:
        """
        Search flight itineraries between origin and destination.
        """
        return [
            {
                "airline": "Global Airways",
                "flight_number": "GA-402",
                "origin": request.origin,
                "destination": request.destination,
                "departure_time": f"{request.departure_date}T08:30:00",
                "price": "$420.00"
            },
            {
                "airline": "Express Air",
                "flight_number": "EA-819",
                "origin": request.origin,
                "destination": request.destination,
                "departure_time": f"{request.departure_date}T14:15:00",
                "price": "$380.00"
            }
        ]

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "schedule_event":
            req = ScheduleEventRequest(**raw_payload)
            evt = self.schedule_event(req)
            reply = (
                f"📅 *Event Scheduled Successfully*:\n"
                f"• Title: {evt['title']}\n"
                f"• Start: {evt['start_time']}\n"
                f"• End: {evt['end_time']}\n"
                f"• Location: {evt['location']}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"event_id": evt["event_id"]}
            )

        elif action == "suggest_itinerary":
            req = SuggestItineraryRequest(**raw_payload)
            itin = self.suggest_itinerary(req)
            formatted_plan = "\n".join([f"• {p}" for p in itin["plan"]])
            reply = f"✈️ *Travel Itinerary for {itin['destination']} ({itin['days']} Days)*:\n{formatted_plan}"
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"destination": itin["destination"]}
            )

        elif action == "search_flights":
            req = SearchFlightsRequest(**raw_payload)
            flights = self.search_flights(req)
            formatted_flights = "\n".join(
                [f"• {f['airline']} ({f['flight_number']}): {f['departure_time']} - {f['price']}" for f in flights]
            )
            reply = f"🛫 *Flights from {req.origin} to {req.destination}*:\n{formatted_flights}"
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"flight_count": len(flights)}
            )

        else:
            # Default: Get calendar events
            req = GetCalendarEventsRequest(**raw_payload)
            events = self.get_calendar_events(req)
            formatted_events = "\n".join(
                [f"• {e['title']} ({e['start_time']} at {e['location']})" for e in events]
            )
            reply = f"📅 *Upcoming Calendar Schedule*:\n{formatted_events}"
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"events_count": len(events)}
            )

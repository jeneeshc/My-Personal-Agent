"""
Health & Wellness Agent Implementation
Tracks fitness goals, activity logging, and healthy habit/meal recommendations.
Conforms to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    LogWorkoutRequest,
    SuggestMealPlanRequest
)

class HealthAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="HealthAgent")

    def log_workout(self, request: LogWorkoutRequest) -> Dict[str, Any]:
        """
        Log workout session details.
        """
        cals = request.calories_burned or (request.duration_minutes * 8)
        return {
            "workout_id": f"work_{hash(request.activity_type) & 0xffffffff}",
            "activity_type": request.activity_type,
            "duration_minutes": request.duration_minutes,
            "calories_burned": cals,
            "logged_at": "2026-08-01T07:00:00Z"
        }

    def suggest_meal_plan(self, request: SuggestMealPlanRequest) -> Dict[str, Any]:
        """
        Generate healthy meal plan recommendations.
        """
        pref = request.dietary_preference
        return {
            "dietary_preference": pref,
            "days": request.days,
            "meals": [
                {
                    "meal": "Breakfast",
                    "suggestion": f"Avocado toast with poached eggs and green tea ({pref} friendly)"
                },
                {
                    "meal": "Lunch",
                    "suggestion": "Grilled chicken/tofu quinoa bowl with mixed roasted veggies"
                },
                {
                    "meal": "Dinner",
                    "suggestion": "Pan-seared salmon or lentils with steamed broccoli & sweet potato"
                }
            ]
        }

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "suggest_meal_plan":
            req = SuggestMealPlanRequest(**raw_payload)
            plan = self.suggest_meal_plan(req)
            formatted_meals = "\n".join([f"• *{m['meal']}*: {m['suggestion']}" for m in plan["meals"]])
            reply = f"🥗 *Healthy Meal Plan ({plan['dietary_preference'].capitalize()})*:\n{formatted_meals}"
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"dietary_preference": plan["dietary_preference"]}
            )

        else:
            # Default: log_workout
            req = LogWorkoutRequest(**raw_payload)
            w = self.log_workout(req)
            reply = (
                f"🏋️ *Workout Logged Successfully*:\n"
                f"• Activity: {w['activity_type'].capitalize()}\n"
                f"• Duration: {w['duration_minutes']} mins\n"
                f"• Est. Calories Burned: {w['calories_burned']} kcal"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"workout_id": w["workout_id"], "calories": w["calories_burned"]}
            )

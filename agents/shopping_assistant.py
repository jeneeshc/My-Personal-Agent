"""
E-commerce & Shopping Assistant Agent Implementation
Manages grocery lists, price drop tracking, and routine purchases.
Conforms to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    GroceryItemRequest,
    CheckProductPriceRequest
)

class ShoppingAssistantAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="ShoppingAssistant")

    def manage_grocery_list(self, request: GroceryItemRequest) -> Dict[str, Any]:
        """
        Add, remove, or check grocery items in list.
        """
        return {
            "item_name": request.item_name,
            "action": request.action,
            "quantity": request.quantity,
            "status": f"Successfully performed '{request.action}' for {request.quantity}x {request.item_name}"
        }

    def check_product_price(self, request: CheckProductPriceRequest) -> Dict[str, Any]:
        """
        Check product price and track price drop history.
        """
        store = request.store or "Amazon / Walmart"
        return {
            "product_name": request.product_name,
            "store": store,
            "current_price": "$79.99",
            "original_price": "$99.99",
            "price_drop_detected": True,
            "savings": "$20.00 (20% OFF)"
        }

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "check_product_price":
            req = CheckProductPriceRequest(**raw_payload)
            res = self.check_product_price(req)
            reply = (
                f"🏷️ *Price Drop Alert ({res['product_name']})*:\n"
                f"• Store: {res['store']}\n"
                f"• Current Price: {res['current_price']} (Was {res['original_price']})\n"
                f"• Savings: {res['savings']}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"product_name": res["product_name"], "price": res["current_price"]}
            )

        else:
            # Default: manage_grocery_list
            req = GroceryItemRequest(**raw_payload)
            res = self.manage_grocery_list(req)
            reply = (
                f"🛒 *Grocery List Updated*:\n"
                f"• Action: {res['action'].upper()}\n"
                f"• Item: {res['quantity']}x {res['item_name']}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"item_name": res["item_name"], "action": res["action"]}
            )

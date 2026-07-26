"""
Money Manager Agent Implementation
Handles financial receipt parsing and expense tracking according to specs/agents/worker_tools.yaml
"""
import re
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    ExtractReceiptRequest,
    ExpenseRecord
)

class MoneyManagerAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="MoneyManager")

    def extract_receipt(self, request: ExtractReceiptRequest, user_id: str) -> ExpenseRecord:
        """
        Extract expense details from text content (SMS/Email text).
        """
        text = request.text_content
        # Extract dollar amount pattern (e.g. $45.99)
        amount_match = re.search(r'\$\s*([0-9]+(?:\.[0-9]{2})?)', text)
        amount = float(amount_match.group(1)) if amount_match else 0.0

        # Simple merchant extraction
        merchant = "Unknown Merchant"
        if "at " in text.lower():
            parts = text.lower().split("at ")
            merchant = parts[1].split()[0].capitalize()

        return ExpenseRecord(
            record_id=f"exp_{hash(text) & 0xffffffff}",
            user_id=user_id,
            merchant=merchant,
            amount=amount,
            currency="USD",
            category="general",
            date="2026-07-25",
            source_raw_text=text
        )

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        raw_payload = payload.payload or {}
        req = ExtractReceiptRequest(**raw_payload)
        record = self.extract_receipt(req, payload.user_id)

        reply = (
            f"💰 *Receipt Processed*:\n"
            f"• Merchant: {record.merchant}\n"
            f"• Amount: ${record.amount:.2f} {record.currency}\n"
            f"• Category: {record.category}"
        )

        return AgentResponseSynthesis(
            delegation_id=payload.delegation_id,
            success=True,
            final_reply_text=reply,
            metadata={"record_id": record.record_id, "amount": record.amount}
        )

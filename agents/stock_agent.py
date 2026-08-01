"""
Business Updates & Stock Performance Agent Implementation
Tracks market trends, ticker quotes, and relevant business news.
Conforms to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    StockPriceRequest,
    GetCompanyNewsRequest
)

class StockAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="StockAgent")

    def get_stock_price(self, request: StockPriceRequest) -> Dict[str, Any]:
        """
        Get real-time / current stock ticker price quote.
        """
        ticker = request.ticker.upper()
        # Mock price lookup data
        mock_prices = {
            "GOOGL": {"price": 182.50, "change": "+1.8%", "currency": "USD"},
            "AAPL": {"price": 224.10, "change": "+0.4%", "currency": "USD"},
            "MSFT": {"price": 448.90, "change": "-0.2%", "currency": "USD"},
            "AMZN": {"price": 186.30, "change": "+1.1%", "currency": "USD"}
        }
        data = mock_prices.get(ticker, {"price": 150.00, "change": "0.0%", "currency": "USD"})
        return {
            "ticker": ticker,
            "price": data["price"],
            "change": data["change"],
            "currency": data["currency"]
        }

    def get_company_news(self, request: GetCompanyNewsRequest) -> List[Dict[str, Any]]:
        """
        Fetch company news and market updates.
        """
        target = request.company_or_ticker.upper()
        return [
            {
                "title": f"{target} Announces Q2 Earnings Growth and New AI Partnership",
                "source": "Bloomberg",
                "published": "2026-07-31T14:00:00Z"
            },
            {
                "title": f"Market Analysts Upgrade {target} Price Target",
                "source": "Reuters",
                "published": "2026-07-30T11:30:00Z"
            }
        ][:request.max_results]

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "get_company_news":
            req = GetCompanyNewsRequest(**raw_payload)
            articles = self.get_company_news(req)
            formatted = "\n".join([f"• {a['title']} ({a['source']})" for a in articles])
            reply = f"📰 *Business News for {req.company_or_ticker.upper()}*:\n{formatted}"
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"news_count": len(articles)}
            )

        else:
            # Default: get_stock_price
            req = StockPriceRequest(**raw_payload)
            quote = self.get_stock_price(req)
            reply = (
                f"📈 *Stock Quote ({quote['ticker']})*:\n"
                f"• Price: ${quote['price']:.2f} {quote['currency']}\n"
                f"• Today's Change: {quote['change']}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=reply,
                metadata={"ticker": quote["ticker"], "price": quote["price"]}
            )

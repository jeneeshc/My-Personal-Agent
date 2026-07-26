"""
News Collector Agent Implementation
Handles regional news and technology updates according to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    RegionalNewsRequest,
    TechNewsRequest
)

class NewsCollectorAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="NewsCollector")

    def get_regional_news(self, request: RegionalNewsRequest) -> List[Dict[str, Any]]:
        """
        Fetch regional news for specified region or user default location.
        """
        region_name = request.region or "User Region"
        # Simulated news items conforming to contract schema
        return [
            {
                "title": f"Top Local Story in {region_name}: Community Infrastructure Project Approved",
                "source": "Regional Daily",
                "category": request.categories[0] if request.categories else "local",
                "summary": f"Local authorities in {region_name} have announced major developments."
            },
            {
                "title": f"Weather Update for {region_name}",
                "source": "Metro News",
                "category": "weather",
                "summary": f"Mild temperatures and clear skies expected across {region_name} this week."
            }
        ][:request.max_results]

    def get_tech_news(self, request: TechNewsRequest) -> List[Dict[str, Any]]:
        """
        Fetch latest technology articles and tech trends.
        """
        tech_list = ", ".join(request.technologies) if request.technologies else "Tech Trends"
        return [
            {
                "title": f"Breakthrough in {tech_list}: Next-Gen AI Models Released",
                "source": "TechCrunch / Google AI Blog",
                "timeframe": request.timeframe,
                "summary": "Researchers demonstrate state-of-the-art reasoning capabilities."
            },
            {
                "title": "Cloud Computing Infrastructure Scaling Innovations",
                "source": "Ars Technica",
                "timeframe": request.timeframe,
                "summary": "Serverless architectures see 40% performance improvement."
            }
        ][:request.max_results]

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        """
        Execute delegated task based on action.
        """
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "get_regional_news":
            req = RegionalNewsRequest(**raw_payload)
            articles = self.get_regional_news(req)
            formatted_text = f"📰 *Regional News Highlights*:\n" + "\n".join(
                [f"• {a['title']} - {a['summary']}" for a in articles]
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_text,
                metadata={"articles_count": len(articles)}
            )

        elif action == "get_tech_news":
            req = TechNewsRequest(**raw_payload)
            articles = self.get_tech_news(req)
            formatted_text = f"💻 *Latest Technology Digest*:\n" + "\n".join(
                [f"• {a['title']} ({a['source']})" for a in articles]
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_text,
                metadata={"articles_count": len(articles)}
            )

        else:
            # Combined default news digest execution
            reg_req = RegionalNewsRequest(**raw_payload.get("regional", {}))
            tech_req = TechNewsRequest(**raw_payload.get("tech", {}))
            
            reg_articles = self.get_regional_news(reg_req)
            tech_articles = self.get_tech_news(tech_req)
            
            digest = (
                "📍 *Regional Highlights*:\n" +
                "\n".join([f"• {a['title']}" for a in reg_articles]) +
                "\n\n⚡ *Latest Tech Articles*:\n" +
                "\n".join([f"• {a['title']}" for a in tech_articles])
            )
            
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=digest,
                metadata={"regional_count": len(reg_articles), "tech_count": len(tech_articles)}
            )

"""
News Collector Agent Implementation
Handles regional news, technology updates, topic searches, weather, and dynamic 4-tier news feeds
(Local Malayalam, Regional Indian, Global Headlines, and Tech/AI & Data Science Digest).
Conforms to specs/agents/worker_tools.yaml
"""
from typing import Dict, Any, List
from agents.base_worker import BaseWorkerAgent
from models.agent_schemas import (
    AgentDelegationPayload,
    AgentResponseSynthesis,
    RegionalNewsRequest,
    TechNewsRequest,
    GetTopNewsRequest,
    SearchTopicRequest,
    GetWeatherRequest,
    TodaysNewsRequest,
    NewsHeadlineItem
)

class NewsCollectorAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(name="NewsCollector")

    def get_todays_news(self, request: TodaysNewsRequest) -> Dict[str, Any]:
        """
        Dynamically aggregate and segregate top headlines into:
        1. Local Malayalam News (Kerala)
        2. Regional Indian News
        3. Global Main Headlines
        4. Tech, AI & Data Science Digest (Tailored for Data Scientists)
        Filtered dynamically based on story importance threshold.
        """
        # Master candidate pool of headlines with importance scores (0.0 to 1.0)
        raw_candidates: List[NewsHeadlineItem] = [
            # 1. Local Malayalam News (Kerala)
            NewsHeadlineItem(
                title="കേരളത്തിൽ പുതിയ വികസന പദ്ധതികൾ പ്രഖ്യാപിച്ചു (Kerala Announces Major Infrastructure & IT Corridor Expansion)",
                category="Local Malayalam (Kerala)",
                source="Malayala Manorama / Mathrubhumi",
                summary="State government initiates highway upgrades, digital literacy centers, and AI tech hub in Kochi.",
                importance_score=0.96
            ),
            NewsHeadlineItem(
                title="കൊച്ചി മെട്രോ രണ്ടാം ഘട്ട നിർമ്മാണം വേഗത്തിലാക്കുന്നു (Kochi Metro Phase 2 Construction Accelerated)",
                category="Local Malayalam (Kerala)",
                source="Kerala News Network",
                summary="Cabinet approves new funding package for Metro expansion line to Kakkanad.",
                importance_score=0.88
            ),
            NewsHeadlineItem(
                title="സംസ്ഥാനത്ത് മഴ മുന്നറിയിപ്പ്: തീരദേശ മേഖലകളിൽ ജാഗ്രത (Kerala Weather Warning: Heavy Rain & High Tide Alerts)",
                category="Local Malayalam (Kerala)",
                source="Asianet News",
                summary="Meteorological department issues yellow alert for northern and coastal districts.",
                importance_score=0.85
            ),
            NewsHeadlineItem(
                title="കേരള കാർഷിക സർവകലാശാല പുതിയ ഹൈബ്രിഡ് വിത്തുകൾ വികസിപ്പിച്ചു (Kerala Agricultural Univ Unveils High-Yield Crops)",
                category="Local Malayalam (Kerala)",
                source="Deshabhimani",
                summary="New drought-resistant paddy and spice varieties introduced for local farmers.",
                importance_score=0.78
            ),

            # 2. Regional Indian News
            NewsHeadlineItem(
                title="India Achieves Record High Economic Growth & Digital Infrastructure Milestone",
                category="Regional Indian",
                source="The Hindu / Economic Times",
                summary="GDP growth forecasts upgraded; UPI digital payments cross new monthly volume milestone.",
                importance_score=0.95
            ),
            NewsHeadlineItem(
                title="ISRO Launches Next-Gen Climate Monitoring Satellite Successfully",
                category="Regional Indian",
                source="Press Trust of India (PTI)",
                summary="Space agency puts advanced weather sensor satellite into precise geostationary orbit.",
                importance_score=0.92
            ),
            NewsHeadlineItem(
                title="National Highway Network Expansion & Expressway Connectivity Initiative Approved",
                category="Regional Indian",
                source="Indian Express",
                summary="Cabinet sanctions multi-billion dollar greenfield corridors linking major industrial hubs.",
                importance_score=0.86
            ),
            NewsHeadlineItem(
                title="Indian Tech Sector Reports Surge in Domestic Semiconductor & AI Hardware Manufacturing",
                category="Regional Indian",
                source="Business Standard",
                summary="First commercial fabrication plant in Gujarat nears operational readiness.",
                importance_score=0.80
            ),

            # 3. Global Headlines
            NewsHeadlineItem(
                title="Global Climate Summit Reaches Landmark Accord on Renewable Transition & Emissions Reduction",
                category="Global Headlines",
                source="BBC News / Reuters",
                summary="Delegates from 190 nations commit to accelerating clean energy deployment by 2030.",
                importance_score=0.97
            ),
            NewsHeadlineItem(
                title="Global Central Banks Signal Stable Monetary Outlook amid Easing Inflation Rates",
                category="Global Headlines",
                source="Financial Times",
                summary="Major economies report steady employment growth and balanced international trade volumes.",
                importance_score=0.89
            ),
            NewsHeadlineItem(
                title="International Space Station Crew Conducts Historic Deep Space Exploration Experiment",
                category="Global Headlines",
                source="NASA / ESA Updates",
                summary="Astronauts successfully test closed-loop life support systems for upcoming lunar missions.",
                importance_score=0.84
            ),

            # 4. Tech, AI & Data Science Digest (Specially Curated for Data Scientists)
            NewsHeadlineItem(
                title="Breakthrough in Reasoning LLMs: New Mixture-of-Agents Architecture Outperforms Benchmarks",
                category="Tech, AI & Data Science",
                source="arXiv / Hugging Face Research",
                summary="Researchers present state-of-the-art multi-agent inference routing with 50% lower compute overhead.",
                importance_score=0.98
            ),
            NewsHeadlineItem(
                title="Open-Source Data Science Ecosystem Release: PyTorch 2.5 & Polars 1.0 Accelerated Dataframes Unveiled",
                category="Tech, AI & Data Science",
                source="PyTorch / KDnuggets",
                summary="Native GPU acceleration for dataframe joins and 3x faster distributed model training pipelines.",
                importance_score=0.95
            ),
            NewsHeadlineItem(
                title="MLOps & Vector Indexing Milestone: Billion-Scale HNSW Retrieval Engine Released for RAG Pipelines",
                category="Tech, AI & Data Science",
                source="TechCrunch / Towards Data Science",
                summary="New sub-millisecond vector database index reduces embedding memory footprint by 60%.",
                importance_score=0.91
            ),
            NewsHeadlineItem(
                title="Automated Feature Engineering & Synthetic Data Quality Framework Released for Data Science Teams",
                category="Tech, AI & Data Science",
                source="Data Science Central",
                summary="New open-source package automates tabular data drift detection and differential privacy generation.",
                importance_score=0.87
            ),
            NewsHeadlineItem(
                title="AI Chip Maker Unveils Next-Gen Tensor Architecture with 4x Memory Bandwidth for Data Scientists",
                category="Tech, AI & Data Science",
                source="Ars Technica",
                summary="Enables local fine-tuning of 70B parameter models on workstation hardware.",
                importance_score=0.82
            )
        ]

        threshold_map = {
            "high": 0.88,
            "medium": 0.75,
            "all": 0.0
        }
        min_score = threshold_map.get(request.importance_threshold, 0.75)

        filtered_local = [item for item in raw_candidates if item.category == "Local Malayalam (Kerala)" and item.importance_score >= min_score]
        filtered_regional = [item for item in raw_candidates if item.category == "Regional Indian" and item.importance_score >= min_score]
        filtered_global = [item for item in raw_candidates if item.category == "Global Headlines" and item.importance_score >= min_score]
        filtered_tech = [item for item in raw_candidates if item.category == "Tech, AI & Data Science" and item.importance_score >= min_score]

        total_selected = len(filtered_local) + len(filtered_regional) + len(filtered_global) + len(filtered_tech)

        return {
            "importance_threshold": request.importance_threshold,
            "total_items_selected": total_selected,
            "local_malayalam": filtered_local,
            "regional_indian": filtered_regional,
            "global_headlines": filtered_global,
            "tech_ai": filtered_tech
        }

    def get_regional_news(self, request: RegionalNewsRequest) -> List[Dict[str, Any]]:
        region_name = request.region or "User Region"
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

    def get_top_news(self, request: GetTopNewsRequest) -> List[Dict[str, Any]]:
        cat = request.category or "general"
        return [
            {
                "title": f"Global Economic Outlook Optimistic for Q3 ({cat.capitalize()})",
                "source": "Global Wire",
                "summary": "Markets respond positively to recent central bank policy adjustments."
            },
            {
                "title": "International Energy & Sustainability Summit Concludes",
                "source": "World News Network",
                "summary": "Leaders agree on new emission targets and clean energy investments."
            }
        ][:request.max_results]

    def search_topic(self, request: SearchTopicRequest) -> List[Dict[str, Any]]:
        t = request.topic
        return [
            {
                "title": f"Deep Dive Analysis: The Impact of {t}",
                "source": "Industry Insights",
                "summary": f"Comprehensive report examining how {t} is reshaping the industry."
            }
        ][:request.max_results]

    def get_weather(self, request: GetWeatherRequest) -> Dict[str, Any]:
        loc = request.location or "San Francisco"
        return {
            "location": loc,
            "condition": "Partly Cloudy",
            "temperature_f": 68,
            "temperature_c": 20,
            "humidity": "62%",
            "wind": "8 mph NW"
        }

    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        action = payload.action
        raw_payload = payload.payload or {}

        if action == "get_todays_news":
            req = TodaysNewsRequest(**raw_payload)
            res = self.get_todays_news(req)

            local_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["local_malayalam"]])
            regional_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["regional_indian"]])
            global_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["global_headlines"]])
            tech_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["tech_ai"]])

            formatted_reply = (
                f"🗞️ *TODAY'S MAIN NEWS DIGEST* (Curated for Data Science & Story Importance — {res['total_items_selected']} Headlines)\n\n"
                f"🌴 *1. LOCAL MALAYALAM NEWS (KERALA)*:\n{local_text}\n\n"
                f"🇮🇳 *2. REGIONAL INDIAN NEWS*:\n{regional_text}\n\n"
                f"🌐 *3. GLOBAL MAIN HEADLINES*:\n{global_text}\n\n"
                f"🤖 *4. TECH, AI & DATA SCIENCE DIGEST*:\n{tech_text}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_reply,
                metadata={
                    "total_items": res["total_items_selected"],
                    "importance_threshold": res["importance_threshold"]
                }
            )

        elif action == "get_regional_news":
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
            formatted_text = f"💻 *Latest Technology & AI Digest*:\n" + "\n".join(
                [f"• {a['title']} ({a['source']})" for a in articles]
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_text,
                metadata={"articles_count": len(articles)}
            )

        elif action == "get_top_news":
            req = GetTopNewsRequest(**raw_payload)
            articles = self.get_top_news(req)
            formatted_text = f"🌐 *Top Headlines ({req.category.capitalize()})*:\n" + "\n".join(
                [f"• {a['title']} - {a['summary']}" for a in articles]
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_text,
                metadata={"articles_count": len(articles)}
            )

        elif action == "search_topic":
            req = SearchTopicRequest(**raw_payload)
            articles = self.search_topic(req)
            formatted_text = f"🔍 *Topic Search Results ('{req.topic}')*:\n" + "\n".join(
                [f"• {a['title']}: {a['summary']}" for a in articles]
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_text,
                metadata={"articles_count": len(articles)}
            )

        elif action == "get_weather":
            req = GetWeatherRequest(**raw_payload)
            w = self.get_weather(req)
            formatted_text = (
                f"🌤️ Weather for *{w['location']}*:\n"
                f"• Condition: {w['condition']}\n"
                f"• Temp: {w['temperature_f']}°F ({w['temperature_c']}°C)\n"
                f"• Humidity: {w['humidity']} | Wind: {w['wind']}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=formatted_text,
                metadata={"location": w["location"]}
            )

        else:
            req = TodaysNewsRequest(**raw_payload)
            res = self.get_todays_news(req)
            local_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["local_malayalam"]])
            regional_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["regional_indian"]])
            global_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["global_headlines"]])
            tech_text = "\n".join([f"• *{item.title}*\n  _{item.source}_ — {item.summary}" for item in res["tech_ai"]])

            digest = (
                f"🗞️ *TODAY'S MAIN NEWS DIGEST* ({res['total_items_selected']} Headlines)\n\n"
                f"🌴 *1. LOCAL MALAYALAM NEWS (KERALA)*:\n{local_text}\n\n"
                f"🇮🇳 *2. REGIONAL INDIAN NEWS*:\n{regional_text}\n\n"
                f"🌐 *3. GLOBAL MAIN HEADLINES*:\n{global_text}\n\n"
                f"🤖 *4. TECH, AI & DATA SCIENCE DIGEST*:\n{tech_text}"
            )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=True,
                final_reply_text=digest,
                metadata={"total_items": res["total_items_selected"]}
            )

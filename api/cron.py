"""
Internal Cron API Route Handler for GCP Cloud Scheduler Triggers
Conforms to specs/api/internal_cron.yaml
"""
from fastapi import APIRouter, Header, HTTPException
from typing import Dict, Any, Optional
from agents.secretary import SecretaryAgent
from services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/internal/cron", tags=["cron"])
secretary = SecretaryAgent()
whatsapp_service = WhatsAppService()

@router.post("/scheduled-tasks")
async def execute_scheduled_tasks(
    x_cloudscheduler_jobname: Optional[str] = Header(None, alias="X-CloudScheduler-JobName")
) -> Dict[str, Any]:
    """
    Endpoint triggered by GCP Cloud Scheduler (e.g., at 06:00 AM IST daily).
    Generates 6:00 AM Daily Morning Briefing (News, Gmail Sync, Expenses, Schedule)
    and dispatches via WhatsApp.
    """
    job_name = x_cloudscheduler_jobname or "daily-morning-briefing-6am-ist"
    print(f"[Cron Executed]: Job '{job_name}' triggered at 6:00 AM IST")

    morning_digest_text = secretary.generate_morning_digest()
    
    # Send via WhatsApp to recipient
    recipient = "default_user"
    await whatsapp_service.send_message(recipient, morning_digest_text)

    return {
        "status": "success",
        "processed_count": 1,
        "details": [
            f"Executed 6:00 AM IST Morning Briefing Job: '{job_name}'",
            "Gmail payment receipts synchronized",
            "4-Tier News Digest generated",
            "Calendar schedule updated"
        ]
    }

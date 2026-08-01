import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from api import whatsapp, cron

# Ensure stdout and stderr use UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

app = FastAPI(
    title="Personal Assistant API",
    description="Multi-Agent Personal Assistant backend for WhatsApp Bot",
    version="0.1.0",
)

app.include_router(whatsapp.router)
app.include_router(cron.router)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Personal Assistant API is running",
        "configured_user": os.environ.get("GOOGLE_USER_EMAIL", "not_set")
    }

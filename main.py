from fastapi import FastAPI
from api import whatsapp

app = FastAPI(
    title="Personal Assistant API",
    description="Multi-Agent Personal Assistant backend for WhatsApp Bot",
    version="0.1.0",
)

app.include_router(whatsapp.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Personal Assistant API is running"}

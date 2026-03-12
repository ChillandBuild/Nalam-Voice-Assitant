import os
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse

from whatsapp_handler import process_whatsapp_message

app = FastAPI(title="Nalam WhatsApp Webhook")

# Ensure static directory exists for serving audio
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Twilio webhook endpoint for WhatsApp messages.
    Returns 200 fast to avoid timeout, process in background.
    """
    form_data = await request.form()
    
    sender = form_data.get("From", "")
    body = form_data.get("Body", "")
    num_media = int(form_data.get("NumMedia", 0))
    media_url = form_data.get("MediaUrl0", "") if num_media > 0 else ""
    media_type = form_data.get("MediaContentType0", "") if num_media > 0 else ""
    
    # Get the raw base URL purely for constructing static audio file links
    base_url = str(request.base_url).rstrip("/")
    
    # Process message in background to avoid 15s Twilio webhook timeout
    background_tasks.add_task(
        process_whatsapp_message, 
        sender=sender, 
        body=body, 
        num_media=num_media, 
        media_url=media_url, 
        media_type=media_type,
        base_url=base_url
    )
    
    # Send empty response back immediately (Twilio likes this)
    return PlainTextResponse("")

# Run using: uvicorn whatsapp_app:app --reload --port 8000

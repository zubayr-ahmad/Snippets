import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from langchain_groq import ChatGroq
import requests
from time import sleep

# Load environment variables
load_dotenv()
PHONE_ID = os.getenv("PHONE_ID")  # from which phone no, you want to send message
TOKEN = os.getenv("TOKEN")        # Need to get from the app dashboard 
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")    # A random string that you can write anything but need to place it while approving webhook
APP_ID = os.getenv("APP_ID")          # These 2 are available on the platform
APP_SECRET = os.getenv("APP_SECRET")

# Set up LLM
llm = ChatGroq(model="llama3-8b-8192", temperature=0)

# Initialize FastAPI
app = FastAPI()

print(f"Starting WhatsApp bot with Phone ID: {PHONE_ID}")

# Handle webhook verification (GET requests from Meta)
@app.get("/webhook")
@app.get("/webhook/")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """Verify webhook with Meta/WhatsApp"""
    print(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print(f"Webhook verified successfully with challenge: {hub_challenge}")
        return PlainTextResponse(content=hub_challenge)
    print(f"Webhook verification failed. Mode: {hub_mode}, Token: {hub_verify_token}")
    raise HTTPException(status_code=403, detail="Verification failed")

# Handle webhook POST requests (incoming messages)
@app.post("/webhook")
@app.post("/webhook/")
async def webhook_post(request: Request):
    """Handle incoming webhook POST requests from Meta"""
    try:
        body = await request.json()
        print(f"Received webhook data: {json.dumps(body, indent=2)}")
        
        # Check if this is a message event
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        
                        for message in messages:
                            if message.get("type") == "text":
                                await handle_text_message(message, value)
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

async def handle_text_message(message, value):
    """Handle incoming text messages"""
    try:
        from_number = message["from"]
        text_body = message["text"]["body"]
        message_id = message["id"]
        send_typing_indicator(message_id)
        
        
        print(f"Processing message from {from_number}: {text_body}")
        
        # Generate response using LLM
        prompt = [
            ("system", "You are a helpful assistant. Reply in exactly 3 concise sentences."),
            ("human", text_body)
        ]
        
        response = llm.invoke(prompt)
        reply_text = response.content.strip()
        
        # Ensure we have exactly 3 sentences
        sentences = [s.strip() for s in reply_text.split('.') if s.strip()]
        if len(sentences) > 3:
            sentences = sentences[:3]
        reply = '. '.join(sentences) + '.'
        
        print(f"Sending reply: {reply}")
        
        # Send reply using WhatsApp Cloud API
        await send_whatsapp_message(from_number, reply)
        
    except Exception as e:
        print(f"Error handling text message: {e}")
        # Try to send error message
        try:
            await send_whatsapp_message(message["from"], "Sorry, I encountered an error processing your message.")
        except Exception as send_error:
            print(f"Could not send error message: {send_error}")

async def send_whatsapp_message(to_number, message_text):
    """Send a WhatsApp message using the Cloud API"""
    url = f"https://graph.facebook.com/v23.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Message sent successfully to {to_number}")
            return True
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

async def mark_message_as_read(message_id):
    """Mark a message as read"""
    url = f"https://graph.facebook.com/v23.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"Message {message_id} marked as read")
            return True
        else:
            print(f"Failed to mark message as read: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error marking message as read: {e}")
        return False

def send_typing_indicator(message_id):
    print(f"Sending typing indicator to {message_id} and also mark as read")
    url = f"https://graph.facebook.com/v23.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp",
            "status": "read",
             "message_id":message_id,
            "typing_indicator": {
                "type": "text"
            }
        }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Typing indicator sent to {message_id}")
    else:
        print(f"Failed to send typing indicator: {response.status_code} - {response.text}")

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "WhatsApp bot is running!", 
        "phone_id": PHONE_ID,
        "endpoints": ["/webhook", "/webhook/"]
    }

# Debug endpoint to check environment variables
@app.get("/debug")
async def debug_info():
    return {
        "phone_id": PHONE_ID[:10] + "..." if PHONE_ID else "Not set",
        "token": TOKEN[:10] + "..." if TOKEN else "Not set", 
        "verify_token": VERIFY_TOKEN if VERIFY_TOKEN else "Not set",
        "app_id": APP_ID if APP_ID else "Not set"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Run via: uvicorn app:app --reload --host 0.0.0.0 --port 800
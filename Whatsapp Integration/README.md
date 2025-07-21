# WhatsApp Bot (FastAPI + WhatsApp Cloud API)

This project is a WhatsApp chatbot that:
- Connects with **Meta's WhatsApp Cloud API** to receive/send messages.
- Uses LLM to generate AI-powered replies.

## 📋 Features
- Webhook handling for WhatsApp messages.
- Message processing using LLaMA3.
- Typing indicator + mark as read.
- REST endpoints for health checks and debugging.

## 📦 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <repo-url>
cd <repo-directory>
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
Example dependencies:
```txt
fastapi
uvicorn
python-dotenv
requests
langchain_groq
```

### 3️⃣ Environment Variables (`.env`)

Create a `.env` file in the project root and add the following:
```env
PHONE_ID=YOUR_PHONE_ID_HERE
TOKEN=YOUR_WHATSAPP_CLOUD_API_TOKEN
VERIFY_TOKEN=YOUR_CUSTOM_VERIFICATION_TOKEN
APP_ID=YOUR_FACEBOOK_APP_ID
APP_SECRET=YOUR_FACEBOOK_APP_SECRET
```
**Details:**
- `PHONE_ID`: Found in Meta App Dashboard (sending phone number).
- `TOKEN`: Permanent/temporary access token from Meta Developer Dashboard.
- `VERIFY_TOKEN`: Random string set by you; used during webhook setup.
- `APP_ID`: Facebook App ID.
- `APP_SECRET`: Facebook App Secret.

### 4️⃣ Running the Bot
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Your bot will be available at:
- `GET /webhook`: Handles Meta's webhook verification.
- `POST /webhook`: Processes incoming WhatsApp messages.
- `GET /`: Health check endpoint.
- `GET /debug`: Environment variables (masked for safety).

## ⚙️ How It Works

- Meta sends webhook POST requests to `/webhook` when your phone number receives a message.
- If the message is text:
  - The bot uses **LLaMA3 8B (via Groq)** to generate a concise 3-sentence reply.
  - Sends typing indicator + marks message as read.
  - Replies via WhatsApp Cloud API.
- Debugging and health endpoints help in monitoring.

## 📊 Notes
- Ensure webhook URL is public (use [ngrok](https://ngrok.com/) or similar during development).
- Webhook must be verified using `VERIFY_TOKEN` during initial setup in Meta Dashboard.
- Ensure the access token (`TOKEN`) has proper permissions (sending/receiving messages).

## 🛠️ WhatsApp Cloud API Integration Guide

Follow these steps to setup WhatsApp Cloud API with your FastAPI backend:

1. Go to [developers.facebook.com](https://developers.facebook.com/) and create a new app.
2. When prompted, select **Business** app type. Your app must be a **Business** app (not Consumer).
3. After creation, go to **My Apps → Your App**.
4. On the left sidebar, scroll past “App Settings” and click **Add Product** (or “+ Add a Product”).
5. From the list, find **WhatsApp** and click **Set Up**.
6. Once set up, you’ll see **WhatsApp** on the left panel. Go inside **API Setup**.
7. Generate the token and sender phone number.
8. Inside **Recipient**, put your phone number to receive messages. Click **Send** to receive a test message.

**Important Note:**
- You cannot send custom messages until the user sends you a message first.
- Once the user replies, you can send messages freely.

9. To receive incoming messages and process them, set up a **Webhook**:
    - Go to **WhatsApp → Configuration**.
    - Expose your backend using **ngrok** or similar service.
    - Set the webhook callback URL (must end with `/webhook/`).
    - Create a **VERIFY_TOKEN** locally (can be any string) and place it in your `.env` file.
    - Use the same token while configuring the webhook on Meta Dashboard.
    - Under webhook fields, subscribe to **messages** and **message_status**.

10. Get your **APP_ID** and **APP_SECRET** from **App Settings → Basic**.
11. Save **PHONE_ID**, **TOKEN**, **VERIFY_TOKEN**, **APP_ID**, and **APP_SECRET** inside the `.env` file.
12. Run your backend and verify the webhook (Meta will send a challenge request).
13. Once verified, your WhatsApp number is fully integrated.
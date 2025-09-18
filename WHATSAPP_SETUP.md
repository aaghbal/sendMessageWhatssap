# WhatsApp Integration Setup Guide

To make your WhatsApp messages actually send (not just simulate), you need to set up a real WhatsApp API service. Here are your options:

## Option 1: Twilio WhatsApp API (Recommended - Easy Setup)

### Step 1: Get Twilio Credentials
1. Go to [Twilio Console](https://console.twilio.com/)
2. Create a free account or log in
3. Copy your **Account SID** and **Auth Token** from the dashboard

### Step 2: Set up WhatsApp Sandbox (Free Testing)
1. Go to [Twilio WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Follow the instructions to join the sandbox:
   - Send a WhatsApp message to **+1 415 523 8886**
   - Include the code they provide (like "join <your-code>")
3. Once connected, you can send messages to any number that has joined your sandbox

### Step 3: Update Backend Configuration
Edit `/backend/.env` file:

```env
# Replace these with your actual Twilio credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+14155238886
```

### Step 4: Test the Integration
1. Make sure both frontend and backend are running:
   ```bash
   # Terminal 1 - Backend
   cd backend && python manage.py runserver
   
   # Terminal 2 - Frontend  
   cd frontend && npm start
   ```

2. Open http://localhost:3000
3. Go to "Send Messages" in the sidebar
4. Add a phone number that has joined your Twilio sandbox
5. Compose a message and send!

## Option 2: Official WhatsApp Business API (Production)

For production use with unlimited numbers:
1. Apply for [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
2. Get approved by Meta
3. Update the backend service to use official API endpoints

## Option 3: WhatsApp Web Automation (Alternative)

If you prefer browser automation (like your `sc.py` script):
1. The backend can be modified to use selenium with WhatsApp Web
2. This requires keeping a browser session active
3. Less reliable but works without API approval

## Current Status

✅ **Backend**: Configured with Twilio WhatsApp API
✅ **Frontend**: Connected to real backend API  
✅ **Bulk Messaging**: Supports sending to multiple numbers
⚠️ **Credentials**: Need to add your Twilio credentials to `.env`

## Testing Checklist

- [ ] Added Twilio credentials to backend `.env`
- [ ] Joined Twilio WhatsApp sandbox with your phone
- [ ] Backend server running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Tested sending a message to your sandbox number

## Troubleshooting

**Error: "Twilio credentials not configured"**
- Make sure you've added real credentials to `/backend/.env`
- Restart the backend server after updating `.env`

**Error: "Message failed to send"**
- Ensure the recipient number has joined your Twilio sandbox
- Check the phone number format (+1234567890)
- Check backend logs for detailed error messages

**Messages not received**
- Twilio sandbox has limitations - only numbers that joined can receive messages  
- For production, you need approved WhatsApp Business API
- Check Twilio console logs for delivery status

## Next Steps

1. **Get Twilio credentials** and update the `.env` file
2. **Join the sandbox** with your phone number  
3. **Test sending messages** through the web interface
4. **Apply for production API** when ready to send to any number

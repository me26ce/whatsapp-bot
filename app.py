from flask import Flask, request
import os
from google import genai
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '')

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=incoming_msg
    )

    reply = response.text

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

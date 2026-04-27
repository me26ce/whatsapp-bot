from flask import Flask, request
import os
import google.generativeai as genai
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
mmodel = genai.GenerativeModel("gemini-1.5-flash-latest")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '')

    response = model.generate_content(incoming_msg)
    reply = response.text

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

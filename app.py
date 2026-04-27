from flask import Flask, request
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

HF_API = os.environ.get("HF_API_KEY")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg = request.values.get('Body', '')

    response = requests.post(
        "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
        headers={"Authorization": f"Bearer {HF_API}"},
        json={"inputs": msg}
    )

    try:
        reply = response.json()[0]['generated_text']
    except:
        reply = "Şu an cevap üretemiyorum."

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

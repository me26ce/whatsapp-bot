from flask import Flask, request
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_PROMPT = (
    "Sen Türkçe konuşan bir WhatsApp kişisel asistanısın. "
    "Kısa, doğal ve anlaşılır cevap ver. Gereksiz İngilizce kullanma."
)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg = request.values.get('Body', '')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key="

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\nKullanıcı: " + msg}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)

    try:
        data = response.json()

        reply = data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        if "error" in data:
            reply = f"API ERROR: {data['error']['message']}"
        elif "candidates" in data:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            reply = f"Bilinmeyen response: {data}"

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

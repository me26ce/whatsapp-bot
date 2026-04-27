from flask import Flask, request
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

GROQ_API = os.environ.get("GROQ_API_KEY")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg = request.values.get('Body', '')

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "user", "content": msg}
                ]
            },
            timeout=20
        )

        data = response.json()

        # 🔍 DEBUG için ham response kontrolü
        if response.status_code != 200:
            reply = f"API HATA: {data}"
        else:
            reply = data['choices'][0]['message']['content']

    except Exception as e:
        reply = f"SYSTEM HATA: {str(e)}"

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

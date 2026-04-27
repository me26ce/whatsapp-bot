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
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        headers={"Authorization": f"Bearer {HF_API}"},
        json={"inputs": msg}
    )

    try:
        data = response.json()

        # güvenli parse
        if isinstance(data, list) and "generated_text" in data[0]:
            reply = data[0]["generated_text"]
        elif isinstance(data, dict) and "error" in data:
            reply = "Model yükleniyor, tekrar dene."
        else:
            reply = str(data)

    except:
        reply = "Şu an cevap veremiyorum."

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

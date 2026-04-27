from flask import Flask, request
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

GROQ_API = os.environ.get("GROQ_API_KEY")

# 🧠 BASİT HAFIZA (RAM)
memory = {}

SYSTEM_PROMPT = (
   "Sen profesyonel bir Türkçe kişisel asistansın. İnsan gibi konuş, kısa ama zeki cevap ver, gereksiz açıklama yapma."
)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg = request.values.get('Body', '')
    user_id = request.values.get('From', '')

    # 🧠 memory başlat
    if user_id not in memory:
        memory[user_id] = []

    # son mesajları tut
    memory[user_id].append(msg)
    history = memory[user_id][-5:]  # son 5 mesaj

    # Groq API çağrısı
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-70b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT + f"\nSon konuşmalar: {history}"},
                {"role": "user", "content": msg}
            ]
        },
        timeout=20
    )

    try:
        data = response.json()
        reply = data['choices'][0]['message']['content']
    except:
        reply = "Şu an cevap veremiyorum."

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

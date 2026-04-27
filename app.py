from flask import Flask, request
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

client = OpenAI(api_key="sk-xxxxx")
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '')

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": incoming_msg}]
    )

    reply = response.choices[0].message.content

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

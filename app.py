from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import feedparser
import sqlite3
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

# -------------------------
# API KEYS
# -------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# -------------------------
# DB
# -------------------------
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    user TEXT,
    key TEXT,
    value TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chatlog (
    user TEXT,
    message TEXT
)
""")

conn.commit()

# -------------------------
# MEMORY
# -------------------------
def set_memory(user, key, value):
    cursor.execute(
        "REPLACE INTO memory (user, key, value) VALUES (?, ?, ?)",
        (user, key, value)
    )
    conn.commit()

def get_memory(user, key):
    cursor.execute(
        "SELECT value FROM memory WHERE user=? AND key=?",
        (user, key)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def add_chat(user, msg):
    cursor.execute(
        "INSERT INTO chatlog (user, message) VALUES (?, ?)",
        (user, msg)
    )
    conn.commit()

def get_history(user):
    cursor.execute(
        "SELECT message FROM chatlog WHERE user=? ORDER BY rowid DESC LIMIT 6",
        (user,)
    )
    rows = cursor.fetchall()
    return [r[0] for r in rows][::-1]

# -------------------------
# WEATHER
# -------------------------
def get_weather(city="Ankara"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=tr"
    r = requests.get(url).json()

    if r.get("main"):
        temp = r["main"]["temp"]
        desc = r["weather"][0]["description"]
        return f"{city}: {temp}°C, {desc}"
    return "Hava alınamadı."

# -------------------------
# NEWS
# -------------------------
def get_news():
    feed = feedparser.parse("https://www.aa.com.tr/tr/rss/default?cat=guncel")
    return [e.title for e in feed.entries[:5]]

def summarize_news(news):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": "Türkiye gündemini özetle:\n" + "\n".join(news)}]}
        ]
    }

    r = requests.post(url, json=payload).json()

    try:
        return r["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Haber alınamadı."

# -------------------------
# AI
# -------------------------
def call_ai(msg, history, name):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
Sen Türkçe kişisel asistansın.

Kullanıcı adı: {name}

Geçmiş:
{history}

Mesaj:
{msg}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    r = requests.post(url, json=payload).json()

    try:
        return r["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Cevap üretilemedi."

# -------------------------
# ROUTER
# -------------------------
def route(msg):
    m = msg.lower()

    if "benim adım" in m:
        return "name"

    if "not al" in m:
        return "note"

    if "notlarım" in m:
        return "get_notes"

    if "haber" in m:
        return "news"

    if "hava" in m:
        return "weather"

    if "saat" in m:
        return "time"

    return "ai"

# -------------------------
# WHATSAPP
# -------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.values.get("Body", "")
    user = request.values.get("From", "")

    add_chat(user, msg)

    history = get_history(user)
    name = get_memory(user, "name")

    action = route(msg)

    # NAME
    if action == "name":
        n = msg.replace("benim adım", "").strip()
        set_memory(user, "name", n)
        reply = f"Tamam {n}, hatırladım 👍"

    # NOTE
    elif action == "note":
        set_memory(user, "note", msg)
        reply = "Not aldım 👍"

    elif action == "get_notes":
        note = get_memory(user, "note")
        reply = note if note else "Not yok."

    # NEWS
    elif action == "news":
        reply = "📰 Türkiye Gündemi:\n\n" + summarize_news(get_news())

    # WEATHER
    elif action == "weather":
        city = "Ankara"
        for w in msg.split():
            if w.istitle():
                city = w
        reply = get_weather(city)

    # TIME
    elif action == "time":
        reply = "Şu an saat: " + datetime.now().strftime("%H:%M")

    # AI
    else:
        reply = call_ai(msg, "\n".join(history), name)

    twilio = MessagingResponse()
    twilio.message(reply)

    return str(twilio)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

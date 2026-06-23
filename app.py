import os
import requests
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN      = os.environ.get("VERIFY_TOKEN", "phonehouse_bot_2026")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """သင်သည် Phone House Myanmar ၏ Facebook page assistant ဖြစ်သည်။
Phone House သည် Mandalay တွင် တည်ရှိသော Audio နှင့် Tech ဆိုင်ဖြစ်သည်။

ကုန်ပစ္စည်းများ:
- JBL Speakers: Charge 6, Flip 7, PartyBox 310, PartyBox 520
- JBL Headphones: Tune 770NC နှင့် အခြားများ
- Wireless Microphones
- Second-hand iPhones နှင့် Smartphones

ဆိုင်အချက်အလက်:
- တည်နေရာ: 69th Street, 35th နှင့် 36th ကြား, Mandalay
- ဖုန်း: 09666555288
- Delivery: Mandalay အတွင်း ရနိုင်သည်။ တစ်ပြည်နယ်လုံး Bus ပို့ဆောင်မှု ရှိသည်။

စည်းမျဉ်းများ:
1. မြန်မာဘာသာ အဓိက ဖြေဆိုပါ။ Customer က English ဖြင့် မေးလျှင် English ဖြင့် ပြန်ဖြေပါ။
2. ဈေးနှုန်း မေးလျှင် — "ဈေးနှုန်း အတိအကျ သိရှိရန် 09666555288 သို့ ဆက်သွယ်ပေးပါ" ဟု ပြောပါ။
3. Stock မေးလျှင် — "Stock စစ်ဆေးပြီး မကြာမီ ဖြေပေးပါမည်" ဟု ပြောပါ။
4. Order လုပ်လိုလျှင် — အမည်၊ လိပ်စာ၊ ဖုန်းနံပါတ် မေးပါ။
5. Complaint ဖြစ်လျှင် — "ဝမ်းနည်းပါသည်၊ ကျွန်တော်တို့ team သို့ ချက်ချင်း report တင်ပေးပါမည်" ဟု ပြောပါ။
6. မသိသော မေးခွန်းများ — "ဆိုင်သို့ တိုက်ရိုက် ဆက်သွယ်ပေးပါ: 09666555288" ဟု ပြောပါ။
7. Response တိုတိုရှင်းရှင်း — 3 ကြောင်းထက် မပိုစေပါနှင့်။
8. Emoji အနည်းငယ် သုံးနိုင်သည်၊ သို့သော် အများကြီး မသုံးပါနှင့်။"""

# Per-user conversation history (resets when server restarts)
conversations = {}

def get_reply(sender_id, user_message):
    if sender_id not in conversations:
        conversations[sender_id] = []

    conversations[sender_id].append({"role": "user", "content": user_message})

    # Keep last 10 messages to save tokens
    history = conversations[sender_id][-10:]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=200,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq error: {e}")
        reply = "ကျေးဇူးပြု၍ ခဏစောင့်ပါ၊ မကြာမီ ဆက်သွယ်ပေးပါမည်။ 📞 09666555288"

    conversations[sender_id].append({"role": "assistant", "content": reply})
    return reply


def send_typing(recipient_id):
    requests.post(
        "https://graph.facebook.com/v19.0/me/messages",
        params={"access_token": PAGE_ACCESS_TOKEN},
        json={"recipient": {"id": recipient_id}, "sender_action": "typing_on"}
    )


def send_message(recipient_id, text):
    r = requests.post(
        "https://graph.facebook.com/v19.0/me/messages",
        params={"access_token": PAGE_ACCESS_TOKEN},
        json={
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE"
        }
    )
    if r.status_code != 200:
        print(f"FB send error: {r.status_code} {r.text}")


# ── Webhook verification ────────────────────────────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified")
        return challenge, 200
    return "Forbidden", 403


# ── Incoming messages ───────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data or data.get("object") != "page":
        return "OK", 200

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            if not sender_id:
                continue
            if event.get("message", {}).get("is_echo"):
                continue

            text = event.get("message", {}).get("text", "").strip()
            if not text:
                continue

            print(f"📩 [{sender_id}]: {text}")
            send_typing(sender_id)
            reply = get_reply(sender_id, text)
            send_message(sender_id, reply)
            print(f"📤 Bot: {reply}")

    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    return "Phone House Messenger Bot ✅ Running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, port=port, host="0.0.0.0")

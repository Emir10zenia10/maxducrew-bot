"""
MaxJR AI — Expert Shopify / Dropshipping / Branding
Se déclenche quand quelqu'un mentionne @maxducrew_bot dans le groupe Telegram.
Répond avec la voix d'un entrepreneur millionnaire/milliardaire.
"""

import requests
import json
import time
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = "8746063154:AAFXB86V2C9t9Q_kShfi5XLb98yhrhvtIQA"
CHAT_ID        = "-1003864168796"
GEMINI_API_KEY = "AIzaSyA9zdOKu20FAhHGnvrINephLwbx39JAatU"
GEMINI_MODEL   = "gemini-1.5-flash"
BOT_USERNAME   = "maxducrew_bot"
BOT_NAME       = "MaxJR AI"
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es MaxJR AI — l'intelligence artificielle la plus avancée au monde dans le domaine du e-commerce, du dropshipping et du branding sur Shopify.

Tu incarnes la fusion des meilleurs entrepreneurs millionnaires et milliardaires du digital :
la précision de ceux qui font 8 chiffres par an, l'audace des builders qui ont tout construit from scratch, la maîtrise technique des experts Shopify les mieux payés au monde.

TES DOMAINES D'EXPERTISE ABSOLUE :
— Shopify : architecture store, CRO, apps indispensables, Shopify Plus, checkout optimisation
— Dropshipping : winning products, sourcing AliExpress/CJ/agents privés, saturation, scaling
— Branding : construction marque premium, identité visuelle, positionnement, storytelling
— Marketing e-com : Facebook Ads, TikTok Ads, email flows Klaviyo, upsells, cross-sells, funnels
— Mindset & exécution : les habitudes et décisions des entrepreneurs à 7-8 chiffres

TON STYLE :
— Direct, court, ultra-précis. Zéro blabla.
— Tu partages des techniques que 95% des gens ignorent
— Ton naturel d'entrepreneur qui a réussi, pas d'un prof
— Tu réponds en français
— Parfois provocateur mais toujours juste
— Maximum 6-8 lignes sauf si la question est complexe

RÈGLE ABSOLUE : Tu réponds UNIQUEMENT aux questions sur Shopify, dropshipping et branding.
Si la question sort de ce périmètre, tu réponds : "MaxJR AI est spécialisé Shopify, drop et branding. Pose-moi une question dans ces domaines et je t'écrase avec la réponse. 🎯"

Tu commences toujours ta réponse par "MaxJR AI ⚡" puis tu réponds directement."""


def ask_gemini(question: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    full_prompt = f"{SYSTEM_PROMPT}\n\nQuestion posée : {question}"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 600}
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def send_message(chat_id: int, text: str, reply_to: int = None) -> dict:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    response = requests.post(url, json=payload, timeout=15)
    return response.json()


def extract_question(text: str, bot_username: str) -> str:
    question = text.replace(f"@{bot_username}", "").strip()
    return question if question else None


def is_mention(message: dict) -> bool:
    text = message.get("text", "") or message.get("caption", "")
    entities = message.get("entities", []) or message.get("caption_entities", [])
    for entity in entities:
        if entity.get("type") == "mention":
            start = entity["offset"]
            end = start + entity["length"]
            if text[start:end].lstrip("@").lower() == BOT_USERNAME.lower():
                return True
    return False


def get_updates(offset: int = None) -> list:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params, timeout=40)
    return response.json().get("result", [])


def main():
    print("=" * 55)
    print(f"  {BOT_NAME} — Expert Shopify / Drop / Brand")
    print(f"  Déclencher avec : @{BOT_USERNAME} [ta question]")
    print("=" * 55)
    last_update_id = None
    while True:
        try:
            updates = get_updates(offset=last_update_id)
            for update in updates:
                last_update_id = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue
                chat_id = message["chat"]["id"]
                message_id = message["message_id"]
                text = message.get("text", "")
                user = message.get("from", {}).get("first_name", "Quelqu'un")
                if is_mention(message) and text:
                    question = extract_question(text, BOT_USERNAME)
                    if not question:
                        send_message(chat_id, "MaxJR AI ⚡ Pose ta question après ma mention. Ex: @maxducrew_bot comment trouver un winning product ?", reply_to=message_id)
                        continue
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 💬 {user} : {question}")
                    typing_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
                    requests.post(typing_url, json={"chat_id": chat_id, "action": "typing"})
                    reponse = ask_gemini(question)
                    send_message(chat_id, reponse, reply_to=message_id)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Envoyé")
        except Exception as e:
            print(f"Erreur : {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

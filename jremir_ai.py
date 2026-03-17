"""
MaxJR AI — Expert Shopify / Dropshipping / Branding
Deux modes :
  1. RÉACTIF  : répond quand quelqu'un mentionne @maxducrew_bot
  2. PROACTIF : pousse des insights e-com automatiquement à heures aléatoires
Propulsé par Groq (Llama 3.3 70B) — ultra-rapide, gratuit
"""

import os
import requests
import time
import random
import threading
from datetime import datetime, timedelta

# ─── CONFIG ───────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID          = "-1003864168796"
GROQ_API_KEY     = os.environ.get("GROQ_API_KEY", "")
BOT_USERNAME     = "maxducrew_bot"
BOT_NAME         = "MaxJR AI"
GROQ_MODEL       = "llama-3.3-70b-versatile"

# Scheduling proactif
MESSAGES_PAR_JOUR = 2        # Nombre d'insights e-com envoyés par jour
HEURE_DEBUT       = 9        # Pas avant 9h
HEURE_FIN         = 22       # Pas après 22h
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_EXPERT = """Tu es MaxJR AI — l'intelligence artificielle la plus avancée au monde dans le domaine du e-commerce, du dropshipping et du branding sur Shopify.

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
Si la question sort de ce périmètre : "MaxJR AI est spécialisé Shopify, drop et branding. Pose-moi une question dans ces domaines et je t'écrase avec la réponse. 🎯"

Tu commences toujours ta réponse par "MaxJR AI ⚡" puis tu réponds directement."""

SYSTEM_PROACTIF = """Tu es MaxJR AI, expert e-commerce millionnaire.

Génère UN message court et percutant pour le groupe Telegram THE CREW — une communauté d'entrepreneurs e-commerce.

Le message doit contenir UNE information ou insight business concret parmi :
— Une tendance produit qui explose en ce moment (Europe ou US)
— Un marché Shopify en forte croissance ou en déclin
— Une technique de conversion, de scaling ou de sourcing que peu de gens connaissent
— Une stat ou donnée e-com récente et actionnable
— Un conseil mindset d'entrepreneur à 7-8 chiffres lié à l'e-com

STYLE :
— 2-4 lignes maximum
— Français, direct, humain, pas corporate
— 1-2 emojis max
— Percutant comme ces exemples :
  "Le marché des produits pour animaux explose en Europe 🐾 Ceux qui ont lancé leur store pet care en Q4 vont encaisser en Q1."
  "TikTok Shop arrive en France. Dans 6 mois ce sera trop tard pour les early adopters. T'es prêt ? 📱"
  "Un store Shopify sans upsell post-achat laisse 30% de revenus sur la table. C'est mathématique."
  "Les gagnants du drop en 2025 sourcent via des agents privés. AliExpress c'est fini pour scaler."

Génère UNIQUEMENT le message. Pas de titre, pas d'explication, pas de guillemets."""


def ask_groq(system: str, user_message: str) -> str:
    """Appel Groq API."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.85,
        "max_tokens": 600
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def send_message(chat_id: int, text: str, reply_to: int = None) -> dict:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    response = requests.post(url, json=payload, timeout=15)
    return response.json()


def extract_question(text: str) -> str:
    question = text.replace(f"@{BOT_USERNAME}", "").strip()
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


# ─── MODE PROACTIF ─────────────────────────────────────────────────────────────
def push_ecom_insight():
    """Génère et envoie un insight e-com proactif dans le groupe."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Génération insight e-com...")
    message = ask_groq(SYSTEM_PROACTIF, "Génère un insight e-com percutant pour aujourd'hui.")
    result = send_message(int(CHAT_ID), message)
    if result.get("ok"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Insight envoyé : {message[:80]}...")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erreur envoi : {result}")


def scheduler_proactif():
    """Thread séparé qui gère l'envoi proactif à heures aléatoires."""
    while True:
        now = datetime.now()
        horaires = []
        for _ in range(MESSAGES_PAR_JOUR):
            h = random.randint(HEURE_DEBUT, HEURE_FIN - 1)
            m = random.randint(0, 59)
            envoi = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if envoi < now:
                envoi += timedelta(days=1)
            horaires.append(envoi)
        horaires.sort()

        print(f"\n📅 Prochains insights proactifs :")
        for h in horaires:
            print(f"   → {h.strftime('%d/%m/%Y à %H:%M')}")

        for horaire in horaires:
            attente = (horaire - datetime.now()).total_seconds()
            if attente > 0:
                time.sleep(attente)
            try:
                push_ecom_insight()
            except Exception as e:
                print(f"Erreur insight proactif : {e}")

        # Attendre le lendemain matin
        demain = datetime.now().replace(hour=HEURE_DEBUT, minute=0, second=0) + timedelta(days=1)
        time.sleep((demain - datetime.now()).total_seconds())


# ─── MODE RÉACTIF ──────────────────────────────────────────────────────────────
def listener_reactif():
    """Thread principal : écoute les mentions et répond."""
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
                    question = extract_question(text) 
                    if not question:
                        send_message(chat_id, "MaxJR AI ⚡ Pose ta question après ma mention. Ex: @maxducrew_bot comment scaler un store Shopify ?", reply_to=message_id)
                        continue
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 💬 {user} : {question}")
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})
                    reponse = ask_groq(SYSTEM_EXPERT, question)
                    send_message(chat_id, reponse, reply_to=message_id)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Réponse envoyée")
        except Exception as e:
            print(f"Erreur listener : {e}")
            time.sleep(5)


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print(f"  {BOT_NAME} — Expert Shopify / Drop / Brand")
    print(f"  Mode RÉACTIF  : @{BOT_USERNAME} [question]")
    print(f"  Mode PROACTIF : {MESSAGES_PAR_JOUR} insights/jour entre {HEURE_DEBUT}h-{HEURE_FIN}h")
    print(f"  Propulsé par Groq 🚀")
    print("=" * 55)

    # Lancer le scheduler proactif dans un thread séparé
    t = threading.Thread(target=scheduler_proactif, daemon=True)
    t.start()

    # Lancer le listener réactif (thread principal)
    listener_reactif()


if __name__ == "__main__":
    main()

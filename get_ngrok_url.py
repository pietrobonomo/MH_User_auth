#!/usr/bin/env python3
"""
Script per ottenere l'URL pubblico di ngrok e mostrare la configurazione webhook.
"""

import httpx
import json

def get_ngrok_url():
    try:
        response = httpx.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        data = response.json()
        
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "https":
                public_url = tunnel.get("public_url")
                webhook_url = f"{public_url}/core/v1/billing/webhook"
                
                print("🌐 ngrok Tunnel Attivo!")
                print(f"📡 URL Webhook: {webhook_url}")
                print("\n📋 Configurazione LemonSqueezy:")
                print(f"   - URL: {webhook_url}")
                print("   - Eventi: order_created, subscription_created, subscription_payment_success")
                print("   - Signing Secret: (usa quello del .env di InsightDesk)")
                print("\n🔗 Dashboard: https://app.lemonsqueezy.com/settings/webhooks")
                return webhook_url
                
    except Exception as e:
        print(f"❌ Errore: {e}")
        print("Assicurati che ngrok sia attivo: ngrok http 5050")
        return None

if __name__ == "__main__":
    get_ngrok_url()

#!/usr/bin/env python3
"""
Test della chiamata API per il form pubblico con impersonificazione admin.

Verifica che la configurazione X-Admin-Key + _as_user_id funzioni correttamente.
"""

import httpx
import json
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# Configurazione
FLOWSTARTER_URL = os.environ.get("FLOWSTARTER_URL", "https://flowstarter-production.up.railway.app")
ADMIN_KEY = os.environ.get("CORE_ADMIN_KEY")
TECHNICAL_USER_UUID = "6dff85ac-2265-4cfa-a2c0-a169401fed47"
APP_ID = "smart_contact_form"

def test_public_form_call():
    """Test chiamata API con impersonificazione admin."""
    
    print("🧪 Test chiamata form pubblico con FlowStarter\n")
    print(f"📡 Endpoint: {FLOWSTARTER_URL}/core/v1/providers/flowise/execute")
    print(f"🔑 Admin Key: {ADMIN_KEY[:10]}...")
    print(f"👤 User UUID: {TECHNICAL_USER_UUID}")
    print(f"📱 App ID: {APP_ID}\n")
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": ADMIN_KEY,
        "X-App-Id": APP_ID
    }
    
    # Body
    payload = {
        "flow_key": "smart_contact",
        "data": {
            "input": "Ciao, questo è un test dal form pubblico. Puoi rispondermi?",
            "_as_user_id": TECHNICAL_USER_UUID
        }
    }
    
    print("📤 Invio richiesta...\n")
    print(f"Headers: {json.dumps({k: v[:20] + '...' if k == 'X-Admin-Key' else v for k, v in headers.items()}, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{FLOWSTARTER_URL}/core/v1/providers/flowise/execute",
                headers=headers,
                json=payload
            )
        
        print(f"📥 Risposta ricevuta: HTTP {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESSO!\n")
            print("Risposta completa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if "result" in result and "text" in result["result"]:
                print(f"\n💬 Testo risposta bot:\n{result['result']['text']}")
            
            return True
            
        else:
            print(f"❌ ERRORE: HTTP {response.status_code}\n")
            print("Body risposta:")
            try:
                error_json = response.json()
                print(json.dumps(error_json, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            
            return False
            
    except Exception as e:
        print(f"❌ ERRORE durante la richiesta: {e}")
        return False


def test_affordability_check():
    """Test pre-check affordability per l'app."""
    
    print("\n" + "="*60)
    print("🔍 Test pre-check affordability\n")
    
    headers = {
        "X-Admin-Key": ADMIN_KEY,
        "X-App-Id": APP_ID
    }
    
    params = {
        "flow_key": "smart_contact",
        "as_user_id": TECHNICAL_USER_UUID
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{FLOWSTARTER_URL}/core/v1/providers/flowise/affordability-check",
                headers=headers,
                params=params
            )
        
        print(f"📥 Risposta: HTTP {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Affordability check:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("can_afford"):
                print("\n✅ L'utente può eseguire il flow")
            else:
                print(f"\n⚠️ Crediti insufficienti:")
                print(f"   Disponibili: {result.get('available_credits', 0)}")
                print(f"   Richiesti: {result.get('required_credits', 0)}")
            
        else:
            print(f"❌ ERRORE: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERRORE: {e}")


def verify_user_openrouter_key():
    """Verifica che l'utente tecnico abbia la chiave OpenRouter."""
    
    print("\n" + "="*60)
    print("🔑 Verifica chiave OpenRouter utente tecnico\n")
    
    headers = {
        "X-Admin-Key": ADMIN_KEY
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{FLOWSTARTER_URL}/core/v1/admin/users",
                headers=headers,
                params={"q": "pietro"}
            )
        
        if response.status_code == 200:
            result = response.json()
            users = result.get("users", [])
            
            for user in users:
                if user.get("id") == TECHNICAL_USER_UUID:
                    print(f"✅ Utente trovato: {user.get('email')}")
                    print(f"   UUID: {user.get('id')}")
                    print(f"   Crediti: {user.get('credits', 0)}")
                    
                    openrouter_key = user.get("openrouter_api_key")
                    if openrouter_key:
                        print(f"   ✅ OpenRouter key: {openrouter_key[:20]}...")
                    else:
                        print(f"   ❌ OpenRouter key: MANCANTE")
                        print("\n⚠️ L'utente non ha una chiave OpenRouter provisionata!")
                        print("   Esegui il provisioning con:")
                        print(f"   POST {FLOWSTARTER_URL}/admin/v1/provision-openrouter")
                    
                    return
            
            print(f"⚠️ Utente con UUID {TECHNICAL_USER_UUID} non trovato")
            
        else:
            print(f"❌ ERRORE: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERRORE: {e}")


if __name__ == "__main__":
    print("="*60)
    print("🧪 TEST INTEGRAZIONE FORM PUBBLICO")
    print("="*60 + "\n")
    
    if not ADMIN_KEY:
        print("❌ ERRORE: CORE_ADMIN_KEY non configurato nel .env")
        exit(1)
    
    # 1. Verifica chiave OpenRouter
    verify_user_openrouter_key()
    
    # 2. Test affordability
    test_affordability_check()
    
    # 3. Test chiamata flow
    print("\n" + "="*60)
    success = test_public_form_call()
    
    print("\n" + "="*60)
    if success:
        print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO")
    else:
        print("❌ ALCUNI TEST FALLITI")
    print("="*60)

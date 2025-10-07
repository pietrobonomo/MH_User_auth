#!/usr/bin/env python3
"""
Test per flow conversazionali con gestione session_id.

Verifica che:
1. Il flow possa essere configurato come conversazionale
2. Le chiamate successive mantengano il contesto usando session_id
3. Senza session_id si crei una nuova conversazione
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
FLOW_KEY = "smart_contact"

def configure_flow_as_conversational():
    """Configura il flow come conversazionale tramite API admin."""
    
    print("🔧 Step 1: Configurazione flow come conversazionale\n")
    
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": ADMIN_KEY
    }
    
    payload = {
        "app_id": APP_ID,
        "flow_key": FLOW_KEY,
        "flow_id": "74f8532c-cc6a-428d-82c8-be622591fc64",  # ID reale dal test precedente
        "node_names": ["agentAgentflow_0"],
        "is_conversational": True  # ✅ Abilita conversazione
    }
    
    print(f"📤 POST {FLOWSTARTER_URL}/core/v1/admin/flow-configs")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{FLOWSTARTER_URL}/core/v1/admin/flow-configs",
                headers=headers,
                json=payload
            )
        
        if response.status_code in (200, 201):
            print("✅ Flow configurato come conversazionale\n")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Errore: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False


def send_message(message: str, session_id: str = None):
    """Invia un messaggio al bot."""
    
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": ADMIN_KEY,
        "X-App-Id": APP_ID
    }
    
    payload = {
        "flow_key": FLOW_KEY,
        "data": {
            "input": message,
            "_as_user_id": TECHNICAL_USER_UUID
        }
    }
    
    # Aggiungi session_id se fornito (conversazione esistente)
    if session_id:
        payload["session_id"] = session_id
        print(f"🔗 Usando session_id esistente: {session_id}\n")
    else:
        print("🆕 Nuova conversazione (no session_id)\n")
    
    print(f"💬 Messaggio: {message}")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{FLOWSTARTER_URL}/core/v1/providers/flowise/execute",
                headers=headers,
                json=payload
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Estrai informazioni dalla risposta
            bot_response = result.get("result", {}).get("text", "")
            flow_info = result.get("flow", {})
            returned_session_id = flow_info.get("session_id")
            is_conversational = flow_info.get("is_conversational", False)
            
            print(f"✅ Risposta ricevuta")
            print(f"   Conversazionale: {is_conversational}")
            print(f"   Session ID: {returned_session_id}")
            print(f"   Risposta bot: {bot_response[:200]}...\n")
            
            return {
                "success": True,
                "bot_response": bot_response,
                "session_id": returned_session_id,
                "is_conversational": is_conversational
            }
        else:
            print(f"❌ Errore: {response.status_code}")
            print(response.text)
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        return {"success": False}


def test_conversation():
    """Test completo di una conversazione multi-turno."""
    
    print("="*60)
    print("🧪 TEST CONVERSAZIONE MULTI-TURNO")
    print("="*60 + "\n")
    
    # Step 1: Configura flow come conversazionale
    if not configure_flow_as_conversational():
        print("\n❌ Impossibile configurare il flow. Test interrotto.")
        return
    
    print("\n" + "="*60)
    print("💬 CONVERSAZIONE 1: Primo messaggio")
    print("="*60 + "\n")
    
    # Step 2: Invia primo messaggio (crea nuova sessione)
    result1 = send_message("Ciao, il mio nome è Marco e ho bisogno di aiuto con un ordine.")
    
    if not result1["success"]:
        print("\n❌ Test fallito al primo messaggio")
        return
    
    session_id = result1["session_id"]
    
    if not session_id:
        print("\n⚠️ WARNING: session_id non ritornato. Il flow potrebbe non essere conversazionale.")
        return
    
    print("\n" + "="*60)
    print("💬 CONVERSAZIONE 1: Secondo messaggio (stessa sessione)")
    print("="*60 + "\n")
    
    # Step 3: Invia secondo messaggio nella stessa sessione
    result2 = send_message(
        "Ti ricordi come mi chiamo?",
        session_id=session_id  # ✅ Usa stesso session_id
    )
    
    if not result2["success"]:
        print("\n❌ Test fallito al secondo messaggio")
        return
    
    # Step 4: Verifica che il bot ricordi il contesto
    bot_response_2 = result2["bot_response"].lower()
    if "marco" in bot_response_2:
        print("\n✅ SUCCESS: Il bot ricorda il nome dalla conversazione precedente!")
    else:
        print("\n⚠️ WARNING: Il bot non sembra ricordare il contesto.")
        print(f"   Risposta: {result2['bot_response']}")
    
    print("\n" + "="*60)
    print("💬 CONVERSAZIONE 2: Nuova sessione indipendente")
    print("="*60 + "\n")
    
    # Step 5: Invia messaggio SENZA session_id (nuova conversazione)
    result3 = send_message("Come mi chiamo?")
    
    if not result3["success"]:
        print("\n❌ Test fallito al terzo messaggio")
        return
    
    # Step 6: Verifica che sia una nuova conversazione
    new_session_id = result3["session_id"]
    
    if new_session_id and new_session_id != session_id:
        print(f"✅ SUCCESS: Creata nuova sessione: {new_session_id}")
    else:
        print(f"⚠️ WARNING: Session ID uguale o non generato")
    
    bot_response_3 = result3["bot_response"].lower()
    if "marco" not in bot_response_3:
        print("✅ SUCCESS: Il bot NON ricorda il nome (nuova conversazione)")
    else:
        print("⚠️ WARNING: Il bot sembra ricordare informazioni dalla sessione precedente")
    
    print("\n" + "="*60)
    print("📊 RIEPILOGO TEST")
    print("="*60)
    print(f"✅ Conversazione 1 - Session ID: {session_id}")
    print(f"✅ Conversazione 2 - Session ID: {new_session_id}")
    print(f"✅ Memoria contestuale: {'FUNZIONANTE' if 'marco' in result2['bot_response'].lower() else 'DA VERIFICARE'}")
    print("="*60)


if __name__ == "__main__":
    if not ADMIN_KEY:
        print("❌ ERRORE: CORE_ADMIN_KEY non configurato nel .env")
        exit(1)
    
    test_conversation()

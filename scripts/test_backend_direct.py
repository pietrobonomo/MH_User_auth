#!/usr/bin/env python3
"""Test diretto del backend conversazionale."""

import httpx
import json

url = "https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute"
headers = {
    "Content-Type": "application/json",
    "X-Admin-Key": "n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM",
    "X-App-Id": "smart_contact_form"
}
payload = {
    "flow_key": "smart_contact",
    "data": {
        "input": "Ciao, mi chiamo Marco e ho bisogno di aiuto",
        "_as_user_id": "6dff85ac-2265-4cfa-a2c0-a169401fed47"
    }
}

print("🧪 Test Backend Conversazionale\n")
print(f"📡 URL: {url}")
print(f"🔑 App ID: smart_contact_form")
print(f"🎯 Flow: smart_contact\n")

try:
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
    
    print(f"📥 Status: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        # Info importanti
        is_conversational = result.get('flow', {}).get('is_conversational')
        session_id = result.get('flow', {}).get('session_id')
        bot_text = result.get('result', {}).get('text', '')
        
        print("✅ SUCCESSO!\n")
        print(f"🔗 is_conversational: {is_conversational}")
        print(f"🆔 session_id: {session_id}")
        print(f"💬 Bot: {bot_text[:200]}...\n")
        
        if is_conversational:
            print("✅ Flow configurato come conversazionale!")
        else:
            print("❌ PROBLEMA: is_conversational è False (dovrebbe essere True)")
            
        if session_id:
            print(f"✅ Session ID ricevuto: {session_id[:20]}...")
        else:
            print("⚠️ Session ID non presente")
            
    else:
        print(f"❌ ERRORE {response.status_code}")
        try:
            error = response.json()
            print(json.dumps(error, indent=2))
        except:
            print(response.text)
            
except Exception as e:
    print(f"❌ ERRORE: {e}")















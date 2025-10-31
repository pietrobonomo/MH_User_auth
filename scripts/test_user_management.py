#!/usr/bin/env python3
"""
Test script per User Management
Testa tutti gli endpoint CRUD per la gestione utenti
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx


BASE_URL = os.environ.get("FLOW_STARTER_URL", "http://localhost:8000")
ADMIN_KEY = os.environ.get("CORE_ADMIN_KEY", "")

if not ADMIN_KEY:
    print("❌ CORE_ADMIN_KEY non configurato")
    print("   Esporta la variabile: export CORE_ADMIN_KEY='your-key'")
    sys.exit(1)


async def test_users_management():
    """Test completo gestione utenti"""
    
    headers = {
        "X-Admin-Key": ADMIN_KEY,
        "Content-Type": "application/json"
    }
    
    test_email = f"test-user-{asyncio.get_event_loop().time()}@example.com"
    created_user_id = None
    
    print("\n" + "="*60)
    print("🧪 TEST USER MANAGEMENT")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30) as client:
        
        # 1. Lista utenti esistenti
        print("\n1️⃣ Test: Lista utenti (GET /core/v1/admin/users)")
        try:
            r = await client.get(f"{BASE_URL}/core/v1/admin/users?limit=10", headers=headers)
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ Trovati {data.get('count', 0)} utenti")
                if data.get('users'):
                    print(f"   📧 Primo utente: {data['users'][0].get('email', 'N/A')}")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        # 2. Crea nuovo utente
        print(f"\n2️⃣ Test: Crea utente (POST /core/v1/admin/users)")
        print(f"   Email: {test_email}")
        try:
            payload = {
                "email": test_email,
                "full_name": "Test User",
            }
            r = await client.post(f"{BASE_URL}/core/v1/admin/users", headers=headers, json=payload)
            print(f"   Status: {r.status_code}")
            if r.status_code in (200, 201):
                data = r.json()
                created_user_id = data.get('user_id')
                print(f"   ✅ Utente creato con ID: {created_user_id}")
                print(f"   🔑 Password generata: {data.get('password', 'N/A')[:10]}...")
                print(f"   💰 Crediti iniziali: {data.get('initial_credits', 0)}")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        if not created_user_id:
            print("\n❌ Impossibile continuare senza user_id")
            return False
        
        # 3. Dettagli utente
        print(f"\n3️⃣ Test: Dettagli utente (GET /core/v1/admin/users/{created_user_id})")
        try:
            r = await client.get(f"{BASE_URL}/core/v1/admin/users/{created_user_id}", headers=headers)
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                user = data.get('user', {})
                print(f"   ✅ Email: {user.get('email')}")
                print(f"   💰 Crediti: {user.get('credits', 0)}")
                print(f"   📅 Creato: {user.get('created_at', 'N/A')[:10]}")
                print(f"   📜 Transazioni: {len(data.get('credits_history', []))}")
                if data.get('subscription'):
                    print(f"   👑 Subscription attiva: {data['subscription'].get('plan_id')}")
                else:
                    print(f"   ℹ️  Nessuna subscription")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        # 4. Modifica crediti (accredita)
        print(f"\n4️⃣ Test: Accredita crediti (POST /core/v1/admin/users/{created_user_id}/credits)")
        try:
            payload = {
                "operation": "credit",
                "amount": 50.0,
                "reason": "Test accredito"
            }
            r = await client.post(
                f"{BASE_URL}/core/v1/admin/users/{created_user_id}/credits",
                headers=headers,
                json=payload
            )
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ Operazione: {data.get('operation')}")
                print(f"   📊 Balance prima: {data.get('balance_before', 0)}")
                print(f"   📈 Balance dopo: {data.get('balance_after', 0)}")
                print(f"   ➕ Differenza: +{data.get('amount', 0)}")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        # 5. Modifica crediti (addebita)
        print(f"\n5️⃣ Test: Addebita crediti (POST /core/v1/admin/users/{created_user_id}/credits)")
        try:
            payload = {
                "operation": "debit",
                "amount": 10.0,
                "reason": "Test addebito"
            }
            r = await client.post(
                f"{BASE_URL}/core/v1/admin/users/{created_user_id}/credits",
                headers=headers,
                json=payload
            )
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ Operazione: {data.get('operation')}")
                print(f"   📊 Balance prima: {data.get('balance_before', 0)}")
                print(f"   📉 Balance dopo: {data.get('balance_after', 0)}")
                print(f"   ➖ Differenza: -{data.get('amount', 0)}")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        # 6. Storico transazioni
        print(f"\n6️⃣ Test: Storico crediti (GET /core/v1/admin/users/{created_user_id}/credits/history)")
        try:
            r = await client.get(
                f"{BASE_URL}/core/v1/admin/users/{created_user_id}/credits/history?limit=50",
                headers=headers
            )
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                transactions = data.get('transactions', [])
                print(f"   ✅ Transazioni trovate: {len(transactions)}")
                print(f"   💰 Balance corrente: {data.get('current_balance', 0)}")
                if transactions:
                    print(f"\n   📜 Ultime transazioni:")
                    for tx in transactions[:3]:
                        op_type = tx.get('operation_type', 'N/A')
                        amount = tx.get('amount', 0)
                        reason = tx.get('reason', 'N/A')[:30]
                        emoji = "➕" if op_type == "credit" else "➖"
                        print(f"      {emoji} {op_type}: {amount} - {reason}")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        # 7. Cancella utente
        print(f"\n7️⃣ Test: Cancella utente (DELETE /core/v1/admin/users/{created_user_id})")
        print(f"   ⚠️  Questa operazione è irreversibile!")
        try:
            r = await client.delete(f"{BASE_URL}/core/v1/admin/users/{created_user_id}", headers=headers)
            print(f"   Status: {r.status_code}")
            if r.status_code in (200, 204):
                print(f"   ✅ Utente cancellato con successo")
            else:
                print(f"   ❌ Errore: {r.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
        
        # 8. Verifica cancellazione
        print(f"\n8️⃣ Test: Verifica cancellazione (GET /core/v1/admin/users/{created_user_id})")
        try:
            r = await client.get(f"{BASE_URL}/core/v1/admin/users/{created_user_id}", headers=headers)
            print(f"   Status: {r.status_code}")
            if r.status_code == 404:
                print(f"   ✅ Utente correttamente rimosso (404 atteso)")
            else:
                print(f"   ⚠️  Utente ancora presente (atteso 404, ricevuto {r.status_code})")
        except Exception as e:
            print(f"   ❌ Eccezione: {e}")
            return False
    
    return True


async def main():
    """Main test runner"""
    print("\n🚀 Avvio test User Management...")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"🔑 Admin Key: {ADMIN_KEY[:10]}..." if ADMIN_KEY else "❌ Non configurato")
    
    success = await test_users_management()
    
    print("\n" + "="*60)
    if success:
        print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
    else:
        print("❌ ALCUNI TEST SONO FALLITI")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)












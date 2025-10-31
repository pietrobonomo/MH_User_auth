#!/usr/bin/env python3
"""
Verifica se il database ha le colonne necessarie per i flow conversazionali.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

async def check_schema():
    """Verifica lo schema della tabella flow_configs."""
    
    print("🔍 Controllo schema database...\n")
    
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Accept": "application/json",
    }
    
    try:
        # Leggi un flow per vedere quali colonne esistono
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/flow_configs?limit=1",
                headers=headers
            )
        
        if response.status_code == 200:
            flows = response.json()
            
            if flows and len(flows) > 0:
                columns = list(flows[0].keys())
                print("✅ Tabella flow_configs trovata")
                print(f"\n📋 Colonne presenti: {columns}\n")
                
                required_columns = ['is_conversational', 'metadata']
                missing = [col for col in required_columns if col not in columns]
                
                if missing:
                    print(f"❌ COLONNE MANCANTI: {missing}\n")
                    print("⚠️  Devi eseguire la migrazione SQL!\n")
                    print("=" * 60)
                    print("SQL DA ESEGUIRE SU SUPABASE DASHBOARD:")
                    print("=" * 60)
                    print("""
ALTER TABLE public.flow_configs 
ADD COLUMN IF NOT EXISTS is_conversational boolean DEFAULT false;

ALTER TABLE public.flow_configs 
ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb;
""")
                    print("=" * 60)
                    return False
                else:
                    print(f"✅ Tutte le colonne richieste sono presenti!\n")
                    return True
            else:
                print("⚠️  Nessun flow trovato nel database")
                return False
                
        else:
            print(f"❌ Errore query database: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ SUPABASE_URL o SUPABASE_SERVICE_KEY non configurati")
        exit(1)
    
    result = asyncio.run(check_schema())
    exit(0 if result else 1)















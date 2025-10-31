#!/usr/bin/env python3
"""
Applica la migrazione per il supporto flow conversazionali.
Legge e esegue sql/001_add_conversational_flows.sql sul database.
"""

import os
import httpx
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

def read_migration():
    """Legge il file di migrazione SQL."""
    migration_file = Path("sql/001_add_conversational_flows.sql")
    if not migration_file.exists():
        print(f"❌ File {migration_file} non trovato")
        return None
    return migration_file.read_text(encoding='utf-8')

def execute_sql(sql: str):
    """Esegue SQL tramite PostgREST query endpoint."""
    
    print(f"📡 Applicazione migrazione al database...\n")
    
    # Supabase non ha un endpoint diretto per eseguire SQL arbitrario via REST
    # Dobbiamo usare psql o pgAdmin, oppure fare l'UPDATE manualmente della tabella
    
    print("⚠️  Per applicare la migrazione, hai due opzioni:\n")
    print("1️⃣  **Manuale via Supabase Dashboard:**")
    print("   - Vai su https://supabase.com/dashboard/project/.../editor")
    print("   - Copia e incolla il contenuto di sql/001_add_conversational_flows.sql")
    print("   - Esegui la query\n")
    
    print("2️⃣  **Via psql (locale):**")
    print(f"   psql {SUPABASE_URL.replace('https://', 'postgres://postgres:PASSWORD@').replace('.supabase.co', '.supabase.co:5432/postgres')} -f sql/001_add_conversational_flows.sql\n")
    
    print("📋 SQL da eseguire:\n")
    print("="*60)
    print(sql)
    print("="*60)

if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ SUPABASE_URL o SUPABASE_SERVICE_KEY non configurati")
        exit(1)
    
    migration_sql = read_migration()
    if migration_sql:
        execute_sql(migration_sql)
















from __future__ import annotations

"""
Applica i file SQL in flow_starter/sql al database Postgres (Supabase) usando SUPABASE_DB_URL.

Esempio uso:
  python -m flow_starter.scripts.apply_sql

Env richieste:
  SUPABASE_DB_URL=postgresql://user:pass@host:port/dbname
"""

import os
import glob
import psycopg2


def main() -> None:
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        print("❌ SUPABASE_DB_URL non impostata")
        raise SystemExit(1)

    sql_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql")
    files = sorted(glob.glob(os.path.join(sql_dir, "*.sql")))
    if not files:
        print("⚠️ Nessun file SQL trovato")
        return

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for path in files:
                print(f"▶️ Applico {os.path.basename(path)}")
                with open(path, "r", encoding="utf-8") as f:
                    sql = f.read()
                cur.execute(sql)
        print("✅ Schema applicato con successo")
    finally:
        conn.close()


if __name__ == "__main__":
    main()



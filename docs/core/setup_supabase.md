# Setup Supabase (passo-passo)

Questa guida crea un progetto Supabase da zero e prepara lo schema richiesto dal Core.

## 1) Crea un progetto Supabase
- Vai su `https://supabase.com` → Sign in → New project
- Scegli Region, imposta una Database Password (conservala) e attendi il provisioning

## 2) Recupera le credenziali
- Project Settings → API
  - Project URL → usa come `SUPABASE_URL`
  - service_role → usa come `SUPABASE_SERVICE_KEY` (server-side)
- Dalla barra URL della dashboard recupera il project ref `<REF>`
  - `SUPABASE_JWKS_URL` = `https://<REF>.supabase.co/auth/v1/jwks`

## 3) Inizializza lo schema con l’SQL Editor
- Dashboard → SQL → New Query
- Incolla il contenuto di `flow_starter/sql/001_core_schema.sql`
- Clicca Run

Cosa viene creato:
- `public.profiles` con colonna `credits`
- `public.credit_transactions` (ledger)
- funzione `public.debit_user_credits(p_user_id, p_amount, p_reason)`

## 4) Configura il Core
- Copia `flow_starter/.env.example` in `flow_starter/.env`
- Compila:
  - `SUPABASE_URL="https://<REF>.supabase.co"`
  - `SUPABASE_SERVICE_KEY="<service_role>"`
  - `SUPABASE_JWKS_URL="https://<REF>.supabase.co/auth/v1/jwks"`
  - (Dev) `SUPABASE_VERIFY_DISABLED=1` per saltare la verifica firma

## 5) Avvia in locale
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```

## 6) Test rapido
- GET `/health`
- GET `/core/v1/users/me` (Authorization: Bearer `<token supabase>`)
- GET `/core/v1/credits/balance` (Authorization)
- POST `/core/v1/credits/estimate` { operation_type: "openrouter_chat", context: { model: "openrouter/model" } }
- POST `/core/v1/providers/openrouter/chat` (Authorization + body + opzionale `Idempotency-Key`)

Note:
- In produzione metti `SUPABASE_VERIFY_DISABLED=0` e usa sempre `SUPABASE_JWKS_URL`.

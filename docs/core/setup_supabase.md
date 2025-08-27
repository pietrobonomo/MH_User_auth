# Setup Supabase (passo-passo)

Questa guida crea un progetto Supabase da zero e prepara lo schema richiesto dal Core.

## 1) Crea un progetto Supabase
- Vai su `https://supabase.com` → Sign in → New project
- Scegli Region, imposta una Database Password (conservala) e attendi il provisioning

## 2) Recupera le credenziali (nuova UI Supabase)
- Project ID (REF): Settings → General → "Project ID".
  - Costruisci `SUPABASE_URL` come: `https://<ProjectID>.supabase.co`
  - Costruisci `SUPABASE_JWKS_URL` come: `https://<ProjectID>.supabase.co/auth/v1/jwks`
  - Esempio: Project ID `licwmckuwkvzrepyncz` →
    - `SUPABASE_URL=https://licwmckuwkvzrepyncz.supabase.co`
    - `SUPABASE_JWKS_URL=https://licwmckuwkvzrepyncz.supabase.co/auth/v1/jwks`
- service_role (Secret key): Settings → API Keys → TAB "Legacy API Keys" → sezione "Secrets" → tasto "Reveal" → copia il valore di `service_role`.
  - Usa questo valore come `SUPABASE_SERVICE_KEY` (solo lato server/Core).

Verifica rapida: apri `SUPABASE_JWKS_URL` nel browser, dovresti vedere un JSON con `keys`.

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

Esempio completo `.env` (dev):
```
SUPABASE_URL="https://licwmckuwkvzrepyncz.supabase.co"
SUPABASE_SERVICE_KEY="eyJhbGciOi...<service_role>..."
SUPABASE_JWKS_URL="https://licwmckuwkvzrepyncz.supabase.co/auth/v1/jwks"
SUPABASE_VERIFY_DISABLED=1
```

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

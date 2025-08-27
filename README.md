# Flow Starter (Core API)

Core FastAPI standalone per autenticazione (via token esterni), crediti e proxy AI.

## Avvio locale

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```

- Base URL: `http://127.0.0.1:5050`
- OpenAPI: `http://127.0.0.1:5050/openapi.json`
- Docs: `http://127.0.0.1:5050/docs`

## Endpoints minimi

- GET `/core/v1/users/me`
- GET `/core/v1/credits/balance`
- POST `/core/v1/credits/estimate`
- POST `/core/v1/providers/openrouter/chat`

## Variabili d'ambiente

Vedi `.env.example`.

- SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWKS_URL (o SUPABASE_VERIFY_DISABLED=1 in dev)
- PRICING_DEFAULT_CREDITS_PER_CALL (default: 1.0)
- PRICING_MODEL_MAP_JSON (es: {"openrouter/model": 2.0})

## Bootstrap Supabase (via SQL Editor)

1. Supabase Dashboard → SQL → New Query.
2. Incolla il contenuto di `flow_starter/sql/001_core_schema.sql`.
3. Esegui (Run). Verranno creati:
   - `public.profiles` (con colonna `credits`)
   - `public.credit_transactions`
   - funzione `public.debit_user_credits(p_user_id, p_amount, p_reason)`
4. Imposta nel `.env` del Core: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWKS_URL`.

## Note

- Verifica JWT via JWKS (se configurato) altrimenti decodifica senza verifica (solo dev).
- Ledger crediti via REST (profiles.credits e RPC debit_user_credits).

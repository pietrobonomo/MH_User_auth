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
- POST `/core/v1/providers/openrouter/chat`

## Variabili d'ambiente

Vedi `.env.example`.

## Note

- Questo è uno scheletro: la verifica JWT Supabase/OpenRouter verrà collegata negli adapter.
- Commenti in italiano, type hints completi, accesso alle env con `os.environ.get()`.

# OpenRouter - Setup e utilizzo nel Core

Questa guida spiega come configurare OpenRouter per il Core e come testare il proxy reale.

## 1) Ottenere l'API Key
- Vai su `https://openrouter.ai`
- Crea un account → Settings → API Keys → Generate new key
- Copia l'API key

## 2) Variabili d'ambiente
Aggiungi al file `flow_starter/.env`:

```
# OpenRouter
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_PROVISIONING_KEY=<la_tua_api_key>
```

Note:
- Se `OPENROUTER_PROVISIONING_KEY` è assente, l'adapter usa uno stub (per sviluppo).
- Se presente, il Core chiama l'endpoint reale `POST /chat/completions` di OpenRouter.

## 3) Endpoint del Core
- `POST /core/v1/providers/openrouter/chat`
  - Headers: `Authorization: Bearer <token_supabase>`
  - Body minimo:
    ```json
    { "model": "openrouter/model", "messages": [{"role":"user","content":"Ciao"}] }
    ```
  - Opzioni supportate (facoltative): `temperature`, `top_p`, `max_tokens`

Risposta tipica:
```json
{
  "response": { "choices": [{ "message": { "role": "assistant", "content": "..." } }] },
  "usage": { "input_tokens": 123, "output_tokens": 456, "cost_credits": null },
  "transaction_id": "..."
}
```

## 4) Pricing, Affordability e addebito crediti
- La configurazione è in `data/config/pricing_config.json` ed è esposta via `GET/PUT /core/v1/admin/pricing/config`.
- Campi rilevanti:
  - `usd_to_credits`, `target_margin_multiplier`, `minimum_operation_cost_credits`
  - `signup_initial_credits`: crediti iniziali assegnati ai nuovi utenti
  - `minimum_affordability_credits`: soglia minima per sbloccare le operazioni
- Pre-check affordability (HTTP 402) su `POST /core/v1/providers/flowise/execute`:
  - `required = max(estimated_cost, minimum_affordability_credits)`
  - Headers di risposta in errore: `X-Estimated-Cost-Credits`, `X-Min-Affordability`, `X-Available-Credits`
- L'addebito reale avviene misurando il delta OpenRouter post-esecuzione e calcolando:
  `actual_credits = delta_usd * final_credit_multiplier`. L'addebito usa la RPC `debit_user_credits`.

## 5) Errori comuni
- 401/403: controlla `Authorization: Bearer <token_supabase>` e la validazione JWKS (o `SUPABASE_VERIFY_DISABLED=1` in dev)
- 400/422 da OpenRouter: verifica `model`, `messages`, formati e quota/limiti
- 500 dal Core: controlla le env e i log

## 6) Test rapido
- Imposta l'API Key in `.env`
- Avvia il Core:
  ```bash
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
  ```
- Esegui la richiesta con un client (o via Swagger `/docs`):
  ```bash
  curl -X POST http://127.0.0.1:5050/core/v1/providers/openrouter/chat \
    -H "Authorization: Bearer <token_supabase>" \
    -H "Content-Type: application/json" \
    -d '{"model":"openrouter/model","messages":[{"role":"user","content":"Ciao"}]}'
  ```

## 7) Modelli supportati
Consulta la documentazione di OpenRouter per i nomi dei modelli e i limiti aggiornati.

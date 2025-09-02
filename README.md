# Flow Starter (Core API)

Core FastAPI standalone per autenticazione (via token esterni), crediti e proxy AI.

[Guida completa: Setup Supabase passo-passo](docs/core/setup_supabase.md) · [Guida OpenRouter](docs/core/openrouter_setup.md)

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
- POST `/core/v1/providers/flowise/execute`
- GET `/core/v1/billing/plans`
- POST `/core/v1/billing/checkout`
- POST `/core/v1/billing/webhook` (da configurare come endpoint di webhook del provider)

### Test checkout e webhook (locale vs live)

- Locale (senza URL pubblico): non puoi ricevere webhook reali, quindi i crediti NON si ricaricano automaticamente dopo il pagamento. Usa la pagina Admin → Testing:
  - "Generate Checkout" per aprire il link
  - "Simulate webhook (dev)" per simulare l'accredito
  - "Start polling" per osservare il saldo

- Locale con ngrok (consigliato):
  1. `ngrok http 5050`
  2. Imposta l'URL pubblico `https://<id>.ngrok.io/core/v1/billing/webhook` nello store LemonSqueezy
  3. Salva il Signing Secret nelle credenziali (Admin → Payment Provider → Test Connection deve risultare OK)
  4. Genera checkout, completa il pagamento, verifica il saldo con "Start polling"

- Live: configura direttamente l'URL pubblico del Core in produzione come webhook e testa un acquisto reale. I crediti saranno accreditati dal webhook e visibili nel ledger.

## Variabili d'ambiente

Vedi `.env.example`.

- Supabase: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWKS_URL` (o `SUPABASE_VERIFY_DISABLED=1` in dev)
- Pricing: `PRICING_DEFAULT_CREDITS_PER_CALL` (default: 1.0), `PRICING_MODEL_MAP_JSON`
- OpenRouter: `OPENROUTER_BASE_URL`, `OPENROUTER_PROVISIONING_KEY`
- Flowise: `FLOWISE_BASE_URL`, `FLOWISE_API_KEY`
- Billing (LemonSqueezy): `LEMONSQUEEZY_API_KEY`, `LEMONSQUEEZY_SIGNING_SECRET`, `LEMONSQUEEZY_BYPASS_SIGNATURE` (solo dev), `LEMONSQUEEZY_STORE_ID`, `BILLING_PROVIDER=lemonsqueezy`
- Core: `CORE_ADMIN_KEY`, `CORE_ENCRYPTION_KEY`, `CORE_APP_ID` (default: `default`)

## Deploy su Railway (one‑click)

1. Prepara un progetto Supabase e applica lo schema (`sql/000_full_schema.sql`).
2. Premi “Deploy on Railway” su questo repo e compila le ENV richieste (vedi lista sopra).
3. Aggiungi un servizio Flowise puntando al tuo fork GitHub oppure immagine ufficiale Docker.
   - Fork: `pietrobonomo/Flowise` ([link repo](https://github.com/pietrobonomo/Flowise))
   - Oppure immagine: `flowiseai/flowise:<version>`
4. Imposta `FLOWISE_BASE_URL` nel servizio core usando l’URL interno/esterno del servizio Flowise.
5. Verifica `/health` e accedi alla dashboard admin `/core/v1/admin-ui/dashboard`.
- (Opzionale single-tenant) `NL_FLOW_*_ID`, `FLOWISE_NODE_MAP_JSON`

## Pricing & Affordability

- Config file: `data/config/pricing_config.json` gestito dagli endpoint `GET/PUT /core/v1/admin/pricing/config`.
- Campi principali:
  - `usd_to_credits`: conversione USD→crediti
  - `target_margin_multiplier`: margine target
  - `minimum_operation_cost_credits`: costo minimo per singola operazione
  - `signup_initial_credits`: crediti iniziali assegnati al nuovo utente (usati in fase di provisioning profilo)
  - `minimum_affordability_credits`: soglia minima globale necessaria per sbloccare le operazioni

### Affordability pre-check e blocco (HTTP 402)

- In `POST /core/v1/providers/flowise/execute` viene effettuato un pre-check:
  - `estimated_cost = pricing.calculate_operation_cost_credits("flowise_execute", {flow_key|flow_id})`
  - `required = max(estimated_cost, minimum_affordability_credits)`
  - Se il saldo (`profiles.credits`) è inferiore a `required`, la richiesta viene bloccata con `HTTP 402` e payload:
    ```json
    {
      "error_type": "insufficient_credits",
      "can_afford": false,
      "estimated_cost": 0.25,
      "minimum_required": 1.0,
      "available_credits": 0.5,
      "shortage": 0.5,
      "flow_key": "...",
      "flow_id": "..."
    }
    ```
  - Headers restituiti: `X-Estimated-Cost-Credits`, `X-Min-Affordability`, `X-Available-Credits`.

### Detrazione crediti su delta OpenRouter

- Dopo l'esecuzione del flow, il Core misura il delta di spesa OpenRouter e addebita i crediti reali:
  - Async (default): ritorna subito il risultato e addebita in background.
  - Sync: attende il delta e addebita prima della risposta.
- Conversione: `actual_credits = delta_usd * pricing.config.final_credit_multiplier`
- Addebito via RPC `debit_user_credits` su Supabase (idempotency key supportata).

## Modalità multi-tenant

- Tabella Supabase `flow_configs(app_id, flow_key, flow_id, node_names JSON)` (già prevista nello schema SQL)
- Runtime: header `X-App-Id` e body con `flow_key`:
```json
{ "flow_key": "news_writer", "data": { "input": "..." } }
```
- Il Core risolve `flow_id` e `node_names` dal DB per quella app; inietta chiavi nei nodi e chiama Flowise.

### Troubleshooting

- Errore `Chatflow demo-flow not found`: significa che stai passando un placeholder `demo-flow` al posto di un vero `flow_id`.
  - Soluzione rapida: prendi l'ID del chatflow da Flowise e invocalo direttamente con `flow_id`.
  - Oppure configura una riga in `flow_configs` via Admin API e usa `X-App-Id` + `flow_key`.
- Come configurare via Admin API (bypass con `X-Admin-Key`):
  - POST `/core/v1/admin/flow-configs` con body:
    ```json
    { "app_id": "my-app", "flow_key": "news_writer", "flow_id": "<FLOW_ID_REALE>", "node_names": ["chatOpenRouter_0"] }
    ```
  - Poi invoca:
    ```json
    { "flow_key": "news_writer", "data": { "question": "Hello" } }
    ```

### Admin API
- GET `/core/v1/admin/flow-configs?app_id=...&flow_key=...`
- POST `/core/v1/admin/flow-configs` body:
```json
{ "app_id": "my-app", "flow_key": "news_writer", "flow_id": "<id>", "node_names": ["chatOpenRouter_0"] }
```

## Sicurezza
- JWT Supabase verificati (JWKS) o dev bypass
- Chiavi OpenRouter per utente solo server-side (Supabase), iniettate nel payload verso Flowise (mai esposte al client)
- RLS e deny-all su `flow_configs` (solo service_role del Core)

## Note
- Verifica JWT via JWKS (se configurato) altrimenti decodifica senza verifica (solo dev)
- Ledger crediti via REST (profiles.credits e RPC debit_user_credits)
- Accredito via RPC `credit_user_credits` su pagamento riuscito

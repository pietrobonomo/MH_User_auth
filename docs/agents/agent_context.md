## Flow Starter – Contesto per Agenti AI (sviluppo app)

Questo documento spiega all'agente AI come integrare un'app client con Flow Starter. L'obiettivo è che l'agente produca subito codice funzionante per login, piani/crediti e invocazione dei flow AI, chiedendo al developer solo il modello di business e le specifiche dei flussi.

### 1) Config di base (ambiente client)
- `NEXT_PUBLIC_FLOW_STARTER_API` deve puntare a `https://<core-domain>/core/v1` (senza `/` finale).
- L'app userà token JWT di Supabase per autenticare l'utente verso il Core.

Prod/Stage su Railway
- Imposta nell'app client:
  ```env
  NEXT_PUBLIC_FLOW_STARTER_API="https://<flow_starter>.up.railway.app/core/v1"
  ```
- Non serve conoscere Flowise interno: il Core su Railway parla a Flowise via rete privata.
- Se sviluppi in locale contro il Core remoto, assicurati che sul Core sia configurato `CORE_CORS_ORIGIN` con il tuo origin (es. `http://127.0.0.1:5173`).

### 2) Auth (via Supabase – proxy del Core)
Usare gli endpoint proxy del Core (o lo skeleton JS già pronto):
- POST `/auth/signup` `{ email, password, redirect_to? }`
- POST `/auth/login` `{ email, password }` → `{ access_token, refresh_token, ... }`
- POST `/auth/refresh` `{ refresh_token }`
- POST `/auth/logout` header `Authorization: Bearer <access_token>`
- GET `/auth/user` header `Authorization: Bearer <access_token>`

Helper nel client skeleton (`client_skeleton/lib/flowStarter.js`):
- `signupAuth(apiBase, email, password, redirectTo)`
- `loginAuth(apiBase, email, password)`
- `refreshAuth(apiBase, refreshToken)`
- `logoutAuth(apiBase, accessToken)`
- `getUserAuth(apiBase, accessToken)`

Linee guida UI:
- Salvare `access_token` (e opzionale `refresh_token`) in storage sicuro.
- Esportare un context/hook `useAuth` con: `user`, `token`, `login()`, `logout()`, `refresh()`.

### 3) Esecuzione di un Flow (Flowise via Core)
- Endpoint principale: POST `/providers/flowise/execute` (richiede Bearer token utente)
- Body tipico:
```json
{ "flow_key": "my_flow", "data": { "input": "..." } }
```
- Opzionale multi-tenant: header `X-App-Id: <app_id>`
- Risposta tipica: `{ "result": { "text": "...", ... }, "pricing": { ... }, "debit": { ... } }`
- Errori di crediti: HTTP 402 con `error_type: "insufficient_credits"` e `shortage`.

Helper nel client skeleton:
- `runAI(userToken, flowKey, inputData, appId?)`

### 4) Crediti, pricing e checkout
- Il Core effettua un pre-check di affordability e può rispondere 402 con il fabbisogno (`minimum_required`, `shortage`).
- Per acquistare crediti: POST `/billing/checkout` (Bearer user). Ritorna `checkout_url`.
- Dopo pagamento, il webhook ricarica i crediti e l'utente può rieseguire il flow.
- Lato UI: intercettare 402 da `runAI()` e aprire la pagina “Ricarica crediti / Seleziona piano”.

### 5) Convenzioni di integrazione
- Il client non conserva né gestisce chiavi dei modelli; le chiavi utente OpenRouter sono gestite server-side e iniettate dal Core nei nodi Flowise.
- Per i contenuti testuali, leggere `result.text`. Se è JSON in stringa, tentare il parse.
- Per tracciamento, salvare nei log client: `flowKey`, `elapsedMs`, eventuali `pricing` e `debit` se presenti.

### 6) Checklist per l’agente AI
Quando generi il codice di un’app:
1. Leggi `NEXT_PUBLIC_FLOW_STARTER_API` dall’ambiente o chiedi all’utente.
2. Implementa login con `loginAuth()` e persisti `access_token`.
3. Esporre hook `useAuth` o equivalente.
4. Implementa azione `runAI()` usando lo skeleton.
5. Gestisci l’errore 402 mostrando UI di acquisto crediti (chiama `/billing/checkout`).
6. Aggiungi pagine: Login, Profile (getUser), Pricing/Credits, Playground (runAI).

### 7) Debug rapido
- 401: token mancante/invalid → rifare login.
- 402: crediti insufficienti → generare checkout e completare acquisto.
- 500 Flowise: verificare che il flow esista e i tools siano configurati.



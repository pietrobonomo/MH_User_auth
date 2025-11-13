# 🚀 FlowStarter su Railway - Guida Completa

## ✅ Setup Semplificato

Con le modifiche del branch `simplify-railway-setup`, FlowStarter **non richiede più setup wizard** su Railway!

Tutto funziona **automaticamente** tramite variabili d'ambiente.

---

## 📋 Variabili Railway Richieste

### Core (Obbligatorie)

```bash
CORE_ADMIN_KEY=<secret-admin-key>
CORE_ENCRYPTION_KEY=<fernet-base64-key>
CORE_APP_ID=marketinghackers
CORE_CORS_ORIGIN=http://localhost:5173
```

### Supabase Self-Hosted (Interno Railway via Kong)

```bash
# URL del Kong gateway (interno)
SUPABASE_URL=http://kong.railway.internal:8000

# JWT tokens firmati con il JWT_SECRET dell'infrastruttura
SUPABASE_SERVICE_KEY=<service_role_jwt>
SUPABASE_ANON_KEY=<anon_jwt>

# JWKS URL pubblico per validazione token
SUPABASE_JWKS_URL=https://<kong-public-domain>/auth/v1/jwks

# Disabilita verifica JWKS se usi Supabase interno
SUPABASE_VERIFY_DISABLED=1

# (Opzionale) URL diretto GotrueAuth per auth
SUPABASE_AUTH_URL=http://gotrue-auth.railway.internal:9999
```

### LemonSqueezy

```bash
BILLING_PROVIDER=lemonsqueezy
LEMONSQUEEZY_API_KEY=<api-jwt-token>
LEMONSQUEEZY_STORE_ID=<store-id>
LEMONSQUEEZY_SIGNING_SECRET=<webhook-secret>
LEMONSQUEEZY_BYPASS_SIGNATURE=1  # Solo per test/dev
```

### Flowise (Opzionale)

```bash
FLOWISE_BASE_URL=<flowise-url>
FLOWISE_API_KEY=<api-key>
```

### OpenRouter Provisioning

```bash
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_PROVISIONING_KEY=<provisioning-key>
```

### Admin UI

```bash
ADMIN_UI_ENABLED=1
ADMIN_UI_USER=admin
ADMIN_UI_PASSWORD=<password>
```

---

## 🔑 X-Admin-Key - Come Funziona

### Cos'è

`X-Admin-Key` è un **header HTTP** usato per autenticare operazioni amministrative **senza richiedere un token utente JWT**.

### A cosa serve

1. **Dashboard Admin** - Tutte le chiamate API della dashboard usano X-Admin-Key
2. **Automazione** - Script e CI/CD possono gestire il sistema
3. **Bypass Auth** - Operazioni admin senza bisogno di login utente
4. **Impersonificazione** - Eseguire azioni per conto di altri utenti

### Come si usa

#### Nella Dashboard (Browser)

1. Accedi a `/core/v1/admin-ui/dashboard` (login: admin/password)
2. Clicca **"Quick Setup"** o apri console browser (F12)
3. Configura l'Admin Key:

```javascript
State.adminKey = 'aSes_PTlzVr2kAs98LOTLxHwUTVdw6rlR-SUc2SuOOM';
State.save();
location.reload();
```

4. La dashboard ora funzionerà per tutte le operazioni!

#### In Script/API Calls

```bash
# Esempio: Lista utenti
curl -X GET \
  -H "X-Admin-Key: aSes_PTlzVr2kAs98LOTLxHwUTVdw6rlR-SUc2SuOOM" \
  https://flowstarter-production.up.railway.app/core/v1/admin/users

# Esempio: Crea utente
curl -X POST \
  -H "X-Admin-Key: aSes_PTlzVr2kAs98LOTLxHwUTVdw6rlR-SUc2SuOOM" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' \
  https://flowstarter-production.up.railway.app/core/v1/admin/users
```

#### In Python

```python
import httpx

ADMIN_KEY = "aSes_PTlzVr2kAs98LOTLxHwUTVdw6rlR-SUc2SuOOM"
BASE_URL = "https://flowstarter-production.up.railway.app"

headers = {
    "X-Admin-Key": ADMIN_KEY,
    "Content-Type": "application/json"
}

# Crea utente
response = httpx.post(
    f"{BASE_URL}/core/v1/admin/users",
    headers=headers,
    json={"email": "test@example.com"}
)
```

---

## 🎯 Differenza con Bearer Token

| Caratteristica | X-Admin-Key | Bearer Token (JWT) |
|---|---|---|
| **Scopo** | Operazioni admin | Autenticazione utente |
| **Formato** | String random | JWT (xxx.yyy.zzz) |
| **Durata** | Permanente | Scade (exp claim) |
| **Permessi** | Accesso completo | Limitato al ruolo utente |
| **Storage** | ENV vars + localStorage | Session/cookies |

---

## 🔄 Credenziali Provider - Come funziona ora

### Sistema a 2 livelli (Backward Compatible)

**Livello 1 - ENV vars (Priorità alta)**
- FlowStarter cerca prima nelle variabili d'ambiente Railway
- ✅ Perfetto per deployment semplificati
- ✅ Zero configurazione nel database
- ⚡ Più veloce (no query DB)

**Livello 2 - Database criptato (Fallback)**
- Se ENV vars non disponibili, cerca nel DB (tabella `encrypted_credentials`)
- ✅ Più sicuro per self-hosted
- ✅ Permette rotazione chiavi
- 🔒 Chiavi criptate con CORE_ENCRYPTION_KEY

### Mapping ENV vars

```python
# LemonSqueezy
lemonsqueezy:api_key → LEMONSQUEEZY_API_KEY
lemonsqueezy:webhook_secret → LEMONSQUEEZY_SIGNING_SECRET

# Flowise
flowise:base_url → FLOWISE_BASE_URL
flowise:api_key → FLOWISE_API_KEY
```

### Vantaggi

✅ **Su Railway**: Zero setup, tutto da ENV vars  
✅ **Self-hosted**: Credenziali sicure criptate nel DB  
✅ **Backward compatible**: Codice esistente continua a funzionare  
✅ **Flessibile**: Puoi scegliere quale metodo usare  

---

## 📊 Architettura MarketingHackers-Platform

```
┌─────────────────────────────────────┐
│  Kong (API Gateway)                 │
│  kong.railway.internal:8000         │
│  https://kong-production.railway.app│
└────┬──────────────┬─────────────────┘
     │              │
     │         ┌────▼──────┐
     │         │ Postgrest │
     │         │   :3000   │
     │         └────┬──────┘
     │              │
┌────▼──────┐  ┌───▼─────────┐
│GotrueAuth │  │  Postgres   │
│  :9999    │  │    :5432    │
└───────────┘  └─────────────┘

┌─────────────────────────────────────┐
│  FlowStarter                        │
│  flowstarter.railway.internal:3000  │
│  → Kong (per Postgrest)             │
│  → GotrueAuth (diretto)             │
└─────────────────────────────────────┘
```

**FlowStarter** comunica:
- Con **Kong internamente** per accedere a Postgrest (path `/rest/v1/...`)
- Con **GotrueAuth direttamente** per autenticazione veloce
- Con **Postgres** tramite Postgrest (via Kong)

---

## 🧪 Test Rapidi

### Health Check

```bash
curl https://flowstarter-production.up.railway.app/health
# {"status":"ok"}
```

### Test Admin Endpoint

```bash
curl -H "X-Admin-Key: <your-admin-key>" \
  https://flowstarter-production.up.railway.app/core/v1/admin/users?limit=1
```

### Test LemonSqueezy Connection

Dashboard → Testing → "Test Connection"

---

## 🔒 Sicurezza Best Practices

### Railway Production

1. **Cambia credenziali default**:
   - `ADMIN_UI_USER` / `ADMIN_UI_PASSWORD` (non usare admin/admin)
   - Genera `CORE_ADMIN_KEY` sicura: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **Proteggi ENV vars**:
   - Non committare `.env` nel repository
   - Usa Railway Secrets per variabili sensibili

3. **CORS**:
   - Configura `CORE_CORS_ORIGIN` con i domini frontend reali
   - Non usare `*` in produzione

### LemonSqueezy Webhook

Configura webhook URL su LemonSqueezy:
```
https://flowstarter-production.up.railway.app/core/v1/billing/webhook
```

---

## 🆘 Troubleshooting

### Errore: "Token mancante"

**Problema**: Admin Key non configurata nel browser  
**Soluzione**: Quick Setup → Admin Key → Salva

### Errore: "Server lacks JWT secret"

**Problema**: JWT tokens non firmati con JWT_SECRET corretto  
**Soluzione**: Rigenera JWT usando lo script Python (vedi docs)

### Errore: "API key mancante" (LemonSqueezy)

**Problema**: Variabile `LEMONSQUEEZY_API_KEY` mancante o non valida  
**Soluzione**: Verifica variabili Railway e testa connessione

---

## 📝 Migration da Setup Wizard

Se hai già usato il setup wizard:

1. ✅ Le credenziali nel DB continueranno a funzionare
2. ✅ ENV vars hanno priorità sul DB
3. ✅ Puoi migrare gradualmente o lasciare tutto nel DB

**Zero breaking changes!** 🎉

---

**Ultima modifica**: 2025-10-31  
**Branch**: `simplify-railway-setup`  
**Status**: ✅ Testato e funzionante


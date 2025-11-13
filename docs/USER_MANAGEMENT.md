# User Management - Documentazione

## 📋 Panoramica

FlowStarter ora include una sezione completa di **User Management** che permette agli amministratori di:

- 👥 **Visualizzare** tutti gli utenti registrati
- 🔍 **Cercare** utenti per email
- 👁️ **Vedere dettagli completi** di ogni utente
- 💰 **Modificare crediti** manualmente (accredito/addebito)
- 📜 **Consultare storico** transazioni crediti
- ➕ **Creare** nuovi utenti
- 🗑️ **Eliminare** utenti esistenti

## 🎯 Accesso alla Sezione

1. Apri la **Admin Dashboard**: `http://your-domain/static/admin/templates/dashboard.html`
2. Nel menu laterale, clicca su **Users** (icona 👥)

## ⚙️ Funzionalità

### 1. Lista Utenti

La pagina principale mostra una tabella con tutti gli utenti:
- **Email**: Indirizzo email dell'utente
- **Crediti**: Saldo crediti disponibili (con badge colorato)
- **Data Registrazione**: Quando l'utente si è registrato
- **Azioni**: Pulsanti per visualizzare dettagli o eliminare

**Ricerca**: Usa la barra di ricerca per filtrare gli utenti per email.

### 2. Dettagli Utente

Cliccando su **"Dettagli"** si apre un modal con 4 tab:

#### Tab "Info"
- **Informazioni Base**: ID, email, nome, data registrazione
- **Crediti Correnti**: Saldo attuale con pulsante per modificare
- **Subscription**: Se presente, mostra piano attivo, status, crediti mensili

#### Tab "Crediti"
Form per modificare manualmente i crediti:
- **Operazione**: Accredita (+) o Addebita (-)
- **Importo**: Numero di crediti da aggiungere/rimuovere
- **Motivo**: Descrizione del motivo (es. "Rimborso supporto")

Mostra il balance prima e dopo l'operazione.

#### Tab "Storico"
Tabella con le ultime transazioni crediti:
- Data e ora
- Tipo (credit/debit)
- Importo
- Motivo
- Balance dopo l'operazione

Pulsante per caricare lo storico completo (fino a 500 transazioni).

#### Tab "Avanzate"
- **Chiavi OpenRouter**: Lista chiavi API provisionate per l'utente
- **Zona Pericolosa**: Pulsante per eliminare l'utente

### 3. Creazione Utente

Clicca sul pulsante **"Nuovo Utente"** in alto a destra per aprire il form:

**Campi**:
- **Email** (obbligatorio): Indirizzo email utente
- **Password** (opzionale): Se vuoto, viene generata automaticamente
- **Nome Completo** (opzionale): Nome e cognome

**Cosa succede alla creazione**:
1. ✅ Utente creato in Supabase Auth
2. ✅ Profilo creato nella tabella `profiles`
3. ✅ Crediti iniziali accreditati (secondo configurazione pricing)
4. ✅ Chiave OpenRouter provisionata automaticamente
5. ✅ Password mostrata una sola volta (salvarla!)

### 4. Eliminazione Utente

**⚠️ ATTENZIONE**: Operazione **irreversibile**!

1. Clicca sul pulsante 🗑️ nella lista o nel tab "Avanzate" del dettaglio
2. Conferma digitando **"ELIMINA"** nel campo
3. Clicca su "Elimina Definitivamente"

**Cosa viene eliminato**:
- ❌ Profilo utente
- ❌ Storico transazioni crediti
- ❌ Subscription attive
- ❌ Chiavi OpenRouter
- ❌ Utente da Supabase Auth (se possibile)

## 🔌 API Endpoints

Tutti gli endpoint richiedono l'header `X-Admin-Key` con la chiave admin.

### Lista Utenti
```http
GET /core/v1/admin/users?q={query}&limit={limit}
```

**Query Parameters**:
- `q` (opzionale): Filtra per email (case-insensitive)
- `limit` (opzionale): Numero massimo risultati (default: 50, max: 100)

**Response**:
```json
{
  "count": 25,
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "credits": 100.0,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Dettagli Utente
```http
GET /core/v1/admin/users/{user_id}
```

**Response**:
```json
{
  "status": "success",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "credits": 100.0,
    "full_name": "Mario Rossi",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "subscription": {
    "plan_id": "pro",
    "status": "active",
    "credits_per_month": 1000
  },
  "credits_history": [
    {
      "id": 123,
      "amount": 50.0,
      "operation_type": "credit",
      "reason": "signup_initial_credits",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "openrouter_keys": [
    {
      "key_name": "sk-or-v1-...",
      "limit_usd": 10,
      "is_active": true
    }
  ]
}
```

### Crea Utente
```http
POST /core/v1/admin/users
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "Optional123!",
  "full_name": "Mario Rossi"
}
```

**Response**:
```json
{
  "status": "success",
  "user_id": "uuid",
  "email": "newuser@example.com",
  "password": "GeneratedPass123!",
  "initial_credits": 50.0,
  "credits_after": 50.0,
  "openrouter": {
    "provisioned": true,
    "key_name": "sk-or-v1-..."
  }
}
```

### Modifica Crediti
```http
POST /core/v1/admin/users/{user_id}/credits
Content-Type: application/json

{
  "operation": "credit",
  "amount": 50.0,
  "reason": "Rimborso supporto"
}
```

**Parameters**:
- `operation`: `"credit"` (accredita) o `"debit"` (addebita)
- `amount`: Importo (sempre positivo)
- `reason`: Descrizione motivo

**Response**:
```json
{
  "status": "success",
  "operation": "credit",
  "amount": 50.0,
  "reason": "Rimborso supporto",
  "balance_before": 100.0,
  "balance_after": 150.0
}
```

### Storico Crediti
```http
GET /core/v1/admin/users/{user_id}/credits/history?limit={limit}&offset={offset}
```

**Query Parameters**:
- `limit` (opzionale): Numero risultati (default: 50, max: 500)
- `offset` (opzionale): Paginazione offset

**Response**:
```json
{
  "status": "success",
  "user_id": "uuid",
  "current_balance": 150.0,
  "transactions": [
    {
      "id": 123,
      "user_id": "uuid",
      "amount": 50.0,
      "operation_type": "credit",
      "reason": "signup_initial_credits",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "count": 25
  }
}
```

### Elimina Utente
```http
DELETE /core/v1/admin/users/{user_id}
```

**Response**:
```json
{
  "status": "success",
  "message": "Utente {user_id} cancellato con successo"
}
```

## 🔒 Sicurezza

- ✅ Tutti gli endpoint richiedono autenticazione admin (`X-Admin-Key`)
- ✅ Le password generate sono sicure (crypto-random)
- ✅ L'eliminazione richiede conferma esplicita
- ✅ Le operazioni critiche sono loggate

## 🧪 Testing

Per testare la funzionalità, esegui lo script di test:

```bash
# Configura la chiave admin
export CORE_ADMIN_KEY="your-admin-key"

# Esegui test
python scripts/test_user_management.py
```

Il test verifica:
1. ✅ Lista utenti
2. ✅ Creazione utente
3. ✅ Dettagli utente
4. ✅ Accredito crediti
5. ✅ Addebito crediti
6. ✅ Storico transazioni
7. ✅ Eliminazione utente

## 📝 Note Tecniche

### Database

La funzionalità utilizza le seguenti tabelle Supabase:
- `profiles`: Profili utente con crediti
- `credit_transactions`: Storico transazioni crediti
- `subscriptions`: Subscription attive
- `openrouter_user_keys`: Chiavi API OpenRouter

### Frontend

**Componenti**:
- `app/static/admin/js/components/users.js`: Logica gestione utenti
- `app/static/admin/js/page-templates.js`: Template UI pagina users
- `app/static/admin/js/dashboard.js`: Routing e integrazione

**Stile**:
- DaisyUI components
- TailwindCSS
- Font Awesome icons

### Backend

**Endpoint**:
- `app/api/endpoints/users.py`: CRUD completo utenti

**Servizi**:
- `app/services/credits_supabase.py`: Gestione crediti
- `app/services/openrouter_provisioning.py`: Provisioning API keys

## 🎨 UI/UX

- 🎯 **Intuitiva**: Interfaccia pulita con azioni chiare
- 🔍 **Ricerca veloce**: Filtra utenti in tempo reale
- 📊 **Visualizzazione completa**: Tutte le info in un unico modal
- ⚡ **Azioni rapide**: Modifica crediti e gestione con pochi click
- ⚠️ **Sicurezza**: Conferme per azioni pericolose

## 🚀 Roadmap Futura

Possibili miglioramenti:
- [ ] Esportazione lista utenti (CSV/Excel)
- [ ] Filtri avanzati (per crediti, data registrazione, subscription)
- [ ] Bulk operations (modifica multipla utenti)
- [ ] Grafici andamento crediti
- [ ] Notifiche email automatiche
- [ ] Log audit dettagliato
- [ ] Sospensione temporanea account

---

**Sviluppato con ❤️ per FlowStarter**












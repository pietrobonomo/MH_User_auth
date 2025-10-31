# 🔧 Troubleshooting OpenRouter Provisioning

## 📊 Analisi Effettuata

### ✅ Variabili d'Ambiente Verificate su Railway

Tutte le variabili necessarie sono presenti:
- `OPENROUTER_PROVISIONING_KEY` ✅
- `OPENROUTER_BASE_URL` ✅  
- `SUPABASE_URL` ✅
- `SUPABASE_SERVICE_KEY` ✅
- `CORE_ADMIN_KEY` ✅
- `CORE_ENCRYPTION_KEY` ✅

### 🛠️ Modifiche Implementate

#### 1. **Logging Dettagliato nell'Endpoint API** (`app/api/endpoints/users.py`)
- Aggiunto import di `logging` e `traceback`
- Log all'inizio del provisioning
- Log di successo con nome chiave creata
- Log di errore con tipo eccezione e stack trace completo
- Errore restituito nella risposta API con tutti i dettagli

#### 2. **Logging Dettagliato nel Servizio** (`app/services/openrouter_provisioning.py`)
- Log per ogni step del processo:
  - **Step 0**: Assicurazione profilo Supabase
  - **Step 1**: Creazione chiave su OpenRouter
  - **Step 2**: Parsing risposta OpenRouter
  - **Step 3**: Generazione metadati chiave
  - **Step 4**: Salvataggio nel profilo Supabase
  - **Step 5**: Salvataggio mapping tracking
- Log di errore dettagliati con status code e body delle risposte HTTP

### 🎯 Emoji per Identificare i Log

- 🔄 = Operazione in corso
- ✅ = Successo
- ❌ = Errore
- ⚠️ = Warning (non critico)
- 📡 = Risposta HTTP
- 🎉 = Completamento con successo

## 📝 Comandi per Deploy e Test

### 1. Deploy su Railway
```powershell
cd "c:\Users\Pietro\Desktop\Marketing-Hackers\Production\flow_starter"
.\deploy-to-railway.ps1
```

### 2. Controlla i log
```powershell
.\check-logs.ps1
```

O manualmente:
```powershell
railway logs --service flow_starter --lines 100
```

### 3. Testa la creazione utente

#### A. Dalla Dashboard Admin (funziona già):
1. Vai su `https://flowstarter-production.up.railway.app/core/v1/admin/ui`
2. Testing → Create Test User
3. Inserisci email e crea

#### B. Dal Form Locale (quello che non funzionava):
1. Assicurati che il form punti a: `https://flowstarter-production.up.railway.app`
2. Inserisci la `X-Admin-Key`: `n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM`
3. Crea un utente di test

### 4. Cerca gli errori nei log

Cerca questi pattern:
```
❌ Errore provisioning OpenRouter
❌ OpenRouter create key failed
❌ Supabase update profile failed
❌ OpenRouter non ha restituito una chiave API valida
```

## 🔍 Possibili Cause (da verificare nei log)

### 1. **Errore chiamata OpenRouter API**
Se vedi: `❌ OpenRouter create key failed: XXX`
- Verifica che la provisioning key sia valida
- Controlla i limiti di rate della chiave
- Verifica che la chiave abbia permessi di creazione

### 2. **Errore formato risposta OpenRouter**
Se vedi: `❌ OpenRouter non ha restituito una chiave API valida`
- La risposta di OpenRouter ha un formato inaspettato
- Controlla il log `Risposta JSON: {...}` per vedere la struttura

### 3. **Errore Supabase**
Se vedi: `❌ Supabase update profile failed: XXX`
- Verifica permessi della service key
- Controlla che la tabella `profiles` abbia le colonne necessarie:
  - `openrouter_api_key`
  - `openrouter_key_hash`
  - `openrouter_key_name`
  - `openrouter_key_limit`
  - `openrouter_key_created_at`
  - `openrouter_provisioning_status`

### 4. **Timeout di rete**
Se vedi timeout o errori di connessione:
- OpenRouter potrebbe essere lento
- Railway potrebbe avere problemi di rete
- Verifica con: `curl -I https://openrouter.ai/api/v1`

## 📊 Verifica Schema Supabase

Connettiti a Supabase Studio e verifica le colonne della tabella `profiles`:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'profiles'
  AND column_name LIKE 'openrouter%';
```

Colonne attese:
- `openrouter_api_key` (text)
- `openrouter_key_hash` (text)
- `openrouter_key_name` (text)
- `openrouter_key_limit` (numeric/float)
- `openrouter_key_created_at` (timestamp/text)
- `openrouter_provisioning_status` (text)

## 🚀 Next Steps

1. ✅ Deploy completato
2. 🔄 Controlla i log per vedere l'errore esatto
3. 🔄 Testa la creazione utente
4. 🔄 Condividi i log se l'errore persiste

---

**Creato il**: 2025-10-07
**Autore**: AI Assistant (Cursor)

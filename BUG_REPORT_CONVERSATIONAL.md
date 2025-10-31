# 🐛 BUG REPORT: is_conversational sempre False

## 📊 PROBLEMA

Il campo `flow.is_conversational` nella risposta dell'endpoint `/core/v1/providers/flowise/execute` **ritorna sempre `False`**, anche quando il database ha `is_conversational=True` per quel flow.

---

## ✅ VERIFICHE COMPLETATE

### 1️⃣ Database Schema - ✅ CORRETTO
```sql
-- Colonne presenti in flow_configs:
✅ app_id (text)
✅ flow_key (text)
✅ flow_id (text)
✅ node_names (jsonb)
✅ created_at (timestamp)
✅ updated_at (timestamp)
✅✅ is_conversational (boolean)  ⬅️ PRESENTE!
✅✅ metadata (jsonb)             ⬅️ PRESENTE!
```

### 2️⃣ Dati nel Database - ✅ CORRETTO
```
app_id: smart_contact_form
flow_key: smart_contact
is_conversational: TRUE  ⬅️ CONFIGURATO CORRETTAMENTE
```

### 3️⃣ Risposta API - ❌ SBAGLIATA
```json
{
  "flow": {
    "flow_id": "74f8532c-cc6a-428d-82c8-be622591fc64",
    "flow_key": "smart_contact",
    "is_conversational": false,  ⬅️ SEMPRE FALSE (BUG!)
    "session_id": "..."
  }
}
```

---

## 🔍 ROOT CAUSE

### File: `app/services/flowise_config_service.py`

**Riga 96 - Query SELECT mancante:**
```python
# ❌ ATTUALE (sbagliato):
url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=eq.{flow_key}&select=flow_id,node_names"

# ✅ DOVREBBE ESSERE:
url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=eq.{flow_key}&select=flow_id,node_names,is_conversational,metadata"
```

**Riga 123-126 - Return mancante:**
```python
# ❌ ATTUALE (sbagliato):
return {
    "flow_id": row.get("flow_id"),
    "node_names": dedup_nodes,
}

# ✅ DOVREBBE ESSERE:
return {
    "flow_id": row.get("flow_id"),
    "node_names": dedup_nodes,
    "is_conversational": row.get("is_conversational", False),
    "metadata": row.get("metadata", {}),
}
```

---

## 🛠️ SOLUZIONE RICHIESTA

### File da modificare: `app/services/flowise_config_service.py`

```python
# Riga 96 - Aggiungi is_conversational e metadata al SELECT
url = f"{supabase_url}/rest/v1/flow_configs?app_id=eq.{app_id}&flow_key=eq.{flow_key}&select=flow_id,node_names,is_conversational,metadata"

# Riga 123-128 - Aggiungi campi al return
return {
    "flow_id": row.get("flow_id"),
    "node_names": dedup_nodes,
    "is_conversational": row.get("is_conversational", False),  # ⬅️ AGGIUNGI
    "metadata": row.get("metadata", {}),                        # ⬅️ AGGIUNGI
}
```

---

## 🧪 COME TESTARE

### Test 1: Verifica che is_conversational sia True nella risposta

```bash
curl -X POST https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM" \
  -H "X-App-Id: smart_contact_form" \
  -d '{
    "flow_key": "smart_contact",
    "data": {
      "input": "test",
      "_as_user_id": "6dff85ac-2265-4cfa-a2c0-a169401fed47"
    }
  }'
```

**Risposta attesa:**
```json
{
  "flow": {
    "is_conversational": true  ⬅️ DEVE ESSERE TRUE!
  }
}
```

### Test 2: Verifica memoria conversazionale

```bash
# Prima chiamata
curl ... -d '{"flow_key": "smart_contact", "data": {"input": "Mi chiamo Mario"}}'
# Salva il session_id dalla risposta

# Seconda chiamata CON session_id
curl ... -d '{"flow_key": "smart_contact", "session_id": "SAVED_SESSION_ID", "data": {"input": "Come mi chiamo?"}}'
```

**Risposta attesa:**
- Il bot deve rispondere "Ti chiami Mario" o simile
- Il bot DEVE ricordare il nome dalla prima chiamata

---

## 📋 CHECKLIST FIX

- [ ] Modificare `app/services/flowise_config_service.py` riga 96
- [ ] Modificare `app/services/flowise_config_service.py` riga 123-128
- [ ] Commit e push
- [ ] Deploy/restart servizio
- [ ] Test 1: verificare `is_conversational: true` in risposta
- [ ] Test 2: verificare memoria funzionante
- [ ] Chiudere issue

---

## 📊 IMPATTO

**CRITICO** - Senza questo fix, tutti i flow conversazionali non funzionano, incluso il form di contatto ROOM06.

---

## ✅ COSA È GIÀ A POSTO

Lato ROOM06 (sito):
- ✅ Frontend gestisce `sessionId` correttamente
- ✅ Backend passa `session_id` a FlowStarter
- ✅ Salva e riusa `sessionId` tra chiamate
- ✅ Configurazione `.env` corretta

Lato FlowStarter (backend):
- ✅ Database migrato correttamente
- ✅ Colonna `is_conversational` presente
- ✅ Config `smart_contact_form` ha `is_conversational=true`
- ✅ Tabella `flow_sessions` creata
- ❌ **SOLO** il codice Python non legge/ritorna il campo

---

**FIX STIMATO:** 5 minuti + 5 minuti deploy = 10 minuti totali

**PRIORITÀ:** 🔴 ALTA - Blocca feature conversazionale per tutti gli utenti


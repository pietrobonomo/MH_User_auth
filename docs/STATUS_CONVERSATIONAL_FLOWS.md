# 📊 Status Conversational Flows - Aggiornamento Finale

**Data:** 7 Ottobre 2025  
**Ultima modifica:** In corso

---

## ✅ COMPLETATO

### 1️⃣ Database Schema
- ✅ Tabella `flow_configs` ha colonna `is_conversational`
- ✅ Tabella `flow_configs` ha colonna `metadata`
- ✅ Tabella `flow_sessions` creata (opzionale, per analytics)
- ✅ Config `smart_contact_form/smart_contact` ha `is_conversational=true`

### 2️⃣ Backend API
- ✅ Endpoint `/execute` supporta `session_id` opzionale nel payload
- ✅ `FlowiseRequest` model include campo `session_id`
- ✅ `FlowiseAdapter.execute()` accetta parametro `session_id`
- ✅ Codice passa `session_id` a Flowise se flow conversazionale
- ✅ Risposta API include `flow.is_conversational` e `flow.session_id`

### 3️⃣ Codice Python Fix
- ✅ `flowise_config_service.py` legge `is_conversational` dal DB
- ✅ `flowise_config_service.py` propaga `is_conversational` nel return
- ✅ `admin.py` include `is_conversational` nelle query SELECT
- ✅ `core.py` gestisce logica condizionale per session_id

### 4️⃣ Admin UI
- ✅ Flow Mappings mostra colonna "Conversational"
- ✅ Form ha checkbox "Conversational Mode"
- ✅ Edit/Save gestiscono `is_conversational`
- ✅ Testing ha sezione "Conversational Flow Test" con chat UI

### 5️⃣ Documentazione
- ✅ `docs/core/conversational_flows.md` - Guida completa
- ✅ `docs/core/public_form_integration.md` - Form pubblici
- ✅ `docs/ISTRUZIONI_SVILUPPATORI_FORM.md` - Guide dev
- ✅ `README.md` aggiornato con link

### 6️⃣ Testing Scripts
- ✅ `scripts/test_conversational_flow.py`
- ✅ `scripts/test_public_form.py`
- ✅ `scripts/check_database_schema.py`
- ✅ `scripts/test_backend_direct.py`

---

## ⚠️ IN CORSO DI DEBUG

### Problema: Session ID Non Mantenuto

**Sintomo:**  
Anche passando `session_id` nella seconda chiamata, Flowise ritorna un session_id DIVERSO.

**Test:**
```
Chiamata 1: NO session_id → Flowise genera: abc-123
Chiamata 2: CON session_id=abc-123 → Flowise genera: xyz-789 ❌
```

**Possibili Cause:**
1. Flowise non riceve il `sessionId` nel payload
2. Il campo ha un nome diverso in Flowise (es. `session_id` vs `sessionId`)
3. Il flow in Flowise non ha memoria abilitata
4. Flowise richiede parametri aggiuntivi per riutilizzare sessioni

**Debug in Corso:**
- Aggiunto logging dettagliato in `provider_flowise.py` (commit `078a116`)
- Log mostreranno se sessionId viene inviato e se cambia nella risposta
- Prossimo: Controllare i log Railway dopo il deploy

---

## 🔧 WORKAROUND TEMPORANEO (se Flowise non supporta sessionId)

Se Flowise non mantiene le sessioni tramite `sessionId`, dovremo:

### Opzione A: Usare chatId invece di sessionId
```python
# Provare con chatId invece
enriched["chatId"] = session_id
```

### Opzione B: Gestire memoria lato FlowStarter
- Salvare cronologia conversazione in `flow_sessions`
- Passare la cronologia completa a Flowise ad ogni chiamata
- Più complesso ma funzionerebbe con qualsiasi versione Flowise

### Opzione C: Upgrade Flowise
- Verificare versione Flowise in uso
- Aggiornare a versione più recente se necessario
- Controllare documentazione Flowise per session management

---

## 🧪 ISTRUZIONI PER TEST (DEV ROOM06)

### Test 1: Backend API (cURL simulato)

```python
# Prima chiamata
response1 = requests.post(
    'https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute',
    headers={
        'Content-Type': 'application/json',
        'X-Admin-Key': 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',
        'X-App-Id': 'smart_contact_form'
    },
    json={
        'flow_key': 'smart_contact',
        'data': {
            'input': 'Ciao, mi chiamo Marco',
            '_as_user_id': '6dff85ac-2265-4cfa-a2c0-a169401fed47'
        }
    }
)

data1 = response1.json()
print(f"is_conversational: {data1['flow']['is_conversational']}")  # Deve essere True
print(f"session_id: {data1['flow']['session_id']}")  # Salva questo ID

session_id = data1['flow']['session_id']

# Seconda chiamata CON session_id
response2 = requests.post(
    'https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute',
    headers={
        'Content-Type': 'application/json',
        'X-Admin-Key': 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',
        'X-App-Id': 'smart_contact_form'
    },
    json={
        'flow_key': 'smart_contact',
        'session_id': session_id,  # ✅ Passa il session_id salvato
        'data': {
            'input': 'Ti ricordi il mio nome?',
            '_as_user_id': '6dff85ac-2265-4cfa-a2c0-a169401fed47'
        }
    }
)

data2 = response2.json()
print(f"session_id returned: {data2['flow']['session_id']}")  # Dovrebbe essere LO STESSO
print(f"Bot response: {data2['result']['text']}")  # Dovrebbe ricordare "Marco"
```

### Test 2: Verificare se il problema è Flowise

**Testare DIRETTAMENTE contro Flowise** (senza FlowStarter):

```bash
curl -X POST https://nl-flow.onrender.com/api/v1/prediction/74f8532c-cc6a-428d-82c8-be622591fc64 \
  -H "Authorization: Bearer ordpP+1X1ooVZIR9QiZoGLVGmU+KGZ3FB1jeyLG1wwM=" \
  -d '{
    "question": "Mi chiamo Marco",
    "sessionId": "test-session-123"
  }'
```

Se anche Flowise diretto ignora sessionId, il problema è nella configurazione del flow Flowise stesso.

---

## 📞 SUPPORTO NECESSARIO

Per procedere serve:
1. Controllare i **log Railway** dopo il prossimo deploy (2-3 min)
2. Verificare **configurazione del flow in Flowise UI**:
   - Il flow ha "Memory" abilitata?
   - Che tipo di memoria (Buffer, Summary, etc.)?
3. Testare **direttamente contro Flowise** (bypassando FlowStarter)

---

## 🎯 PRIORITÀ

**ALTA** - Feature quasi completa, manca solo il passaggio corretto sessionId a Flowise.

**Tempo stimato fix:** 30-60 minuti una volta identificata la causa root.

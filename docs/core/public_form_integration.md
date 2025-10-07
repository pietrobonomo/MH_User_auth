# 🌐 Guida Integrazione Form Pubblico con FlowStarter

## 📋 Caso d'uso
Form di customer service **pubblico** che consente a chiunque di inviare domande senza login. Tutte le richieste vengono eseguite "a nome di" un utente tecnico che paga i costi.

---

## 🔑 Credenziali necessarie

### 1. X-Admin-Key (Header)
```
X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM
```

### 2. Utente tecnico/servizio (UUID)
```
User ID: 6dff85ac-2265-4cfa-a2c0-a169401fed47
Email: pietrobonomo22@gmail.com
```

**⚠️ IMPORTANTE:** Nelle chiamate API devi usare l'**UUID**, NON l'email!

---

## ✅ CHIAMATA CORRETTA

### Endpoint
```
POST https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute
```

### Headers
```typescript
{
  'Content-Type': 'application/json',
  'X-Admin-Key': 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',  // ✅ OBBLIGATORIO
  'X-App-Id': 'smart_contact_form'
}
```

### Body
```json
{
  "flow_key": "smart_contact",
  "data": {
    "input": "Domanda dell'utente qui",
    "_as_user_id": "6dff85ac-2265-4cfa-a2c0-a169401fed47"  // ✅ UUID, NON EMAIL!
  }
}
```

---

## 💻 Esempio Codice (JavaScript/TypeScript)

```typescript
async function inviaRichiestaFlowStarter(inputUtente: string) {
  const response = await fetch(
    'https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Key': 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',
        'X-App-Id': 'smart_contact_form'
      },
      body: JSON.stringify({
        flow_key: 'smart_contact',
        data: {
          input: inputUtente,
          _as_user_id: '6dff85ac-2265-4cfa-a2c0-a169401fed47'  // UUID utente tecnico
        }
      })
    }
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`FlowStarter error: ${response.status} - ${errorBody}`);
  }

  const result = await response.json();
  return result;
}

// Uso
try {
  const risposta = await inviaRichiestaFlowStarter('Ciao, ho bisogno di supporto');
  console.log('Risposta bot:', risposta.result);
} catch (error) {
  console.error('Errore:', error);
}
```

---

## ❌ ERRORI COMUNI

### Errore 1: "Chiave OpenRouter utente mancante"
**Causa:** Stai usando il token JWT invece di X-Admin-Key, oppure `_as_user_id` è sbagliato

**Soluzione:**
- ✅ Aggiungi header `X-Admin-Key`
- ✅ Usa UUID in `_as_user_id`, non email

### Errore 2: 401 Unauthorized
**Causa:** X-Admin-Key mancante o sbagliato

**Soluzione:**
- Verifica che l'header sia `X-Admin-Key` (con i trattini)
- Verifica il valore della chiave

### Errore 3: 402 Payment Required
**Causa:** L'utente tecnico non ha crediti o affordability non configurato

**Soluzione:**
- Verifica che l'app `smart_contact_form` abbia affordability=0 nella config
- Oppure aggiungi crediti all'utente Pietro

---

## 🔒 Sicurezza

**⚠️ ATTENZIONE:** La `X-Admin-Key` è una **credenziale sensibile**!

### Best practices:
1. **NON esporre la chiave nel codice frontend** lato client
2. **Usa un backend intermediario** che fa le chiamate a FlowStarter
3. **Valida gli input** prima di inoltrarli a FlowStarter
4. **Rate limiting** per prevenire abusi

### Architettura consigliata:
```
[Frontend pubblico] 
    ↓ (POST /api/contact-form)
[Tuo Backend] 
    ↓ (con X-Admin-Key)
[FlowStarter API]
```

---

## 🧪 Test con cURL

```bash
curl -X POST https://flowstarter-production.up.railway.app/core/v1/providers/flowise/execute \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM" \
  -H "X-App-Id: smart_contact_form" \
  -d '{
    "flow_key": "smart_contact",
    "data": {
      "input": "Test dal form pubblico",
      "_as_user_id": "6dff85ac-2265-4cfa-a2c0-a169401fed47"
    }
  }'
```

---

## 📊 Risposta attesa

```json
{
  "payload_sent": {
    "input": "Test dal form pubblico",
    "_as_user_id": "6dff85ac-2265-4cfa-a2c0-a169401fed47"
  },
  "result": {
    "text": "Risposta del bot AI...",
    "messageId": "..."
  },
  "pricing": {
    "status": "pending",
    "mode": "async"
  },
  "flow": {
    "flow_id": "...",
    "flow_key": "smart_contact"
  }
}
```

---

## 🔧 Troubleshooting

### Verifica configurazione affordability
```bash
curl https://flowstarter-production.up.railway.app/core/v1/admin/pricing/config \
  -H "X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM"
```

Cerca `flow_costs_usd` e verifica che `smart_contact_form: 0` sia presente.

### Verifica crediti utente tecnico
```bash
curl https://flowstarter-production.up.railway.app/core/v1/admin/users?q=pietro \
  -H "X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM"
```

---

## 📞 Supporto

In caso di problemi:
1. Verifica i log di FlowStarter su Railway
2. Controlla che il flow `smart_contact` sia configurato correttamente in Flowise
3. Verifica che l'utente Pietro abbia la chiave OpenRouter provisionata

**Utente tecnico:**
- UUID: `6dff85ac-2265-4cfa-a2c0-a169401fed47`
- Email: `pietrobonomo22@gmail.com`
- OpenRouter key: `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`

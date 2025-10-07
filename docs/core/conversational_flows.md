# 🔗 Flow Conversazionali - Gestione Sessioni

## 📋 Panoramica

FlowStarter supporta sia **flow stateless** (ogni chiamata è indipendente) che **flow conversazionali** (mantengono il contesto tra chiamate successive).

---

## 🎯 Casi d'uso

### Flow Stateless (Default)
- ✅ Generazione contenuti one-shot
- ✅ Traduzioni
- ✅ Analisi singoli testi
- ✅ Ogni esecuzione è indipendente

**Esempio:** "Genera un post Instagram su AI"

### Flow Conversazionali
- ✅ Customer service bot
- ✅ Assistenti virtuali
- ✅ Chat multi-turno
- ✅ Mantiene memoria della conversazione

**Esempio:** Chat di supporto dove il bot ricorda il nome e il contesto

---

## ⚙️ Configurazione

### 1️⃣ Configurare il Flow come Conversazionale

#### Via Admin API

```bash
POST /core/v1/admin/flow-configs
X-Admin-Key: your-admin-key
Content-Type: application/json

{
  "app_id": "my_app",
  "flow_key": "customer_support",
  "flow_id": "flowise-flow-uuid",
  "node_names": ["agentAgentflow_0"],
  "is_conversational": true  ✅
}
```

#### Via Dashboard Admin (Coming Soon)
La dashboard admin avrà un toggle per abilitare/disabilitare la modalità conversazionale per ogni flow.

---

## 💻 Utilizzo

### Prima Chiamata (Nuova Conversazione)

```typescript
const response = await fetch('https://your-api.com/core/v1/providers/flowise/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN',
    'X-App-Id': 'my_app'
  },
  body: JSON.stringify({
    flow_key: 'customer_support',
    data: {
      input: 'Ciao, il mio nome è Marco e ho un problema con un ordine'
    }
    // ⚠️ NO session_id → nuova conversazione
  })
});

const result = await response.json();

// Salva session_id per le prossime chiamate
const sessionId = result.flow.session_id;  // es: "43db4e86-39e3-41e9-92a7-cc5bed84452b"
const isConversational = result.flow.is_conversational;  // true
```

### Chiamate Successive (Stessa Conversazione)

```typescript
const response2 = await fetch('https://your-api.com/core/v1/providers/flowise/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN',
    'X-App-Id': 'my_app'
  },
  body: JSON.stringify({
    flow_key: 'customer_support',
    session_id: sessionId,  // ✅ Usa il session_id precedente
    data: {
      input: 'Ti ricordi come mi chiamo?'
    }
  })
});

// Il bot risponderà "Marco" perché mantiene il contesto
```

---

## 📊 Risposta API

### Struttura Risposta

```json
{
  "result": {
    "text": "Risposta del bot...",
    "chatId": "43db4e86-39e3-41e9-92a7-cc5bed84452b",
    "sessionId": "43db4e86-39e3-41e9-92a7-cc5bed84452b"
  },
  "pricing": { /* ... */ },
  "flow": {
    "flow_id": "flowise-flow-uuid",
    "flow_key": "customer_support",
    "is_conversational": true,  ✅
    "session_id": "43db4e86-39e3-41e9-92a7-cc5bed84452b"  ✅
  }
}
```

### Campi Importanti

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `flow.is_conversational` | `boolean` | Se `true`, il flow supporta sessioni |
| `flow.session_id` | `string` | ID della sessione da usare nelle prossime chiamate |
| `result.sessionId` | `string` | Alias di `flow.session_id` (da Flowise) |
| `result.chatId` | `string` | ID chat Flowise (equivalente a session_id) |

---

## 🔄 Gestione Sessioni Lato Client

### Esempio React

```typescript
import { useState } from 'react';

function ChatBot() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  async function sendMessage(input: string) {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        flow_key: 'customer_support',
        session_id: sessionId,  // null alla prima chiamata
        data: { input }
      })
    });

    const result = await response.json();
    
    // Salva session_id dalla prima risposta
    if (!sessionId && result.flow.session_id) {
      setSessionId(result.flow.session_id);
    }

    // Aggiungi messaggio alla conversazione
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: result.result.text
    }]);
  }

  function startNewConversation() {
    setSessionId(null);  // Reset → prossima chiamata crea nuova sessione
    setMessages([]);
  }

  // ...
}
```

---

## 🔧 Come Funziona

### Backend (FlowStarter)

1. **Configurazione:** Il flow ha `is_conversational: true` in `flow_configs`
2. **Richiesta:** Se viene passato `session_id`, viene inoltrato a Flowise
3. **Flowise:** Gestisce la memoria conversazionale usando `sessionId`
4. **Risposta:** FlowStarter estrae e ritorna il `session_id` dalla risposta Flowise

### Flowise

Flowise mantiene automaticamente la storia della chat quando riceve un `sessionId`:

```json
{
  "question": "Ti ricordi il mio nome?",
  "sessionId": "43db4e86-39e3-41e9-92a7-cc5bed84452b"
}
```

---

## ❓ FAQ

### Q: Cosa succede se non passo session_id per un flow conversazionale?
**A:** Viene creata una nuova conversazione. Il `session_id` verrà generato da Flowise e ritornato nella risposta.

### Q: Cosa succede se passo session_id per un flow NON conversazionale?
**A:** Il `session_id` viene ignorato. Ogni chiamata è indipendente.

### Q: Per quanto tempo è valido un session_id?
**A:** Dipende dalla configurazione di Flowise. Di default, le sessioni persistono finché non vengono eliminate manualmente o expire secondo le policy di Flowise.

### Q: Posso usare lo stesso session_id per utenti diversi?
**A:** ⚠️ **NO!** Ogni utente deve avere il proprio `session_id`. Non condividere mai session_id tra utenti diversi per motivi di privacy e sicurezza.

### Q: Come elimino una sessione?
**A:** Per ora le sessioni vengono gestite automaticamente da Flowise. In futuro potremmo aggiungere un endpoint per eliminare sessioni specifiche.

---

## 🧪 Testing

### Test Manuale

Usa lo script fornito:

```bash
python scripts/test_conversational_flow.py
```

Lo script:
1. Configura il flow come conversazionale
2. Invia un primo messaggio ("Mi chiamo Marco")
3. Invia un secondo messaggio nella stessa sessione ("Ti ricordi il mio nome?")
4. Verifica che il bot ricordi il contesto
5. Invia un messaggio in una nuova sessione per verificare l'isolamento

---

## 🔐 Sicurezza

### Best Practices

1. **Isolamento Sessioni:** Ogni utente deve avere il proprio `session_id`
2. **Validazione:** Valida che l'utente sia autorizzato ad accedere al `session_id` richiesto
3. **Storage Sicuro:** Non esporre `session_id` in URL o log pubblici
4. **Timeout:** Considera di implementare timeout per sessioni inattive

### Esempio Backend Sicuro

```typescript
// ❌ SBAGLIATO: session_id nell'URL
app.get('/chat/:sessionId', ...)

// ✅ CORRETTO: session_id nel body + autenticazione
app.post('/chat', authenticateUser, async (req, res) => {
  const { session_id, input } = req.body;
  const user_id = req.user.id;
  
  // Verifica che la sessione appartenga all'utente
  if (session_id) {
    const session = await getSession(session_id);
    if (session.user_id !== user_id) {
      return res.status(403).json({ error: 'Unauthorized' });
    }
  }
  
  // Procedi con la chiamata...
});
```

---

## 📦 Database Schema

### Tabella `flow_configs`

```sql
ALTER TABLE public.flow_configs 
ADD COLUMN is_conversational boolean DEFAULT false;
```

### Tabella `flow_sessions` (Tracking Opzionale)

```sql
CREATE TABLE public.flow_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id text NOT NULL,
  user_id uuid REFERENCES profiles(id),
  app_id text NOT NULL,
  flow_key text NOT NULL,
  flow_id text NOT NULL,
  first_message_at timestamptz DEFAULT now(),
  last_message_at timestamptz DEFAULT now(),
  message_count integer DEFAULT 1,
  metadata jsonb DEFAULT '{}',
  UNIQUE(session_id, user_id)
);
```

**Nota:** La tabella `flow_sessions` è opzionale e serve solo per analytics/debugging.

---

## 🚀 Roadmap

- [ ] Dashboard UI per abilitare/disabilitare conversazioni
- [ ] Endpoint per elencare sessioni attive di un utente
- [ ] Endpoint per eliminare sessioni
- [ ] Analytics sessioni (durata media, messaggi per sessione, ecc.)
- [ ] Limiti configur per sessione (max messaggi, max durata)
- [ ] Export conversazioni per training/audit

---

## 📚 Riferimenti

- [Flowise Session Management](https://docs.flowiseai.com)
- [Public Form Integration Guide](./public_form_integration.md)
- [Admin API Reference](../../README.md#admin-endpoints)

# 🔧 Modifiche Necessarie per Form Conversazionale

## ✅ COSA FUNZIONA GIÀ

- ✅ FlowStarter è configurato e funzionante
- ✅ Flow `smart_contact` è conversazionale
- ✅ Credenziali corrette (X-Admin-Key, UUID utente)
- ✅ Backend FlowStarter mantiene le sessioni

---

## 🎯 COSA DOVETE MODIFICARE NEL VOSTRO CODICE

### 📝 MODIFICHE MINIME RICHIESTE

#### 1️⃣ **Salvare il `session_id` dalla Prima Risposta**

**PRIMA (attuale):**
```javascript
const response = await fetch(FLOWSTARTER_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Admin-Key': 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',
    'X-App-Id': 'smart_contact_form'
  },
  body: JSON.stringify({
    flow_key: 'smart_contact',
    data: {
      input: userMessage,
      _as_user_id: '6dff85ac-2265-4cfa-a2c0-a169401fed47'
    }
  })
});

const result = await response.json();
const botMessage = result.result.text;
// ❌ NON salva il session_id
```

**DOPO (modificato):**
```javascript
const response = await fetch(FLOWSTARTER_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Admin-Key': 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',
    'X-App-Id': 'smart_contact_form'
  },
  body: JSON.stringify({
    flow_key: 'smart_contact',
    session_id: currentSessionId,  // ✅ AGGIUNTO: passa se esiste
    data: {
      input: userMessage,
      _as_user_id: '6dff85ac-2265-4cfa-a2c0-a169401fed47'
    }
  })
});

const result = await response.json();
const botMessage = result.result.text;
const sessionId = result.flow.session_id;  // ✅ AGGIUNTO: salva per prossime chiamate

// ✅ AGGIUNTO: Salva in state/localStorage
if (sessionId && !currentSessionId) {
  currentSessionId = sessionId;
  localStorage.setItem('chatSessionId', sessionId);  // Opzionale: persiste tra reload
}
```

---

#### 2️⃣ **Gestire il Session ID nello State**

Aggiungere una variabile per tracciare la sessione corrente:

```javascript
// Nel componente del form/chat
let currentSessionId = null;  // O useState in React

// All'inizio (opzionale): riprendi sessione da localStorage
currentSessionId = localStorage.getItem('chatSessionId');
```

---

#### 3️⃣ **Bottone "Nuova Conversazione"** (Opzionale)

Permettere all'utente di resettare la conversazione:

```javascript
function startNewConversation() {
  currentSessionId = null;
  localStorage.removeItem('chatSessionId');
  // Pulisci anche la cronologia messaggi mostrata
}
```

---

## 💻 ESEMPIO COMPLETO (React)

```jsx
import { useState } from 'react';

function ChatForm() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  async function sendMessage() {
    if (!input.trim()) return;
    
    const userMessage = input.trim();
    setInput('');
    
    // Aggiungi messaggio utente alla UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    
    try {
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
            session_id: sessionId,  // ✅ null alla prima chiamata, poi riutilizza
            data: {
              input: userMessage,
              _as_user_id: '6dff85ac-2265-4cfa-a2c0-a169401fed47'
            }
          })
        }
      );
      
      const result = await response.json();
      
      // ✅ Salva session_id dalla prima risposta
      if (!sessionId && result.flow.session_id) {
        setSessionId(result.flow.session_id);
        console.log('✅ Session started:', result.flow.session_id);
      }
      
      // Aggiungi risposta bot
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: result.result.text 
      }]);
      
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: 'Errore di connessione' 
      }]);
    }
  }

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
      ))}
      
      <input 
        value={input} 
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      
      <button onClick={sendMessage}>Invia</button>
      
      {sessionId && (
        <button onClick={() => setSessionId(null)}>
          Nuova Conversazione
        </button>
      )}
    </div>
  );
}
```

---

## 🔑 CAMPI RICHIESTI NEL PAYLOAD

```javascript
{
  "flow_key": "smart_contact",           // ✅ Già presente
  "session_id": "uuid-o-null",           // ✅ AGGIUNGERE QUESTO
  "data": {
    "input": "messaggio utente",        // ✅ Già presente
    "_as_user_id": "6dff85ac-2265..."   // ✅ Già presente
  }
}
```

---

## 📊 RISPOSTA API MODIFICATA

**Prima:**
```json
{
  "result": {
    "text": "Risposta bot..."
  }
}
```

**Ora:**
```json
{
  "result": {
    "text": "Risposta bot..."
  },
  "flow": {
    "is_conversational": true,         // ✅ NUOVO
    "session_id": "uuid-sessione"      // ✅ NUOVO - SALVARE QUESTO!
  }
}
```

---

## 🧪 TEST RICHIESTI

### Test 1: Prima Chiamata
```javascript
// NO session_id nel payload
{ flow_key: "smart_contact", data: { input: "Ciao, mi chiamo Marco" } }
```
**Verificare:** Risposta include `flow.session_id` ✅

### Test 2: Seconda Chiamata
```javascript
// CON session_id salvato
{ 
  flow_key: "smart_contact", 
  session_id: "SAVED_FROM_FIRST_CALL",
  data: { input: "Ti ricordi il mio nome?" } 
}
```
**Verificare:** Bot risponde "Marco" ✅

### Test 3: Nuova Conversazione
```javascript
// SENZA session_id (reset)
{ flow_key: "smart_contact", data: { input: "Come mi chiamo?" } }
```
**Verificare:** Bot non ricorda (nuovo session_id) ✅

---

## ⚠️ NOTE IMPORTANTI

1. **Session ID è opzionale** - Se non lo passate, Flowise crea una nuova conversazione
2. **Non serve autenticazione diversa** - Continuate a usare X-Admin-Key come prima
3. **Backend intermediario consigliato** - Non esponete X-Admin-Key nel frontend
4. **Persistenza** - Decidete voi se salvare sessionId in localStorage o solo in memoria

---

## 📞 SUPPORTO

Se riscontrate problemi:
1. Verificate che `result.flow.session_id` sia presente nella risposta
2. Controllate i log browser per vedere il session_id inviato/ricevuto
3. Testate prima in dev/staging prima di andare in produzione

---

**Modifiche minime richieste: 5-10 righe di codice! 🚀**















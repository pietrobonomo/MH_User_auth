# 📋 Istruzioni per Integrare Form Conversazionale

## 🎯 Obiettivo
Implementare un form di customer service che **mantiene la conversazione** tra messaggi successivi, permettendo al bot di ricordare il contesto (nome utente, problema discusso, etc.).

---

## 🔑 Credenziali FlowStarter

```javascript
const FLOWSTARTER_CONFIG = {
  apiUrl: 'https://flowstarter-production.up.railway.app',
  adminKey: 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM',
  technicalUserId: '6dff85ac-2265-4cfa-a2c0-a169401fed47',
  appId: 'smart_contact_form',
  flowKey: 'smart_contact'
};
```

⚠️ **IMPORTANTE:** Non esporre `adminKey` nel frontend! Usare un backend intermediario.

---

## 🏗️ Architettura Consigliata

```
[Form Frontend] 
    ↓ POST /api/chat (senza admin key)
[Vostro Backend] 
    ↓ POST /core/v1/providers/flowise/execute (con admin key)
[FlowStarter API]
    ↓
[Bot AI]
```

### Perché serve il backend?
- ✅ Proteggere la `adminKey`
- ✅ Validare input utente
- ✅ Rate limiting
- ✅ Log e analytics

---

## 💻 CODICE DA IMPLEMENTARE

### 1️⃣ Backend (Node.js/Express)

```javascript
// /api/chat endpoint
app.post('/api/chat', async (req, res) => {
  const { message, sessionId } = req.body;
  
  // Validazione input
  if (!message || message.trim().length === 0) {
    return res.status(400).json({ error: 'Message is required' });
  }
  
  if (message.length > 1000) {
    return res.status(400).json({ error: 'Message too long' });
  }
  
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
          session_id: sessionId || undefined,  // Passa solo se esiste
          data: {
            input: message,
            _as_user_id: '6dff85ac-2265-4cfa-a2c0-a169401fed47'
          }
        })
      }
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('FlowStarter error:', response.status, errorText);
      return res.status(response.status).json({ 
        error: 'Failed to get bot response' 
      });
    }
    
    const data = await response.json();
    
    // Estrai dati importanti
    const botResponse = data.result?.text || '';
    const newSessionId = data.flow?.session_id;
    const isConversational = data.flow?.is_conversational;
    
    // Log per debug (opzionale)
    console.log('Bot response:', {
      sessionId: newSessionId,
      conversational: isConversational,
      responseLength: botResponse.length
    });
    
    // Ritorna risposta pulita al frontend
    res.json({
      message: botResponse,
      sessionId: newSessionId,
      isConversational: isConversational
    });
    
  } catch (error) {
    console.error('Error calling FlowStarter:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

---

### 2️⃣ Frontend (React)

```jsx
import { useState, useRef, useEffect } from 'react';

function ChatForm() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Auto-scroll ai nuovi messaggi
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;
    
    const userMessage = input.trim();
    setInput('');
    
    // Aggiungi messaggio utente alla UI
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }]);
    
    setLoading(true);
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          sessionId: sessionId  // null alla prima chiamata
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Salva sessionId dalla prima risposta
      if (!sessionId && data.sessionId) {
        setSessionId(data.sessionId);
        console.log('✅ Session started:', data.sessionId);
      }
      
      // Aggiungi risposta bot alla UI
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.message,
        timestamp: new Date()
      }]);
      
    } catch (error) {
      console.error('Error:', error);
      
      // Mostra errore all'utente
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'error',
        content: 'Errore di connessione. Riprova.',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };
  
  const startNewConversation = () => {
    if (window.confirm('Vuoi iniziare una nuova conversazione?')) {
      setSessionId(null);
      setMessages([]);
      console.log('🆕 New conversation started');
    }
  };
  
  return (
    <div className="chat-container">
      {/* Header con info sessione */}
      <div className="chat-header">
        <h2>Customer Support</h2>
        {sessionId && (
          <button onClick={startNewConversation} className="new-chat-btn">
            Nuova Conversazione
          </button>
        )}
      </div>
      
      {/* Lista messaggi */}
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            👋 Ciao! Come posso aiutarti?
          </div>
        )}
        
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`message message-${msg.role}`}
          >
            <div className="message-content">
              {msg.content}
            </div>
            <div className="message-time">
              {msg.timestamp.toLocaleTimeString('it-IT', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message message-assistant loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Form input */}
      <form onSubmit={sendMessage} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Scrivi un messaggio..."
          disabled={loading}
          maxLength={1000}
          className="message-input"
        />
        <button 
          type="submit" 
          disabled={loading || !input.trim()}
          className="send-button"
        >
          {loading ? '...' : 'Invia'}
        </button>
      </form>
      
      {/* Debug info (rimuovere in produzione) */}
      {process.env.NODE_ENV === 'development' && sessionId && (
        <div className="debug-info">
          Session ID: {sessionId.substring(0, 8)}...
        </div>
      )}
    </div>
  );
}

export default ChatForm;
```

---

### 3️⃣ CSS Minimale

```css
.chat-container {
  max-width: 600px;
  margin: 0 auto;
  height: 600px;
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  padding: 1rem;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #fff;
}

.message {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  max-width: 80%;
}

.message-user {
  background: #007bff;
  color: white;
  margin-left: auto;
  text-align: right;
}

.message-assistant {
  background: #f1f1f1;
  color: #333;
  margin-right: auto;
}

.message-error {
  background: #f8d7da;
  color: #721c24;
  margin: 0 auto;
  text-align: center;
}

.input-form {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #ddd;
  background: #f5f5f5;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 0.5rem;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-10px);
  }
}
```

---

## 🧪 COME TESTARE

### Test 1: Prima Conversazione

```javascript
// Prima chiamata
POST /api/chat
{
  "message": "Ciao, il mio nome è Marco e ho un problema con un ordine"
}

// Risposta attesa:
{
  "message": "Ciao Marco! Mi dispiace per il problema...",
  "sessionId": "43db4e86-39e3-41e9-92a7-cc5bed84452b",  // ⬅️ SALVARE
  "isConversational": true
}
```

### Test 2: Messaggio nella Stessa Conversazione

```javascript
// Seconda chiamata (con sessionId)
POST /api/chat
{
  "message": "Ti ricordi come mi chiamo?",
  "sessionId": "43db4e86-39e3-41e9-92a7-cc5bed84452b"  // ⬅️ STESSO ID
}

// Risposta attesa:
{
  "message": "Certo, ti chiami Marco!",  // ⬅️ Ricorda il nome
  "sessionId": "43db4e86-39e3-41e9-92a7-cc5bed84452b",
  "isConversational": true
}
```

### Test 3: Nuova Conversazione

```javascript
// Terza chiamata (SENZA sessionId)
POST /api/chat
{
  "message": "Come mi chiamo?"
  // ⬅️ NO sessionId
}

// Risposta attesa:
{
  "message": "Non lo so, non me l'hai ancora detto",  // ⬅️ NON ricorda
  "sessionId": "9f3e2d1c-8b7a-4e5f-9d8c-7e6f5a4b3c2d",  // ⬅️ NUOVO ID
  "isConversational": true
}
```

---

## 🐛 TROUBLESHOOTING

### Problema: `sessionId` sempre `null`

**Causa:** Il flow non è configurato come conversazionale

**Soluzione:** Verificare la configurazione:
```bash
curl https://flowstarter-production.up.railway.app/core/v1/admin/flow-configs/all?app_id=smart_contact_form \
  -H "X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM"
```

Deve contenere:
```json
{
  "is_conversational": true  // ⬅️ Deve essere true
}
```

Se è `false`, riconfigurare:
```bash
curl -X POST https://flowstarter-production.up.railway.app/core/v1/admin/flow-configs \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM" \
  -d '{
    "app_id": "smart_contact_form",
    "flow_key": "smart_contact",
    "flow_id": "74f8532c-cc6a-428d-82c8-be622591fc64",
    "node_names": ["agentAgentflow_0"],
    "is_conversational": true
  }'
```

### Problema: Bot non ricorda il contesto

**Possibili cause:**
1. `sessionId` non viene passato correttamente
2. Il bot Flowise non ha memoria abilitata
3. Si sta usando un `sessionId` diverso

**Debug:** Aggiungere log nel backend:
```javascript
console.log('Sending to FlowStarter:', {
  sessionId: sessionId || 'NEW',
  message: message.substring(0, 50)
});
```

### Problema: Errore 502 Bad Gateway

**Causa:** Chiave OpenRouter mancante per l'utente tecnico

**Verifica:** L'utente `pietrobonomo22@gmail.com` deve avere la chiave OpenRouter provisionata.

---

## 📊 METRICHE DA MONITORARE

Suggerisco di tracciare:
- ✅ Numero di conversazioni avviate (nuovi `sessionId`)
- ✅ Durata media conversazione (tempo tra primo e ultimo messaggio)
- ✅ Numero medio di messaggi per conversazione
- ✅ Rate di errori (502, 400, etc.)

```javascript
// Esempio log analytics
analytics.track('chat_message_sent', {
  sessionId: sessionId,
  messageCount: messages.length,
  isFirstMessage: !sessionId
});
```

---

## 🔐 SICUREZZA

### ⚠️ IMPORTANTE

1. **MAI esporre `adminKey` nel frontend**
2. **Rate limiting sul backend** (es. max 10 msg/minuto per IP)
3. **Validazione input** (lunghezza max, caratteri pericolosi)
4. **Timeout** (max 60s per richiesta a FlowStarter)
5. **Sanitizzazione output** (evitare XSS se il bot ritorna HTML)

### Esempio Rate Limiting (Express)

```javascript
const rateLimit = require('express-rate-limit');

const chatLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minuto
  max: 10, // max 10 richieste
  message: 'Troppi messaggi, riprova tra un minuto'
});

app.post('/api/chat', chatLimiter, async (req, res) => {
  // ...
});
```

---

## 📞 SUPPORTO

In caso di problemi:
1. Verificare i log backend per errori FlowStarter
2. Controllare che il flow sia configurato con `is_conversational: true`
3. Verificare che `sessionId` venga salvato e passato correttamente
4. Testare manualmente con cURL (vedi esempi sotto)

### Test Manuale con cURL

```bash
# Test completo end-to-end
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Ciao, mi chiamo Marco"}'

# Copia il sessionId dalla risposta e usalo qui:
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Ti ricordi il mio nome?", "sessionId": "PASTE_SESSION_ID_HERE"}'
```

---

## ✅ CHECKLIST IMPLEMENTAZIONE

- [ ] Backend endpoint `/api/chat` implementato
- [ ] `adminKey` protetta (non nel frontend)
- [ ] Frontend gestisce `sessionId` correttamente
- [ ] UI mostra conversazione (messaggi user/bot)
- [ ] Pulsante "Nuova conversazione" funzionante
- [ ] Rate limiting implementato
- [ ] Validazione input implementata
- [ ] Gestione errori (502, timeout, etc.)
- [ ] Testing su device mobili
- [ ] CSS responsive
- [ ] Log/analytics configurati

---

**Buon lavoro! 🚀**

# 🚀 Flow Starter - Core API Platform

## Cos'è Flow Starter?

**Flow Starter** è un'API Core standalone progettata per essere il "cervello centrale" di applicazioni SaaS che utilizzano AI generativa. È un sistema di **backend-as-a-service specializzato** che gestisce autenticazione, crediti, pricing dinamico e proxy intelligente verso provider AI esterni come OpenRouter e Flowise/NL-Flow.

### Il Problema che Risolve

Sviluppare un'applicazione AI richiede:
- ✅ **Autenticazione sicura** con JWT e gestione utenti
- ✅ **Sistema crediti** per monetizzare l'utilizzo AI
- ✅ **Pricing dinamico** che si adatta ai costi reali dei provider
- ✅ **Proxy intelligente** che nasconde le complessità dei provider AI
- ✅ **Billing integrato** con webhook e gestione pagamenti
- ✅ **Multi-tenancy** per gestire più applicazioni

**Flow Starter risolve tutto questo in un'unica piattaforma pronta all'uso.**

---

## 🎯 Caratteristiche Principali

### 1. **Sistema Crediti Avanzato**
- **Ledger atomico** con transazioni sicure via PostgreSQL
- **Pre-check affordability** che blocca operazioni costose se crediti insufficienti
- **Addebito reale** basato sul consumo effettivo dei provider AI
- **Idempotency** per evitare addebiti duplicati

### 2. **Pricing Dinamico & Business Intelligence**
- **Dashboard Business** integrata per simulazioni di pricing
- **Costi fissi configurabili** (infrastruttura, marketing, supporto)
- **Margini target** personalizzabili per sostenibilità economica
- **Override per flow** specifici con costi personalizzati
- **Proiezioni mensili** basate su MAU e mix operazioni

### 3. **Proxy AI Intelligente**
- **OpenRouter Integration**: Chat completion con modelli all'avanguardia
- **Flowise/NL-Flow Proxy**: Esecuzione di workflow AI complessi
- **Chiavi utente isolate**: Ogni utente ha la propria API key OpenRouter
- **Timeout e retry** intelligenti per affidabilità

### 4. **Multi-Tenancy Nativo**
- **App ID separation**: Gestione di più applicazioni su un singolo Core
- **Flow configurations**: Mapping flow_key → flow_id per app
- **Pricing per-app**: Configurazioni separate per ogni applicazione
- **Affordability per-app**: Soglie minime personalizzabili

### 5. **Billing Provider-Agnostico**
- **LemonSqueezy** integrato out-of-the-box
- **Webhook sicuri** con verifica signature
- **Architettura estendibile** per altri provider (Stripe, Paddle)
- **Transazioni atomiche** con rollback automatico

---

## 🏗️ Architettura Tecnica

### Stack Core
- **FastAPI** 0.109.2 - Framework web moderno e performante
- **Supabase** - Database PostgreSQL con autenticazione JWT
- **Pydantic** 2.6.3 - Validazione dati e type safety
- **HTTPX** - Client HTTP asincrono per provider esterni

### Schema Database
```sql
-- Gestione utenti e crediti
public.profiles (id, email, credits, openrouter_api_key)
public.credit_transactions (ledger atomico)

-- Multi-tenancy
public.flow_configs (app_id, flow_key, flow_id, node_names)
public.pricing_configs (app_id, config)

-- Billing
public.billing_transactions (provider-agnostico)
public.billing_webhook_logs (audit trail)
```

### Sicurezza
- **Row Level Security (RLS)** su tutte le tabelle
- **JWT verification** via Supabase JWKS
- **API Keys isolation** - chiavi utente mai esposte al client
- **Webhook signature verification** per billing
- **Service role access** per operazioni privilegiate

---

## 📊 Dashboard Business Integrata

### Funzionalità
- **📈 Simulazioni Pricing**: Modifica margini e costi in tempo reale
- **💰 Proiezioni Revenue**: Calcola ricavi basati su MAU e utilizzo
- **⚙️ Override Flow**: Personalizza costi per workflow specifici
- **📋 Scenario Management**: Salva e carica configurazioni di test
- **📤 Import/Export**: Backup e condivisione configurazioni

### Metriche Calcolate
- **Overhead Multiplier**: Basato su costi fissi vs revenue target
- **Final Credit Multiplier**: Conversione USD→Crediti con margini
- **Gross Margin %**: Margine lordo su mix operazioni
- **Break-even Analysis**: Punto di pareggio per sostenibilità

---

## 🚀 Casi d'Uso Ideali

### 1. **SaaS AI Content Generation**
- Blog post automatici, social media content
- SEO optimization, marketing copy
- **Esempio**: InsightDesk per content marketing

### 2. **AI-Powered Analytics Platforms**
- Analisi sentiment, topic modeling
- Report automatici, insights generation
- **Beneficio**: Costi prevedibili con pricing trasparente

### 3. **Chatbot e Virtual Assistant**
- Customer support, lead qualification
- Multi-model routing per ottimizzazione costi
- **Vantaggio**: Scaling automatico con controllo budget

### 4. **Document Processing Services**
- OCR, summarization, translation
- Workflow complessi con multiple AI calls
- **Plus**: Affordability check previene overspending

---

## 💡 Vantaggi Competitivi

### Per Sviluppatori
- **🚀 Time-to-Market**: Setup in minuti, non settimane
- **🔧 Configurazione Zero**: Tutto via API e dashboard
- **📱 Multi-Platform**: REST API compatibile con qualsiasi frontend
- **🧪 Testing Friendly**: Stub mode per sviluppo senza costi

### Per Business
- **💰 Controllo Costi**: Pricing dinamico basato su metriche reali
- **📊 Trasparenza**: Dashboard completa per business intelligence
- **🎯 Scalabilità**: Da MVP a enterprise senza refactoring
- **🔒 Compliance**: Audit trail completo per transazioni

### Per Utenti Finali
- **⚡ Performance**: Proxy ottimizzato con timeout intelligenti
- **🛡️ Affidabilità**: Sistema di retry e fallback automatici
- **💳 Pagamenti Sicuri**: Integrazione billing provider certificati
- **🌍 Multi-Region**: Supporto deployment globale

---

## 🛠️ Quick Start (5 minuti)

### 1. Setup Supabase
```bash
# Crea progetto su supabase.com
# Esegui SQL schema: flow_starter/sql/000_full_schema.sql
```

### 2. Configurazione
```bash
# Copia template
cp .env.example .env

# Configura variabili
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
OPENROUTER_PROVISIONING_KEY=your-openrouter-key
```

### 3. Avvio
```bash
# Installa dipendenze
pip install -r requirements.txt

# Avvia server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 5050
```

### 4. Test
```bash
# Health check
curl http://127.0.0.1:5050/health

# Dashboard business
open http://127.0.0.1:5050/core/v1/admin-ui/business-dashboard
```

---

## 📈 Roadmap & Estensioni

### Immediate (Q1 2024)
- [ ] **Stripe Integration** - Alternativa a LemonSqueezy
- [ ] **Usage Analytics** - Dashboard metriche utilizzo
- [ ] **Rate Limiting** - Protezione anti-abuse
- [ ] **Caching Layer** - Redis per performance

### Medium Term (Q2-Q3 2024)
- [ ] **White-label UI** - Dashboard brandizzabile
- [ ] **A/B Testing** - Pricing experiments
- [ ] **Advanced Billing** - Subscription management
- [ ] **API Gateway** - Routing intelligente

### Long Term (Q4 2024+)
- [ ] **ML Cost Prediction** - Predizione costi AI
- [ ] **Auto-scaling** - Scaling automatico risorse
- [ ] **Marketplace** - Ecosystem di flow condivisi
- [ ] **Enterprise SSO** - SAML, OIDC integration

---

## 🎯 Target Market

### Primary
- **🚀 Startup AI**: Team 2-10 persone che vogliono focus sul prodotto
- **💼 Digital Agencies**: Agenzie che offrono servizi AI ai clienti
- **🏢 SMB SaaS**: Aziende che vogliono aggiungere AI ai prodotti esistenti

### Secondary
- **🎓 Indie Hackers**: Sviluppatori che monetizzano progetti AI
- **🔬 Research Teams**: Laboratori che testano modelli AI
- **🏛️ Enterprise**: Grandi aziende per POC e prototipi

---

## 💰 Modello di Business

### Pricing Strategy
- **🆓 Open Source Core**: Codice base gratuito e modificabile
- **☁️ Hosted Service**: Servizio gestito con SLA e supporto
- **🏢 Enterprise License**: Deployment on-premise con supporto dedicato
- **🛠️ Professional Services**: Customizzazione e integrazione

### Revenue Streams
1. **Subscription Tiers**: Free, Pro, Enterprise
2. **Usage-based**: Costo per API call oltre soglie incluse
3. **Professional Services**: Setup, training, customizzazione
4. **Marketplace Commission**: Revenue share su flow premium

---

## 🌟 Conclusioni

**Flow Starter non è solo un'API - è una piattaforma completa** che permette agli sviluppatori di concentrarsi sulla logica di business invece che sull'infrastruttura.

### Perché Scegliere Flow Starter?

✅ **Riduce il time-to-market del 80%** per applicazioni AI  
✅ **Elimina la complessità** di pricing, billing e multi-tenancy  
✅ **Scala automaticamente** da MVP a milioni di utenti  
✅ **Controllo totale** su costi e margini tramite dashboard  
✅ **Sicurezza enterprise-grade** con audit trail completo  

### Call to Action

**Pronto a trasformare la tua idea AI in un business scalabile?**

1. 🚀 **[Setup in 5 minuti](docs/core/setup_supabase.md)** - Segui la guida quick start
2. 💡 **[Esplora la Demo](http://127.0.0.1:5050/docs)** - Test gli endpoint in Swagger
3. 📊 **[Configura il Business](http://127.0.0.1:5050/core/v1/admin-ui/business-dashboard)** - Ottimizza pricing e margini
4. 🎯 **Deploy in Produzione** - Railway, Vercel, o la tua infrastruttura preferita

---

*Flow Starter - Dove l'AI incontra il Business* 🤖💼





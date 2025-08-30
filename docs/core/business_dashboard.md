## Business Dashboard (Pricing) – Guida Completa

Questa guida spiega come usare la Business Dashboard per configurare il pricing, simulare i moltiplicatori e generare proiezioni mensili basate sul tuo modello di business.

- URL locale: `http://127.0.0.1:5050/core/v1/admin-ui/business-dashboard`
- Requisito: Bearer Token Supabase valido (incollalo nel campo in alto).

### Obiettivi della Dashboard
- Configurare `pricing_config.json` senza editare manualmente file JSON
- Calcolare e visualizzare moltiplicatori di prezzo basati su costi e margini
- Definire override dei costi per singolo flow (per `flow_key` o `flow_id`)
- Simulare proiezioni mensili su base MAU, operazioni/utente e mix di flow
- Salvare/caricare scenari e importare/esportare configurazioni

---

## Autenticazione

- Inserisci il Bearer Token nell’input “Bearer Token”.
- Il token viene usato per chiamare le API admin del Core.
- Errori comuni:
  - 401/403: token mancante/invalidato
  - 422: header non valido o payload incoerente

Suggerimento: il token inserito è salvato in localStorage come `flowstarter_last_token`.

---

## Configurazione di base (pricing_config.json)

Il file di configurazione è letto e scritto dal Core. Percorso default:
- `flow_starter/data/config/pricing_config.json`
- Variabile ambiente alternativa: `PRICING_CONFIG_FILE`

Struttura esempio:
```json
{
  "monthly_revenue_target_usd": 10000.0,
  "fixed_monthly_costs_usd": [
    { "name": "Infrastructure (Railway, Vercel)", "cost_usd": 50.0 },
    { "name": "Payment Processor (Stripe/Lemon)", "cost_usd": 50.0 },
    { "name": "Business & Marketing", "cost_usd": 2500.0 },
    { "name": "Support & Maintenance", "cost_usd": 1000.0 },
    { "name": "Legal & Accounting", "cost_usd": 200.0 },
    { "name": "development tools", "cost_usd": 200.0 }
  ],
  "usd_to_credits": 100.0,
  "target_margin_multiplier": 2.5,
  "flow_costs_usd": {
    "X-post": 0.001754
  },
  "minimum_operation_cost_credits": 0.01
}
```

### Campi e significato
- **monthly_revenue_target_usd**: obiettivo di ricavi mensili (USD)
- **fixed_monthly_costs_usd[]**: elenco dei costi fissi mensili (USD)
- **usd_to_credits**: fattore di conversione (es. 1 USD = 100 crediti)
- **target_margin_multiplier**: moltiplicatore di margine target complessivo (es. 2.5x)
- **flow_costs_usd {key: usd}**: override costo base in USD per flow (per `flow_key` o `flow_id`)
- **minimum_operation_cost_credits**: soglia minima in crediti per un’operazione

---

## API di configurazione

- GET config: `GET /core/v1/admin/pricing/config`
- PUT config: `PUT /core/v1/admin/pricing/config`

Esempio GET:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:5050/core/v1/admin/pricing/config | jq
```

Esempio PUT (aggiorna config):
```bash
curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "monthly_revenue_target_usd": 8000,
    "fixed_monthly_costs_usd": [{"name":"Infra","cost_usd":100}],
    "usd_to_credits": 100,
    "target_margin_multiplier": 2.0,
    "minimum_operation_cost_credits": 0.01,
    "flow_costs_usd": {"X-post": 0.0015}
  }' \
  http://127.0.0.1:5050/core/v1/admin/pricing/config | jq
```

---

## Logica di calcolo (formule)

Siano:
- `fixed_sum` = somma dei costi in `fixed_monthly_costs_usd`
- `R` = `monthly_revenue_target_usd`
- `M` = `target_margin_multiplier`
- `C` = `usd_to_credits`
- `min_cred` = `minimum_operation_cost_credits`
- `base_cost_usd` = costo base USD dell’operazione (override per flow o default)

Moltiplicatori:
- `overhead_multiplier` = 1 + fixed_sum / R (se R <= 0 → 1)
- `usd_multiplier` = `overhead_multiplier` × `M`
- `final_credit_multiplier` = `overhead_multiplier` × `M` × `C`

Prezzi finali:
- `final_cost_credits` = max(`base_cost_usd` × `final_credit_multiplier`, `min_cred`)
- `final_cost_usd` = se `C` > 0 allora `final_cost_credits` / `C` altrimenti `base_cost_usd` × `usd_multiplier`

Note:
- Se esiste `flow_costs_usd[flow_key]` o `flow_costs_usd[flow_id]`, quello sovrascrive `base_cost_usd` per il flow.

---

## Sezioni della UI

### 1) Header
- Bearer Token: necessario per chiamare le API
- Base URL Core: default `http://127.0.0.1:5050`

### 2) Configurazione
- Revenue Target, USD→Credits, Margin Multiplier, Min Op Cost
- Fixed Monthly Costs: tabella con righe `name/cost_usd`
- Flow Costs Override: tabella con righe `flow_key_or_id/base_cost_usd`

Azioni:
- Carica Config: legge la config corrente dal Core
- Salva Config: invia un PUT con i valori presenti in UI

### 3) Simulazione
- Mostra i KPI calcolati:
  - Overhead x, Margin x, USD→Credits, Final Credit x
  - USD Multiplier e Markup %
- Mostra un esempio di costo finale (credits/USD) su un flow di esempio

### 4) Proiezioni mensili
- Input: MAU, operazioni per utente/mese, mix per flow (in %)
- Calcolo:
  - `ops_total` = MAU × ops_per_user
  - Per ogni flow nel mix: quota di `ops_total`, prezzo unitario (USD), revenue, raw cost
  - Totali e gross margin percentuale

### 5) Scenari & Import/Export
- Salva scenario: salva uno “snapshot” in `localStorage.pricing_scenarios`
- Carica scenario: applica lo scenario selezionato
- Export: scarica JSON con configurazione + proiezioni
- Import: carica un JSON locale e popola la UI

---

## Best Practice operative
- Tieni `monthly_revenue_target_usd` realistico rispetto alla fase del prodotto
- Mantieni aggiornata la lista dei costi fissi con valori netti e ricorrenti
- Usa override per i flow più costosi o ad alto volume per una granularità migliore
- Usa “Proiezioni” per stress-testare margini su diversi mix/volumi
- Versiona le configurazioni importanti (usa export JSON e git)

---

## Troubleshooting
- 401/403: verifica Bearer Token; se in sviluppo puoi rigenerarlo o usare gli strumenti già presenti nella sezione Examples
- 422: payload non conforme allo schema; controlla numeri/campi obbligatori
- 500: controlla variabili d’ambiente e log del Core
- UI non aggiorna: ricarica la pagina; assicurati che il Core sia in modalità reload

---

## Roadmap UX (miglioramenti suggeriti)
- Preset scenari: “Lean”, “Growth”, “Enterprise”
- Unit economics: ARPU, LTV stimato, CAC placeholder
- Grafici (trend proiezioni, breakdown per flow)
- Validazioni inline e tooltip con hint esplicativi
- Import/Export multipli per batch di scenari

---

## Riferimenti codice
- UI: `flow_starter/app/api/endpoints/admin_ui.py` → rotta `GET /core/v1/admin-ui/business-dashboard`
- API Config: `flow_starter/app/api/endpoints/pricing.py` → `GET/PUT /core/v1/admin/pricing/config`
- Motore pricing: `flow_starter/app/services/pricing_service.py`



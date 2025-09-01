# Setup Webhook LemonSqueezy con ngrok

## 1. Installa ngrok
```bash
# Scarica da https://ngrok.com/download
```

## 2. Esponi il Core pubblicamente
```bash
ngrok http 5050
```

## 3. Configura webhook su LemonSqueezy
- Vai su https://app.lemonsqueezy.com/settings/webhooks
- Aggiungi nuovo webhook:
  - **URL**: `https://tuosubdominio.ngrok.io/core/v1/billing/webhook`
  - **Eventi**: 
    - `order_created`
    - `subscription_created` 
    - `subscription_payment_success`
  - **Signing secret**: Usa quello nel tuo .env o generane uno nuovo

## 4. Testa il pagamento
Dopo aver configurato il webhook, ogni pagamento su LemonSqueezy invierà automaticamente il webhook al tuo Core locale e accrediterà i crediti.

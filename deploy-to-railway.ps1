# Script per deploy su Railway
# Assicurati di essere nella directory flow_starter

Write-Host "🚀 Deploy FlowStarter su Railway" -ForegroundColor Cyan
Write-Host ""

# Verifica Railway CLI
$railwayCheck = railway --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Railway CLI non trovata. Installa con: npm install -g @railway/cli" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Railway CLI trovata: $railwayCheck" -ForegroundColor Green
Write-Host ""

# Verifica link progetto
Write-Host "📡 Verifico link al progetto..." -ForegroundColor Yellow
railway status
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Progetto non linkato. Esegui: railway link" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔄 Inizio deploy..." -ForegroundColor Yellow
Write-Host ""

# Deploy con Railway
railway up --service flow_starter

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deploy completato con successo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Prossimi passi:" -ForegroundColor Cyan
    Write-Host "  1. Controlla i log: railway logs --service flow_starter" -ForegroundColor White
    Write-Host "  2. Testa la creazione utente dal form locale" -ForegroundColor White
    Write-Host "  3. Cerca i log con emoji: 🔄 ✅ ❌" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Deploy fallito!" -ForegroundColor Red
    Write-Host "Controlla i log: railway logs --service flow_starter" -ForegroundColor Yellow
}

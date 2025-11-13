# Script per controllare i log di Railway
# Cerca i messaggi di provisioning OpenRouter

Write-Host "📋 Recupero log da Railway..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Cerca i seguenti indicatori:" -ForegroundColor Yellow
Write-Host "  🔄 = Operazione in corso" -ForegroundColor White
Write-Host "  ✅ = Successo" -ForegroundColor Green
Write-Host "  ❌ = Errore" -ForegroundColor Red
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# Ottieni gli ultimi log del servizio flow_starter
railway logs --service flow_starter

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "💡 Tip: Usa CTRL+F per cercare 'OpenRouter' o 'provisioning'" -ForegroundColor Yellow

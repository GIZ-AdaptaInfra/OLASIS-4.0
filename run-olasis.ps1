<# 
run-olasis.ps1  —  OLASIS + ngrok
 - Define variáveis de ambiente fixas
 - Sobe o app Flask local
 - Abre túnel ngrok para acesso público
 Requisitos:
 - Python/venv com deps instaladas
 - ngrok instalado e authtoken configurado (ngrok config add-authtoken ...)
#>

param(
  [int]$Port = 5000  # altere para 8080 se preferir
)

Write-Host "===> Preparando ambiente ..." -ForegroundColor Cyan

# === VARIÁVEIS FIXAS ===
$env:GOOGLE_API_KEY  = "AIzaSyCV2cyD-SEpnvwHtnoE4yksJyPeukK9OxE"
$env:SECRET_KEY      = "rEqA47pinNtmwuHIqOo508EilgK0xDyKHSJRv4Iss6Q"
$env:OPENALEX_MAILTO = "olasis2025@gmail.com"

Write-Host "GOOGLE_API_KEY / SECRET_KEY / OPENALEX_MAILTO configurados." -ForegroundColor Green

# 0) Porta
$env:PORT = "$Port"

# 1) Detectar Python (usa venv se existir)
$pythonPath = ".\venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) { $pythonPath = "python" }

# 2) Abrir o app Flask em uma janela separada
Write-Host "===> Iniciando OLASIS local em http://127.0.0.1:$Port ..." -ForegroundColor Cyan
$flaskCmd = "`"$pythonPath`" app.py"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$flaskCmd | Out-Null
Start-Sleep -Seconds 3

# 3) Conferir se ngrok está instalado
$ngrok = (Get-Command ngrok -ErrorAction SilentlyContinue)
if (-not $ngrok) {
  Write-Host "ngrok não encontrado. Instale em https://ngrok.com/download e rode: ngrok config add-authtoken <TOKEN>" -ForegroundColor Yellow
  exit 1
}

# 4) Abrir túnel ngrok em uma nova janela
Write-Host "===> Abrindo túnel ngrok para a porta $Port ..." -ForegroundColor Cyan
$ngrokCmd = "ngrok http $Port"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$ngrokCmd | Out-Null

Write-Host "`nPronto! Aguarde a janela do ngrok exibir a URL 'https://....ngrok-free.app'." -ForegroundColor Green
Write-Host "Teste: https://...ngrok-free.app/health" -ForegroundColor Green

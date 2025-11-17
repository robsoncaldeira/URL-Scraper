# Script para executar o URL Scraper com urls.txt e keywords.txt
# Uso: .\run_scraper.ps1

param(
    [string]$Mode = "seed",           # seed, keywords, ou hybrid
    [string]$UrlsFile = "urls.txt",
    [string]$KeywordsFile = "keywords.txt",
    [int]$FollowDepth = 0,
    [float]$Delay = 1.0,
    [switch]$UseBing,                 # Adicionar para usar Bing discovery
    [string]$OutputDir = "results"
)

# Criar diretório de saída se não existir
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Gerar timestamp para nome único
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = Join-Path $OutputDir "scraping_results_${timestamp}.json"

Write-Host "URL Scraper - Modo: $Mode"
Write-Host "URLs file: $UrlsFile"
Write-Host "Keywords file: $KeywordsFile"
Write-Host "Output: $outputFile"
Write-Host "Follow depth: $FollowDepth"
Write-Host "Delay: $Delay segundos"
Write-Host ""

# Construir comando
$cmd = "python cli.py --mode $Mode --delay $Delay --output `"$outputFile`""

if ($Mode -eq "seed" -or $Mode -eq "hybrid") {
    if (-not (Test-Path $UrlsFile)) {
        Write-Error "Arquivo de URLs não encontrado: $UrlsFile"
        exit 1
    }
    $cmd += " --urls `"$UrlsFile`""
}

if ($Mode -eq "keywords" -or $Mode -eq "hybrid") {
    if (-not (Test-Path $KeywordsFile)) {
        Write-Error "Arquivo de keywords não encontrado: $KeywordsFile"
        exit 1
    }
    $cmd += " --keywords `"$KeywordsFile`""
}

if ($Mode -eq "hybrid") {
    $cmd += " --follow-depth $FollowDepth"
}

if ($UseBing) {
    $cmd += " --use-bing"
    if (-not $env:BING_API_KEY) {
        Write-Warning "BING_API_KEY não está definida! Use: setx BING_API_KEY 'sua_chave'"
    }
}

# Executar
Write-Host "Executando: $cmd`n"
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nScraping concluído com sucesso!"
    Write-Host "Resultados salvos em: $outputFile"
    
    # Opcional: abrir arquivo de resultados
    # Invoke-Item $outputFile
} else {
    Write-Error "Erro ao executar CLI"
    exit 1
}

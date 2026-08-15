#!/usr/bin/env pwsh
<#
.SYNOPSIS
    MJ AI Assistant — One-click startup script
    Starts Ollama (CPU mode), FastAPI backend, and Frontend
.NOTES
    Intel iGPU: Ollama runs in CPU-only mode (no CUDA needed)
#>

$BackendDir  = "$PSScriptRoot\backend"
$FrontendDir = "$PSScriptRoot\frontend"

Write-Host ""
Write-Host "  MJ AI Assistant — Starting Up" -ForegroundColor Cyan
Write-Host "  ==============================" -ForegroundColor Cyan
Write-Host ""

# ── Step 0: Start Ollama in CPU-only mode ────────────────────────────────────
$ollamaRunning = $false
try {
    $null = Invoke-RestMethod "http://localhost:11434/api/tags" -TimeoutSec 2
    $ollamaRunning = $true
    Write-Host "  [OK] Ollama already running" -ForegroundColor Green
} catch {}

if (-not $ollamaRunning) {
    Write-Host "  [1/3] Starting Ollama (CPU mode - Intel UHD)..." -ForegroundColor Yellow
    $env:OLLAMA_SKIP_GPU      = "1"
    $env:OLLAMA_NO_GPU        = "1"
    $env:CUDA_VISIBLE_DEVICES = ""
    Start-Process "ollama" -ArgumentList "serve" `
        -WindowStyle Minimized `
        -Environment @{
            OLLAMA_SKIP_GPU      = "1"
            OLLAMA_NO_GPU        = "1"
            CUDA_VISIBLE_DEVICES = ""
        }
    Write-Host "  [1/3] Waiting for Ollama to be ready..." -ForegroundColor Gray
    $retries = 0
    while ($retries -lt 10) {
        Start-Sleep -Seconds 2
        try {
            $null = Invoke-RestMethod "http://localhost:11434/api/tags" -TimeoutSec 2
            Write-Host "  [OK] Ollama is ready" -ForegroundColor Green
            break
        } catch {
            $retries++
        }
    }
    if ($retries -ge 10) {
        Write-Host "  [WARN] Ollama may not have started. Check manually." -ForegroundColor Red
    }
}

# ── Step 1: Check port 8000 ───────────────────────────────────────────────────
$portCheck = netstat -ano | Select-String ":8000 "
if ($portCheck) {
    Write-Host "  [OK] FastAPI already running on port 8000" -ForegroundColor Green
} else {
    Write-Host "  [2/3] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$BackendDir'; `$env:OLLAMA_SKIP_GPU='1'; Write-Host 'MJ Backend starting...' -ForegroundColor Cyan; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    ) -WindowStyle Normal
    Start-Sleep -Seconds 3
}

# ── Step 2: Start Frontend ────────────────────────────────────────────────────
if (Test-Path "$FrontendDir\package.json") {
    $frontPort = netstat -ano | Select-String ":5174 "
    if ($frontPort) {
        Write-Host "  [OK] Frontend already running on port 5174" -ForegroundColor Green
    } else {
        Write-Host "  [3/3] Starting Frontend on http://localhost:5174..." -ForegroundColor Green
        Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-Command",
            "Set-Location '$FrontendDir'; Write-Host 'MJ Frontend starting...' -ForegroundColor Cyan; npm run dev"
        ) -WindowStyle Normal
    }
} else {
    Write-Host "  [3/3] Frontend not found, skipping." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "  Services:" -ForegroundColor White
Write-Host "    Ollama:      http://localhost:11434" -ForegroundColor Green
Write-Host "    Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "    API Docs:    http://localhost:8000/docs" -ForegroundColor Green
Write-Host "    Frontend:    http://localhost:5174" -ForegroundColor Green
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press any key to exit this launcher (services keep running)." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

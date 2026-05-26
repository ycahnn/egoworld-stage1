param(
    [ValidateSet("cpu", "cu126", "none")]
    [string]$MainTorch = "cpu",

    [ValidateSet("cpu", "cu118", "none")]
    [string]$HamerTorch = "cpu"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "== EgoWorld Stage 1 full setup =="

& .\scripts\setup_main.ps1 -Torch $MainTorch
& .\scripts\setup_hamer.ps1 -Torch $HamerTorch

Write-Host "All setup complete."
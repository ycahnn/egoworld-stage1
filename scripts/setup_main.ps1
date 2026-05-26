param(
    [ValidateSet("cpu", "cu126", "none")]
    [string]$Torch = "cpu"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = ".\.venv\Scripts\python.exe"

Write-Host "== Setup main .venv =="

if (!(Test-Path $Python)) {
    Write-Host "Creating .venv with Python 3.11..."
    py -3.11 -m venv .venv
}

& $Python --version
& $Python -m pip install --upgrade pip setuptools wheel --index-url https://pypi.org/simple

Write-Host "Installing common requirements..."
& $Python -m pip install -r .\requirements.txt --index-url https://pypi.org/simple --no-cache-dir

if ($Torch -eq "cpu") {
    Write-Host "Installing main torch CPU..."
    & $Python -m pip install -r .\requirements-torch-cpu.txt --no-cache-dir
}
elseif ($Torch -eq "cu126") {
    Write-Host "Installing main torch CUDA 12.6..."
    & $Python -m pip install -r .\requirements-torch-cu126.txt --no-cache-dir
}
else {
    Write-Host "Skipping main torch installation."
}

Write-Host "Checking main environment..."
& $Python -c "import sys; print('python', sys.version)"
& $Python -c "import mediapipe as mp; print('mediapipe', mp.__version__)"
& $Python -c "import cv2; print('opencv', cv2.__version__)"
& $Python -c "import numpy as np; print('numpy', np.__version__)"
& $Python -c "import torch; print('torch', torch.__version__); print('cuda', torch.cuda.is_available())"
& $Python -m pip check

Write-Host "Main environment setup complete."
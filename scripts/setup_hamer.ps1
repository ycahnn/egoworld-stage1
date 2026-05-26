param(
    [ValidateSet("cpu", "cu118", "none")]
    [string]$Torch = "cpu"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$HamerDir = Join-Path $Root "external\hamer"
$HamerPython = Join-Path $HamerDir ".hamer\Scripts\python.exe"

Write-Host "== Setup HaMeR .hamer =="

if (!(Test-Path $HamerDir)) {
    Write-Host "Cloning HaMeR into external\hamer..."
    New-Item -ItemType Directory -Force -Path ".\external" | Out-Null
    git clone --recursive https://github.com/geopavlakos/hamer.git .\external\hamer
}

if (!(Test-Path (Join-Path $HamerDir "hamer"))) {
    throw "external\hamer exists, but HaMeR source folder external\hamer\hamer was not found."
}

if (!(Test-Path $HamerPython)) {
    Write-Host "Creating .hamer with Python 3.10..."
    py -3.10 -m venv .\external\hamer\.hamer
}

& $HamerPython --version
& $HamerPython -m pip install --upgrade pip setuptools wheel --index-url https://pypi.org/simple

if ($Torch -eq "cpu") {
    Write-Host "Installing HaMeR torch CPU..."
    & $HamerPython -m pip install -r .\requirements-hamer-torch-cpu.txt --no-cache-dir
}
elseif ($Torch -eq "cu118") {
    Write-Host "Installing HaMeR torch CUDA 11.8..."
    & $HamerPython -m pip install -r .\requirements-hamer-torch-cu118.txt --no-cache-dir
}
else {
    Write-Host "Skipping HaMeR torch installation."
}

Write-Host "Installing chumpy separately..."
& $HamerPython -m pip install chumpy==0.70 --no-build-isolation --index-url https://pypi.org/simple

Write-Host "Installing HaMeR common requirements..."
& $HamerPython -m pip install -r .\requirements-hamer.txt --index-url https://pypi.org/simple --no-cache-dir

Write-Host "Checking HaMeR environment..."
Set-Location $HamerDir

& $HamerPython -c "import sys; print('python', sys.version)"
& $HamerPython -c "import torch; print('torch', torch.__version__); print('cuda', torch.cuda.is_available())"
& $HamerPython -c "import hamer; print('hamer import ok')"
& $HamerPython -c "import smplx, timm, cv2, numpy, scipy; print('hamer deps ok')"

Set-Location $Root
& $HamerPython -m pip check

Write-Host "HaMeR environment setup complete."  
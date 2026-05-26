# EgoWorld Stage 1

**Project goal:** reproduce an EgoWorld Stage 1-style observation extraction pipeline from an exocentric RGB image to hand crops and HaMeR/MANO mesh metadata.

This repo implements Stage 1 building blocks:

- monocular depth estimation (dummy or MoGe)
- RGB-D backprojection to a point cloud
- MediaPipe hand bounding boxes
- hand crop extraction for HaMeR
- HaMeR/MANO mesh metadata ingestion
- projection verification for HaMeR mesh outputs

---

## Workspace documentation

- `docs/PROJECT_STATUS.md` — current achievement summary and final outputs
- `docs/PIPELINE_OVERVIEW.md` — step-by-step pipeline explanation
- `docs/FILE_MANIFEST.md` — important files, shapes, and status
- `docs/RUNBOOK.md` — exact commands for rerunning the pipeline
- `docs/KNOWN_ISSUES.md` — current issues, failure modes, and constraints
- `docs/CLEANUP_LOG.md` — files moved to `_trash_review` and why

## 한국어 문서

- `docs/PROJECT_MAP_KR.md`
- `docs/FILE_DEPENDENCY_GRAPH_KR.md`
- `docs/RUN_COMMANDS_KR.md`
- `docs/OBSOLETE_OR_FAILED_KR.md`

---

## Environment model

This project intentionally uses two separate Python environments.

```text
egoworld-stage1/
├─ .venv/                         # Main Stage 1 environment, Python 3.11
├─ external/
│  └─ hamer/                      # Cloned HaMeR repository
│     ├─ hamer/                   # HaMeR Python package
│     ├─ demo.py
│     ├─ setup.py
│     └─ .hamer/                  # HaMeR-only environment, Python 3.10
├─ requirements.txt
├─ requirements-torch-cpu.txt
├─ requirements-torch-cu126.txt
├─ requirements-hamer.txt
├─ requirements-hamer-torch-cpu.txt
├─ requirements-hamer-torch-cu118.txt
└─ scripts/
   ├─ setup_main.ps1
   ├─ setup_hamer.ps1
   └─ setup_all.ps1
```

### Main environment: `.venv`

Use `.venv` for all Stage 1 scripts except HaMeR core inference.

Typical tasks:

- MoGe or dummy depth estimation
- Open3D point cloud generation/visualization
- MediaPipe hand bbox detection
- hand crop extraction
- projection verification

Python version:

```text
Python 3.11
```

### HaMeR environment: `external/hamer/.hamer`

Use `.hamer` only for HaMeR core inference and MANO mesh/joint generation.

Typical tasks:

- loading HaMeR model code
- running HaMeR forward inference
- producing MANO vertices/joints/mesh metadata

Python version:

```text
Python 3.10
```

---

## Important Stage 1 constraints

Follow these rules for this workflow:

- Do **not** install `detectron2` on Windows.
- Do **not** use HaMeR renderer.
- Do **not** use `pyrender`, `PyOpenGL`, or OpenGL rendering for Stage 1 inference.
- Do **not** run `pip install -e .[all]` inside HaMeR.
- Use HaMeR as a pure-inference backend inside `external/hamer`.
- Use MediaPipe or another lightweight detector to generate hand bboxes before HaMeR inference.
- Keep `.venv` and `.hamer` separate.

---

## Dependency structure

Do not put GPU-specific PyTorch wheels inside common requirements files.

### Main environment dependencies

```text
requirements.txt
```

Portable/common dependencies only. This file should not contain:

```text
torch
torchvision
torchaudio
+cu126
```

Install PyTorch separately:

```text
requirements-torch-cpu.txt       # main .venv CPU torch
requirements-torch-cu126.txt     # main .venv CUDA 12.6 torch
```

### HaMeR environment dependencies

```text
requirements-hamer.txt
```

HaMeR common dependencies only. This file should not contain:

```text
torch
torchvision
chumpy
detectron2
pyrender
PyOpenGL
pyglet
-e git+https://github.com/geopavlakos/hamer.git
```

Install HaMeR PyTorch separately:

```text
requirements-hamer-torch-cpu.txt     # HaMeR .hamer CPU torch
requirements-hamer-torch-cu118.txt   # HaMeR .hamer CUDA 11.8 torch
```

`chumpy==0.70` is installed separately by the setup script because it needs special build handling.

---

## Files not included in Git

These should be ignored or kept out of the repository:

```text
.venv/
external/hamer/.hamer/
outputs/
inputs/exo.jpg
external/hamer/_DATA/
hamer.ckpt
MANO_RIGHT.pkl
MANO_LEFT.pkl
```

Recommended `.gitignore` entries:

```gitignore
.venv/
external/hamer/.hamer/
outputs/
inputs/exo.jpg
external/hamer/_DATA/
*.ckpt
MANO_RIGHT.pkl
MANO_LEFT.pkl
```

---

# Setup: Windows from scratch

## 0. Prerequisites

Install:

- Git
- Python 3.11
- Python 3.10
- Git LFS, if large model files are managed through LFS
- NVIDIA driver, only if using GPU locally

Check installed Python versions:

```powershell
py -0p
```

---

## 1. Clone this repo

```powershell
git clone <repo-url> egoworld-stage1
cd egoworld-stage1
```

---

## 2. Clone HaMeR into `external/hamer`

Do not manually create `external/hamer` before clone. Create only the parent folder:

```powershell
New-Item -ItemType Directory -Force .\external | Out-Null
git clone --recursive https://github.com/geopavlakos/hamer.git .\external\hamer
```

Verify clone:

```powershell
Test-Path .\external\hamer
Test-Path .\external\hamer\hamer
Test-Path .\external\hamer\demo.py
Test-Path .\external\hamer\.git
```

Expected result:

```text
True
True
True
True
```

Why `external\hamer\hamer` appears twice:

```text
external\hamer        # cloned HaMeR repository folder
external\hamer\hamer  # actual Python package imported as `hamer`
```

---

## 3. Allow PowerShell setup scripts for the current terminal

Windows may block `.ps1` scripts by default. Allow them only for the current PowerShell process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

If files are still blocked:

```powershell
Unblock-File .\scripts\setup_main.ps1
Unblock-File .\scripts\setup_hamer.ps1
Unblock-File .\scripts\setup_all.ps1
```

---

## 4. Install environments

### Laptop / CPU development setup

Use this when developing locally on a laptop or when CUDA is not needed locally:

```powershell
.\scripts\setup_all.ps1 -MainTorch cpu -HamerTorch cpu
```

This creates and installs:

```text
.venv                  # Python 3.11 main env
external/hamer/.hamer  # Python 3.10 HaMeR env
```

CPU setup is enough for:

- checking imports
- verifying file paths
- running MediaPipe bbox extraction
- testing non-heavy pipeline steps
- preparing code before moving to server

`torch.cuda.is_available()` may print `False`. That is normal on CPU setup.

### Local CUDA setup

Use this only if the local machine has an NVIDIA GPU and `nvidia-smi` works:

```powershell
nvidia-smi
```

Then run:

```powershell
.\scripts\setup_all.ps1 -MainTorch cu126 -HamerTorch cu118
```

This installs:

```text
main .venv torch    → CUDA 12.6 wheel
HaMeR .hamer torch  → CUDA 11.8 wheel
```

---

## 5. Verify installation

Run from project root:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\external\hamer\.hamer\Scripts\python.exe -m pip check
```

Expected:

```text
No broken requirements found.
```

Check main environment:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print('main python', sys.version)"
.\.venv\Scripts\python.exe -c "import cv2; print('opencv', cv2.__version__)"
.\.venv\Scripts\python.exe -c "import mediapipe as mp; print('mediapipe', mp.__version__)"
.\.venv\Scripts\python.exe -c "import numpy as np; print('numpy', np.__version__)"
.\.venv\Scripts\python.exe -c "import torch; print('main torch', torch.__version__, torch.cuda.is_available())"
```

Check HaMeR environment:

```powershell
.\external\hamer\.hamer\Scripts\python.exe -c "import sys; print('hamer python', sys.version)"
.\external\hamer\.hamer\Scripts\python.exe -c "import torch; print('hamer torch', torch.__version__, torch.cuda.is_available())"
.\external\hamer\.hamer\Scripts\python.exe -c "import smplx, timm, cv2, numpy, scipy; print('hamer deps ok')"

cd .\external\hamer
.\.hamer\Scripts\python.exe -c "import hamer; print('hamer import ok')"
cd ..\..
```

---

## 6. Place model assets

Place required model files after HaMeR clone.

Typical locations:

```text
external/hamer/hamer.ckpt
external/hamer/data/MANO_RIGHT.pkl
external/hamer/data/MANO_LEFT.pkl
```

Also place any required HaMeR assets under:

```text
external/hamer/_DATA/
```

These files are not included in Git.

---

## 7. Add input image

Create `inputs/` and add an exocentric image:

```powershell
New-Item -ItemType Directory -Force .\inputs | Out-Null
```

Expected input example:

```text
inputs/exo.jpg
```

---

# Running Stage 1

Run all main scripts with `.venv` unless explicitly stated otherwise.

## Depth + point cloud

```powershell
.\.venv\Scripts\python.exe infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs
```

Expected outputs:

```text
outputs/depth_raw.npy
outputs/depth_vis.png
outputs/depth_gray.png
outputs/depth_mask.png
outputs/exo_point_cloud.ply
```

## Hand bounding boxes

```powershell
.\.venv\Scripts\python.exe infer_hand_bbox.py --image inputs/exo.jpg --out outputs
```

Expected outputs:

```text
outputs/hand_bboxes.json
outputs/hand_bbox_debug.png
```

## Crop hands from bboxes

```powershell
.\.venv\Scripts\python.exe crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
```

Expected outputs:

```text
outputs/hand_crops/
```

## HaMeR inference

HaMeR inference must use:

```text
external/hamer/.hamer
```

Example from project root:

```powershell
.\external\hamer\.hamer\Scripts\python.exe .\external\hamer\infer_hamer_from_bboxes.py --bboxes .\outputs\hand_bboxes.json --out .\outputs\hamer
```

If the wrapper is located in the project root instead of `external/hamer`, run the corresponding script with `.hamer` Python and keep paths explicit.

Expected outputs:

```text
outputs/hamer/hamer_metadata.json
outputs/hamer/vertices_*.npy
outputs/hamer/faces_*.npy
```

## Projection verification

Use the main `.venv`:

```powershell
.\.venv\Scripts\python.exe scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
```

Expected outputs:

```text
outputs/hamer_projection/
outputs/hamer_projection/final_projection_report.md
```

---

# Server setup notes

The laptop setup is mainly for development and import/path validation.

For server execution:

1. Clone this repository on the server.
2. Clone HaMeR into `external/hamer`.
3. Create `.venv` with Python 3.11.
4. Create `external/hamer/.hamer` with Python 3.10.
5. Install common requirements.
6. Install PyTorch according to the server GPU/driver.

Check the server GPU first:

```bash
nvidia-smi
```

Linux path differences:

```text
Windows main Python:
.\.venv\Scripts\python.exe

Linux main Python:
./.venv/bin/python

Windows HaMeR Python:
.\external\hamer\.hamer\Scripts\python.exe

Linux HaMeR Python:
./external/hamer/.hamer/bin/python
```

The same dependency split applies on the server:

```text
requirements.txt
requirements-torch-*.txt
requirements-hamer.txt
requirements-hamer-torch-*.txt
```

Choose the PyTorch wheel index according to the server environment.

---

# Reset and reinstall

To reset only Python environments:

```powershell
Remove-Item -Recurse -Force .\.venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\external\hamer\.hamer -ErrorAction SilentlyContinue
```

Then reinstall:

```powershell
.\scripts\setup_all.ps1 -MainTorch cpu -HamerTorch cpu
```

To also fresh-clone HaMeR when `external/hamer` was empty or broken:

```powershell
Remove-Item -Recurse -Force .\external\hamer -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force .\external | Out-Null
git clone --recursive https://github.com/geopavlakos/hamer.git .\external\hamer
```

Then run setup again.

---

# Troubleshooting

## PowerShell script blocked

Error:

```text
cannot be loaded because running scripts is disabled on this system
```

Fix:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Wi-Fi disconnects during install

Reconnect and rerun the same command:

```powershell
.\scripts\setup_all.ps1 -MainTorch cpu -HamerTorch cpu
```

Already-installed packages are usually skipped as `Requirement already satisfied`.

## `external\hamer\hamer` looks strange

This is normal:

```text
external\hamer        # repository
external\hamer\hamer  # Python package
```

## `torch.cuda.is_available()` is False on laptop

Normal for CPU setup. On server/GPU setup, verify:

```bash
nvidia-smi
```

and install the correct CUDA PyTorch wheel.

## `chumpy` build fails

Do not manually install it with random options. The setup script installs:

```text
chumpy==0.70
```

with the required build handling.

## Do not use renderer path

Even if renderer-related packages exist in an old environment, Stage 1 inference should not call:

```text
HaMeR renderer
pyrender
PyOpenGL
OpenGL
detectron2
```

---

# Final projection rule

- Right hand: use normal camera projection from HaMeR camera translation.
- Left hand: after projecting mesh vertices to image coordinates, apply a 2D bbox mirror correction to the `u` coordinate:

```text
u' = x_left + x_right - u
```

This mirrors the projected x-coordinates inside the MediaPipe bbox for left hands only.

---

# Current project status

- Depth pipeline: working with dummy depth and MoGe wrapper
- MediaPipe bbox detection: working
- Hand crop extraction: working
- HaMeR mesh ingestion: requires external HaMeR repo and model assets
- Projection verification: working with left-hand 2D bbox mirror correction
- Next steps: complete `scripts/render_hand_depth.py` if needed, but avoid OpenGL/renderer dependency for Stage 1 inference

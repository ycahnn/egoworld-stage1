# EgoWorld Stage 1 — Conda Server Setup

**Project goal:** reproduce an EgoWorld Stage 1-style observation extraction pipeline from an exocentric RGB image to hand crops and HaMeR/MANO mesh metadata.

This README is written for the **server/conda workflow**.  
It replaces the earlier Windows `venv` / `.venv` / `.hamer` workflow.

This repo implements Stage 1 building blocks:

- monocular depth estimation, using dummy depth or MoGe
- RGB-D backprojection to a point cloud
- MediaPipe hand bounding boxes
- hand crop extraction for HaMeR
- HaMeR/MANO mesh metadata ingestion
- projection verification for HaMeR mesh outputs

---

## Big picture

This project uses **two separate conda environments**:

```text
egoworld-main   # Python 3.11, main Stage 1 pipeline
egoworld-hamer  # Python 3.10, HaMeR core inference only
```

Do **not** create `.venv` or `external/hamer/.hamer` on the server when using this conda workflow.

The project code lives in your own workspace folder, for example:

```text
/home/<user>/projects/egoworld-stage1/
```

The conda environments live inside your conda installation, usually:

```text
/home/<user>/miniconda3/envs/egoworld-main/
/home/<user>/miniconda3/envs/egoworld-hamer/
```

If the server has a shared conda installation, environment locations may instead be under the shared conda path. Check with:

```bash
conda info --envs
```

---

## Recommended server folder structure

```text
/home/<user>/
├── miniconda3/
│   └── envs/
│       ├── egoworld-main/
│       │   ├── bin/python
│       │   └── lib/python3.11/site-packages/
│       │
│       └── egoworld-hamer/
│           ├── bin/python
│           └── lib/python3.10/site-packages/
│
└── projects/
    └── egoworld-stage1/
        ├── requirements.txt
        ├── requirements-torch-cpu.txt
        ├── requirements-torch-cu126.txt
        ├── requirements-hamer.txt
        ├── requirements-hamer-torch-cpu.txt
        ├── requirements-hamer-torch-cu118.txt
        ├── infer_depth_pointcloud.py
        ├── infer_hand_bbox.py
        ├── crop_hands_from_bboxes.py
        ├── scripts/
        ├── inputs/
        ├── outputs/
        └── external/
            └── hamer/
                ├── hamer/
                ├── demo.py
                ├── setup.py
                └── ...
```

Important distinction:

```text
external/hamer        # cloned HaMeR repository folder
external/hamer/hamer  # actual Python package imported as `hamer`
```

So `external/hamer/hamer` is normal. The first `hamer` is the repository directory; the second `hamer` is the Python package directory.

---

## Important Stage 1 constraints

Follow these rules for this workflow:

- Do **not** install `detectron2`.
- Do **not** use HaMeR renderer.
- Do **not** use `pyrender`, `PyOpenGL`, or OpenGL rendering for Stage 1 inference.
- Do **not** run `pip install -e .[all]` inside HaMeR.
- Use HaMeR only as a pure-inference backend inside `external/hamer`.
- Use MediaPipe or another lightweight detector to generate hand bboxes before HaMeR inference.
- Keep `egoworld-main` and `egoworld-hamer` separate.

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
requirements-torch-cpu.txt       # main env CPU torch
requirements-torch-cu126.txt     # main env CUDA 12.6 torch
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
requirements-hamer-torch-cpu.txt     # HaMeR env CPU torch
requirements-hamer-torch-cu118.txt   # HaMeR env CUDA 11.8 torch
```

`chumpy==0.70` is installed separately because it needs special build handling.

---

## Files not included in Git

These should be ignored or kept out of the repository:

```text
outputs/
inputs/exo.jpg
external/hamer/_DATA/
external/hamer/hamer.ckpt
external/hamer/data/MANO_RIGHT.pkl
external/hamer/data/MANO_LEFT.pkl
*.ckpt
MANO_RIGHT.pkl
MANO_LEFT.pkl
```

Recommended `.gitignore` entries:

```gitignore
outputs/
inputs/exo.jpg
external/hamer/_DATA/
external/hamer/*.ckpt
external/hamer/data/MANO_RIGHT.pkl
external/hamer/data/MANO_LEFT.pkl
*.ckpt
MANO_RIGHT.pkl
MANO_LEFT.pkl
```

When using conda on the server, you normally do **not** need these Windows/venv ignore entries:

```text
.venv/
external/hamer/.hamer/
```

But keeping them in `.gitignore` is harmless if the repo is also used on Windows.

---

# Setup: Server/Linux with Conda

## 0. Check conda

From your server home directory:

```bash
pwd
conda --version
conda info --envs
```

If `conda activate` does not work, initialize conda in the current shell.

For Miniconda:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
```

For Anaconda:

```bash
source ~/anaconda3/etc/profile.d/conda.sh
```

If the server uses a shared conda installation, ask the server admin where `conda.sh` is located, or find it with:

```bash
find ~ /opt -path "*/etc/profile.d/conda.sh" 2>/dev/null
```

---

## 1. Create your own project folder

Use your own workspace so multiple users do not overwrite each other.

```bash
mkdir -p ~/projects
cd ~/projects
```

Clone this repo:

```bash
git clone <repo-url> egoworld-stage1
cd egoworld-stage1
```

If you are copying the project manually instead of using GitHub, place it at:

```text
~/projects/egoworld-stage1/
```

---

## 2. Clone HaMeR into `external/hamer`

Create only the parent folder. Let `git clone` create `external/hamer`.

```bash
mkdir -p external
git clone --recursive https://github.com/geopavlakos/hamer.git external/hamer
```

Verify clone:

```bash
test -d external/hamer && echo "external/hamer ok"
test -d external/hamer/hamer && echo "hamer package ok"
test -f external/hamer/demo.py && echo "demo.py ok"
test -d external/hamer/.git && echo "git repo ok"
```

Expected output:

```text
external/hamer ok
hamer package ok
demo.py ok
git repo ok
```

If `external/hamer` already exists but is empty or broken:

```bash
rm -rf external/hamer
mkdir -p external
git clone --recursive https://github.com/geopavlakos/hamer.git external/hamer
```

Do **not** delete `external/hamer` if you have already placed checkpoints or MANO files there unless those files are backed up.

---

## 3. Check GPU

Before installing GPU PyTorch, check the server GPU:

```bash
nvidia-smi
```

If this works and shows NVIDIA GPU information, use GPU torch requirements.

If this fails, install CPU torch requirements for basic import/path testing.

---

## 4. Create conda environments

Create the main environment:

```bash
conda create -n egoworld-main python=3.11 pip -y
```

Create the HaMeR environment:

```bash
conda create -n egoworld-hamer python=3.10 pip -y
```

Verify:

```bash
conda info --envs
```

Expected example:

```text
egoworld-main       /home/<user>/miniconda3/envs/egoworld-main
egoworld-hamer      /home/<user>/miniconda3/envs/egoworld-hamer
```

---

# Install dependencies

## 5. Install main environment

Activate the main environment:

```bash
conda activate egoworld-main
```

Verify that `python` points to the main conda env:

```bash
which python
python --version
```

Expected:

```text
.../miniconda3/envs/egoworld-main/bin/python
Python 3.11.x
```

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install common main dependencies:

```bash
python -m pip install -r requirements.txt --index-url https://pypi.org/simple
```

Install main PyTorch.

For GPU server using CUDA 12.6 wheel:

```bash
python -m pip install -r requirements-torch-cu126.txt
```

For CPU-only test:

```bash
python -m pip install -r requirements-torch-cpu.txt
```

Verify main environment:

```bash
python -m pip check

python -c "import sys; print('main python', sys.version)"
python -c "import cv2; print('opencv', cv2.__version__)"
python -c "import mediapipe as mp; print('mediapipe', mp.__version__)"
python -c "import numpy as np; print('numpy', np.__version__)"
python -c "import torch; print('main torch', torch.__version__); print('cuda', torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
```

---

## 6. Install HaMeR environment

Activate the HaMeR environment:

```bash
conda activate egoworld-hamer
```

Verify that `python` points to the HaMeR conda env:

```bash
which python
python --version
```

Expected:

```text
.../miniconda3/envs/egoworld-hamer/bin/python
Python 3.10.x
```

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install HaMeR PyTorch.

For GPU server using CUDA 11.8 wheel:

```bash
python -m pip install -r requirements-hamer-torch-cu118.txt
```

For CPU-only test:

```bash
python -m pip install -r requirements-hamer-torch-cpu.txt
```

Install `chumpy` separately:

```bash
python -m pip install chumpy==0.70 --no-build-isolation --index-url https://pypi.org/simple
```

Install HaMeR common dependencies:

```bash
python -m pip install -r requirements-hamer.txt --index-url https://pypi.org/simple
```

Verify HaMeR environment:

```bash
python -m pip check

python -c "import torch; print('hamer torch', torch.__version__); print('cuda', torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')"
python -c "import smplx, timm, cv2, numpy, scipy; print('hamer deps ok')"
```

Check `hamer` import from inside the HaMeR repo:

```bash
cd external/hamer
python -c "import hamer; print('hamer import ok')"
cd ../..
```

---

## 7. Place model assets

Place required HaMeR model files after cloning HaMeR.

Typical locations:

```text
external/hamer/hamer.ckpt
external/hamer/data/MANO_RIGHT.pkl
external/hamer/data/MANO_LEFT.pkl
external/hamer/_DATA/
```

Create the data folder if needed:

```bash
mkdir -p external/hamer/data
```

Verify files:

```bash
ls -lh external/hamer/hamer.ckpt
ls -lh external/hamer/data/MANO_RIGHT.pkl
ls -lh external/hamer/data/MANO_LEFT.pkl
```

These files are not included in Git.

---

## 8. Add input image

Create `inputs/` and add an exocentric image:

```bash
mkdir -p inputs
```

Expected input example:

```text
inputs/exo.jpg
```

---

# Running Stage 1 with Conda

Always activate the correct conda environment before running a script.

## 1. Depth + point cloud

Use `egoworld-main`:

```bash
conda activate egoworld-main

python infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs
```

Expected outputs:

```text
outputs/depth_raw.npy
outputs/depth_vis.png
outputs/depth_gray.png
outputs/depth_mask.png
outputs/exo_point_cloud.ply
```

---

## 2. Hand bounding boxes

Use `egoworld-main`:

```bash
conda activate egoworld-main

python infer_hand_bbox.py --image inputs/exo.jpg --out outputs
```

Expected outputs:

```text
outputs/hand_bboxes.json
outputs/hand_bbox_debug.png
```

---

## 3. Crop hands from bboxes

Use `egoworld-main`:

```bash
conda activate egoworld-main

python crop_hands_from_bboxes.py \
  --image inputs/exo.jpg \
  --bbox_json outputs/hand_bboxes.json \
  --out outputs/hand_crops
```

Expected outputs:

```text
outputs/hand_crops/
```

---

## 4. HaMeR inference

Use `egoworld-hamer`:

```bash
conda activate egoworld-hamer
```

If the HaMeR wrapper is in the project root:

```bash
python infer_hamer_from_bboxes.py \
  --bboxes outputs/hand_bboxes.json \
  --out outputs/hamer
```

If the wrapper is inside `external/hamer`:

```bash
python external/hamer/infer_hamer_from_bboxes.py \
  --bboxes outputs/hand_bboxes.json \
  --out outputs/hamer
```

Expected outputs:

```text
outputs/hamer/hamer_metadata.json
outputs/hamer/vertices_*.npy
outputs/hamer/faces_*.npy
```

---

## 5. Projection verification

Use `egoworld-main`:

```bash
conda activate egoworld-main

python scripts/verify_hamer_projection.py \
  --image inputs/exo.jpg \
  --hamer_dir outputs/hamer \
  --bbox_json outputs/hand_bboxes.json \
  --out outputs/hamer_projection
```

Expected outputs:

```text
outputs/hamer_projection/
outputs/hamer_projection/final_projection_report.md
```

---

# One-shot command summary

From project root:

```bash
# Clone HaMeR
mkdir -p external
git clone --recursive https://github.com/geopavlakos/hamer.git external/hamer

# Create environments
conda create -n egoworld-main python=3.11 pip -y
conda create -n egoworld-hamer python=3.10 pip -y

# Main env
conda activate egoworld-main
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt --index-url https://pypi.org/simple
python -m pip install -r requirements-torch-cu126.txt
python -m pip check

# HaMeR env
conda activate egoworld-hamer
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-hamer-torch-cu118.txt
python -m pip install chumpy==0.70 --no-build-isolation --index-url https://pypi.org/simple
python -m pip install -r requirements-hamer.txt --index-url https://pypi.org/simple
python -m pip check
```

For CPU-only test, replace:

```bash
python -m pip install -r requirements-torch-cu126.txt
python -m pip install -r requirements-hamer-torch-cu118.txt
```

with:

```bash
python -m pip install -r requirements-torch-cpu.txt
python -m pip install -r requirements-hamer-torch-cpu.txt
```

---

# Reset and reinstall Conda environments

To remove only the conda environments:

```bash
conda deactivate
conda env remove -n egoworld-main -y
conda env remove -n egoworld-hamer -y
```

Then recreate:

```bash
conda create -n egoworld-main python=3.11 pip -y
conda create -n egoworld-hamer python=3.10 pip -y
```

To fresh-clone HaMeR when `external/hamer` is empty or broken:

```bash
rm -rf external/hamer
mkdir -p external
git clone --recursive https://github.com/geopavlakos/hamer.git external/hamer
```

Do not run `rm -rf external/hamer` if model files are already inside it unless they are backed up.

---

# Multi-user server notes

If multiple people use the same server:

1. Put your project under your own home directory.

```text
/home/<your_user>/projects/egoworld-stage1/
```

2. Use conda environments under your own conda installation if possible.

```text
/home/<your_user>/miniconda3/envs/egoworld-main/
/home/<your_user>/miniconda3/envs/egoworld-hamer/
```

3. Do not install packages into `base`.

Always use:

```bash
conda activate egoworld-main
```

or:

```bash
conda activate egoworld-hamer
```

4. If the server uses shared conda, avoid modifying shared environments unless you have permission.

You can check the exact environment path with:

```bash
conda info --envs
which python
python -c "import sys; print(sys.executable)"
```

5. Environment names may collide if multiple users share the same conda installation. In that case, use user-specific names:

```bash
conda create -n youngchan-egoworld-main python=3.11 pip -y
conda create -n youngchan-egoworld-hamer python=3.10 pip -y
```

Then use:

```bash
conda activate youngchan-egoworld-main
conda activate youngchan-egoworld-hamer
```

---

# Troubleshooting

## `conda activate` does not work

Run:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
```

or:

```bash
source ~/anaconda3/etc/profile.d/conda.sh
```

Then try:

```bash
conda activate egoworld-main
```

## Wrong Python is being used

Check:

```bash
which python
python --version
python -c "import sys; print(sys.executable)"
```

For main env, expected path contains:

```text
envs/egoworld-main/bin/python
```

For HaMeR env, expected path contains:

```text
envs/egoworld-hamer/bin/python
```

## Wi-Fi or SSH disconnects during install

Reconnect, activate the same environment, and rerun the same install command.

Example:

```bash
conda activate egoworld-main
python -m pip install -r requirements.txt --index-url https://pypi.org/simple
python -m pip install -r requirements-torch-cu126.txt
```

Already-installed packages are usually skipped as `Requirement already satisfied`.

For long installs on a remote server, consider using `tmux` or `screen`.

## `torch.cuda.is_available()` is False

Check:

```bash
nvidia-smi
```

Then verify that the correct PyTorch wheel was installed:

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

If CUDA is still unavailable, the installed torch wheel may not match the server driver/GPU setup.

## `chumpy` build fails

Install it separately in the HaMeR environment:

```bash
conda activate egoworld-hamer
python -m pip install --upgrade pip setuptools wheel
python -m pip install chumpy==0.70 --no-build-isolation --index-url https://pypi.org/simple
```

## Do not use renderer path

Stage 1 inference should not call:

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
- Next steps: complete non-renderer depth/mesh export utilities if needed

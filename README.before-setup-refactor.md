# EgoWorld Stage 1

**Project goal:** reproduce an EgoWorld Stage 1-style observation extraction pipeline from an exocentric RGB image to hand crops and HaMeR mesh metadata.

## Workspace documentation

- `docs/PROJECT_STATUS.md` — current achievement summary and final outputs
- `docs/PIPELINE_OVERVIEW.md` — step-by-step pipeline explanation
- `docs/FILE_MANIFEST.md` — important files, shapes, and status
- `docs/RUNBOOK.md` — exact PowerShell commands for rerunning the pipeline
- `docs/KNOWN_ISSUES.md` — current issues, failure modes, and constraints
- `docs/CLEANUP_LOG.md` — files moved to `_trash_review` and why

## 한국어 문서

- `docs/PROJECT_MAP_KR.md`
- `docs/FILE_DEPENDENCY_GRAPH_KR.md`
- `docs/RUN_COMMANDS_KR.md`
- `docs/OBSOLETE_OR_FAILED_KR.md`

프로젝트의 코드 파일, 산출물 파일, 실행 순서, 현재 구현 범위는 위 한국어 문서에 정리되어 있습니다.

This repo implements Stage 1 building blocks:
- monocular depth estimation (dummy or MoGe)
- RGB-D backprojection to a point cloud
- MediaPipe hand bounding boxes
- hand crop extraction for HaMeR
- HaMeR/MANO mesh metadata ingestion and projection verification

**Environments**
- Main environment: `.venv` (Python 3.11). Used for MoGe depth wrapper, Open3D visualization, MediaPipe bbox detection, point cloud generation, and projection verification.
- HaMeR environment: `external/hamer/.hamer` (Python 3.10). Used only for HaMeR core inference and MANO mesh/joints generation.

**Quick repo layout**
- `inputs/` — drop `exo.jpg` or other source images here.
- `outputs/` — generated outputs (depth, point clouds, crops, hamer metadata).
- `src/` — project modules: depth estimator, pointcloud, I/O helpers, bbox & crop utilities.
- `scripts/` — utilities such as `verify_hamer_projection.py`.
- `external/hamer/` — external HaMeR repository (not included).

**Files generated in `outputs/`** (typical)
- `outputs/depth_raw.npy`, `depth_vis.png`, `depth_gray.png`, `depth_mask.png`
- `outputs/exo_point_cloud.ply`
- `outputs/hand_bboxes.json`, `hand_bbox_debug.png`
- `outputs/hand_crops/*` (hand crop PNGs + metadata)
- `outputs/hamer/*` (HaMeR outputs including `hamer_metadata.json`, `vertices_*.npy`, `faces_*.npy`)
- `outputs/hamer_projection/*` (projection debug images and `final_projection_report.md`)

**Files NOT included in Git**
- `.venv/` (main Python environment)
- `external/hamer/.hamer` (HaMeR Python env)
- `outputs/` (generated outputs)
- `inputs/exo.jpg` (example image)
- `external/hamer/_DATA/` (large HaMeR data assets)
- `hamer.ckpt` (HaMeR model checkpoint)
- `MANO_RIGHT.pkl`, `MANO_LEFT.pkl` (MANO model files)

## Setup (Windows, from scratch)
Prerequisites: Windows laptop, Python installers for 3.11 and 3.10, Git, and Git LFS if needed for large files.

1. Clone the repo:

```powershell
git clone <repo-url> egoworld-stage1
cd egoworld-stage1
```

2. Create and activate the main environment (Python 3.11):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. (Optional) Verify MoGe availability in `.venv` if you plan to use it.

4. Clone HaMeR into `external/hamer` and create its environment (Python 3.10):

```powershell
git clone <hamer-repo-url> external/hamer
cd external/hamer
py -3.10 -m venv .hamer
.\.hamer\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-hamer.txt
# return to project root
cd ../../
```

5. Place HaMeR required model files (not included):
- copy `hamer.ckpt` into `external/hamer/` or a path expected by your local HaMeR setup
- copy `MANO_RIGHT.pkl` and `MANO_LEFT.pkl` into `external/hamer/data/` (or configured MANO path)

6. Create the `inputs/` folder and add your exocentric image `exo.jpg`.

## Exact run commands (from project root, with `.venv` activated)
Note: run all main scripts using the main `.venv` unless explicitly stated.

- Depth + point cloud:

```powershell
python infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs
```

- Hand bounding boxes (MediaPipe):

```powershell
python infer_hand_bbox.py --image inputs/exo.jpg --out outputs
```

- Crop hands from bboxes:

```powershell
python crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
```

- Run HaMeR inference (use HaMeR environment): activate `.hamer` and run the external script in `external/hamer` or run the repo's wrapper that calls into HaMeR. Example (inside `external/hamer` with `.hamer` active):

```powershell
# activate HaMeR env
.\.hamer\Scripts\Activate.ps1
python infer_hamer_from_bboxes.py --bboxes ../../outputs/hand_bboxes.json --out ../../outputs/hamer
```

- Projection verification (main `.venv`):

```powershell
python scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
```

## Final projection rule
- Right hand: use normal camera projection from HaMeR camera translation.
- Left hand: after projecting mesh vertices to image coordinates, apply a 2D bbox mirror correction to the u coordinate:

$$u' = x_{\\text{left}} + x_{\\text{right}} - u$$

This mirrors the projected x-coordinates inside the MediaPipe bbox for left hands only (final adopted behavior).

## Current project status
- Depth pipeline: working (dummy + MoGe wrapper)
- MediaPipe bbox detection: working
- HaMeR mesh ingestion: working (external HaMeR required)
- Projection verification: working (left-hand 2D bbox mirror correction implemented)
- Next steps: `scripts/render_hand_depth.py` completion and final scale correction verification

## Troubleshooting & important notes
- Do NOT install `detectron2` on Windows for this Stage 1 workflow.
- Do NOT use HaMeR renderer, `pyrender`, or OpenGL for Stage 1 inference — HaMeR should be run as a pure-inference backend inside `external/hamer`.
- Use the main `.venv` (Python 3.11) for all Stage 1 scripts except HaMeR core inference.
- Use the `.hamer` Python 3.10 environment for HaMeR runs.
- If you see camera projection mismatches for left hands, ensure `hand_side_for_hamer` labels are correct and that `scripts/verify_hamer_projection.py` is run to visualize the final mirrored correction.

## Quick commands summary
```powershell
# setup main env
py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

# setup HaMeR env
cd external/hamer; py -3.10 -m venv .hamer; .\.hamer\Scripts\Activate.ps1; pip install -r requirements-hamer.txt

# run full Stage 1 (examples)
python infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs
python infer_hand_bbox.py --image inputs/exo.jpg --out outputs
python crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
# activate .hamer then run HaMeR wrapper
.\.hamer\Scripts\Activate.ps1; python infer_hamer_from_bboxes.py --bboxes ../../outputs/hand_bboxes.json --out ../../outputs/hamer
python scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
```

If anything in this README is unclear or you want the README tailored for Linux/macOS instead, open an issue or edit the file.

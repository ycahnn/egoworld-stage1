# Project Status — EgoWorld Stage 1

## 1) Completed
- MoGe depth output (via MoGe wrapper)
- `outputs/depth_raw.npy`
- `outputs/exo_point_cloud.ply` generation (RGB-D backprojection)
- MediaPipe `outputs/hand_bboxes.json`
- Extracted hand crops in `outputs/hand_crops/`
- HaMeR / MANO outputs: per-hand vertices, joints, faces and exported OBJ meshes
- Camera and projection metadata saved (e.g., `outputs/hamer/hamer_metadata.json`)
- Projection verification implemented and diagnostic images produced
- Final adopted projection rule:
  - Right hand: normal camera projection
  - Left hand: after projection, apply 2D bbox mirror correction (u' = x_left + x_right - u)

## 2) Important generated outputs
- `outputs/depth_raw.npy`
- `outputs/exo_point_cloud.ply`
- `outputs/hand_bboxes.json`
- `outputs/hand_crops/` (PNG crops + metadata)
- `outputs/hamer/*_vertices.npy`
- `outputs/hamer/*_joints.npy`
- `outputs/hamer/*_faces.npy`
- `outputs/hamer/*_mesh.obj`
- `outputs/hamer_projection/final_projection_debug.png`

## 3) Not yet implemented / pending
- `scripts/render_hand_depth.py` (render per-hand depth rasterization)
- `outputs/hand_depth.npy` (per-hand depth arrays)
- scale factor `s*` estimation and application
- `outputs/depth_scaled.npy` and `outputs/exo_point_cloud_scaled.ply`

## 4) Environment notes
- Main environment: `.venv` — Python 3.11 (Stage 1 scripts, MoGe wrapper, MediaPipe, Open3D)
- HaMeR environment: `external/hamer/.hamer` — Python 3.10 (HaMeR core inference, MANO files)
- Important: avoid `detectron2` installation on Windows; do not use HaMeR renderer / `pyrender` / OpenGL for Stage 1 inference

## 5) Next recommended step
- Implement `scripts/render_hand_depth.py` using the final projection rule (left-hand 2D bbox mirror correction) and add scale-factor estimation so outputs `depth_scaled.npy` and `exo_point_cloud_scaled.ply` can be produced.

----
Small, actionable: run `python scripts/verify_hamer_projection.py` to visually confirm projection behavior before implementing rendering.
# Project Status: EgoWorld Stage 1

## What works

- MoGe depth branch is functional in the main `.venv` environment.
- `exo_point_cloud.ply` has been generated and visualized.
- MediaPipe hand bbox detection works.
- Handedness correction is implemented and working.
- Hand crop extraction from `outputs/hand_bboxes.json` works.
- HaMeR data files exist:
  - `MANO_RIGHT.pkl`
  - `MANO_LEFT.pkl`
  - `hamer.ckpt`

## What is partially working

- `infer_hamer_from_bboxes.py` reaches HaMeR model loading.
- HaMeR currently fails later in dataset/preprocessing utilities or dependency imports.
- The main Stage 1 pipeline is stable, while HaMeR integration remains isolated and under diagnostics.

## What is blocked

- HaMeR core inference is blocked by HaMeR-specific dependencies and preprocessing utilities.
- A missing or incompatible HaMeR dependency such as `webdataset` or related preprocessing modules is preventing a clean end-to-end run.
- The HaMeR environment currently cannot be assumed to work without additional setup.

## Recommended next steps

1. Run the project state checker in the main `.venv` environment.
2. Confirm the all-important HaMeR files under `external/hamer/_DATA`.
3. Keep the main `.venv` Stage 1 pipeline untouched while diagnosing HaMeR.
4. Add a controlled HaMeR integration step only after the environment and dependency status are confirmed.

## Reproduction commands

From project root:

```powershell
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -c "import numpy, cv2, open3d, mediapipe, moge"
.venv\Scripts\python.exe scripts\check_project_state.py
```

For HaMeR environment checks:

```powershell
external\hamer\.hamer\Scripts\python.exe --version
external\hamer\.hamer\Scripts\python.exe -c "import numpy, torch, chumpy, hamer"
external\hamer\.hamer\Scripts\python.exe -c "import webdataset, smplx, timm, pytorch_lightning, yacs"
```

## Notes

- Do not modify the MoGe depth pipeline unless explicitly requested.
- Do not modify the MediaPipe bbox detector unless explicitly requested.
- Do not install packages automatically from this diagnostic audit.

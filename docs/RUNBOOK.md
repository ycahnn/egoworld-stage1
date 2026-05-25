# Runbook

This runbook contains the exact PowerShell commands to rerun the current Stage 1 pipeline using the correct environments.

## Main pipeline environment

Use the main project environment at `.venv` for all Stage 1 scripts except HaMeR core inference.

```powershell
Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1"
.\.venv\Scripts\Activate.ps1
python --version
python infer_depth_pointcloud.py --image inputs/exo.jpg --out outputs
python infer_hand_bbox.py --image inputs/exo.jpg --out outputs
python crop_hands_from_bboxes.py --image inputs/exo.jpg --bbox_json outputs/hand_bboxes.json --out outputs/hand_crops
python scripts/verify_hamer_projection.py --image inputs/exo.jpg --hamer_dir outputs/hamer --bbox_json outputs/hand_bboxes.json --out outputs/hamer_projection
python scripts/check_workspace_integrity.py
```

## HaMeR inference environment

Use the HaMeR Python environment in `external/hamer/.hamer` for HaMeR core inference.

```powershell
Set-Location "c:\Users\Youngchan Ahn\Desktop\egoworld-stage1\external\hamer"
.\.hamer\Scripts\Activate.ps1
python --version
python infer_hamer_from_bboxes.py --bboxes ..\..\outputs\hand_bboxes.json --out ..\..\outputs\hamer
```

## Notes

- Do not use system Python for Stage 1. Always use `.\.venv\Scripts\python.exe` for workspace validation and main scripts.
- Do not modify unrelated model code or move external environments like `external/hamer/.hamer` or `external/hamer/_DATA`.
- If HaMeR inference is run manually, keep `external/hamer/.hamer` isolated from the main `.venv` environment.

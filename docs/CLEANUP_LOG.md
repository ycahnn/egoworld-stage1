# Cleanup Log

This file documents files moved to `_trash_review` during workspace cleanup.

- `_trash_review/outputs/pose/`
  - reason: old failed `P_exo` attempt using HaMeR `joints.npy` + `pred_cam_t_full`.
  - source: `outputs/pose/`

- `_trash_review/outputs/pose_depth/P_exo_pose_map.png`
  - reason: non-final pose visualization output not part of the final pipeline.
  - source: `outputs/pose_depth/P_exo_pose_map.png`

- `_trash_review/outputs/hamer_projection/bbox_fallback_projection_debug.png`
  - reason: obsolete projection diagnostic image, replaced by the final projection debug output.
  - source: `outputs/hamer_projection/bbox_fallback_projection_debug.png`

- `_trash_review/scripts/export_p_exo.py`
  - reason: old failed exporter implementing the `joints + pred_cam_t_full` P_exo candidate path.
  - source: `scripts/export_p_exo.py`

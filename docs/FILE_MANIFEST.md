# File Manifest

## Inputs

- `inputs/exo.jpg`
  - type: image
  - meaning: source exocentric RGB input for Stage 1
  - status: final

## Depth and intrinsics

- `outputs/depth_raw.npy`
  - type: NumPy array
  - shape: (H, W) expected depth map
  - meaning: raw monocular depth estimate from the exo image
  - status: final
- `outputs/K_exo.npy`
  - type: NumPy array
  - shape: (3, 3)
  - meaning: exocentric camera intrinsics used for projection and depth-to-3D lifting
  - status: final

## Hand detection

- `outputs/hand_bboxes.json`
  - type: JSON
  - meaning: MediaPipe hand bounding box detections for the input image
  - status: final

## HaMeR outputs

- `outputs/hamer/hamer_metadata.json`
  - type: JSON
  - meaning: metadata for HaMeR inference outputs and hand ordering
  - status: final
- `outputs/hamer/*_vertices.npy`
  - type: NumPy arrays
  - meaning: HaMeR mesh vertices for each hand
  - status: final
- `outputs/hamer/*_faces.npy`
  - type: NumPy arrays
  - meaning: HaMeR mesh faces for each hand
  - status: final
- `outputs/hamer/*_joints.npy`
  - type: NumPy arrays
  - meaning: HaMeR joint coordinates in the hand root/local frame
  - status: final

## Projection debug

- `outputs/hamer_projection/final_projection_debug.png`
  - type: PNG image
  - meaning: final verified projection of HaMeR mesh onto the original image
  - status: final
- `outputs/hamer_projection/final_projection_report.md`
  - type: Markdown
  - meaning: summary report for final HaMeR projection results
  - status: final

## Hand depth and scaled point cloud

- `outputs/hamer_depth/hand_depth.npy`
  - type: NumPy array
  - shape: (H, W)
  - meaning: rendered hand depth map derived from projected HaMeR mesh
  - status: final
- `outputs/hamer_depth/hand_mask.png`
  - type: PNG image
  - meaning: binary mask for rendered hand depth region
  - status: final
- `outputs/scaled_depth/depth_scaled.npy`
  - type: NumPy array
  - shape: (H, W)
  - meaning: scaled exocentric depth aligned to hand depth scale
  - status: final
- `outputs/scaled_depth/exo_point_cloud_scaled.ply`
  - type: PLY mesh file
  - meaning: scaled exocentric point cloud generated from `depth_scaled.npy`
  - status: final

## Exocentric pose outputs

- `outputs/pose_depth/P_exo.npy`
  - type: NumPy array
  - shape: (N, 3)
  - meaning: final 3D exocentric pose points for MediaPipe landmarks
  - status: final
- `outputs/pose_depth/P_exo_2d.npy`
  - type: NumPy array
  - shape: (N, 2)
  - meaning: 2D hand landmark pixel positions used to lift `P_exo`
  - status: final
- `outputs/pose_depth/P_exo_valid.npy`
  - type: NumPy array
  - shape: (N,)
  - meaning: validity mask for final `P_exo` joints
  - status: final
- `outputs/pose_depth/P_exo_projection_debug.png`
  - type: PNG image
  - meaning: projection debug image for the final `P_exo` result
  - status: final
- `outputs/pose_depth/P_exo_metadata.json`
  - type: JSON
  - meaning: metadata describing how `P_exo` was generated and joint order
  - status: final
- `outputs/pose_depth/P_exo_skeleton_black.png`
  - type: PNG image
  - meaning: black-background rendering of the final `P_exo` skeleton
  - status: final

## Scripts and helpers

- `scripts/check_workspace_integrity.py`
  - type: Python script
  - meaning: verify required final workspace outputs and print shapes
  - status: final
- `scripts/verify_hamer_projection.py`
  - type: Python script
  - meaning: verify HaMeR projection onto the original image
  - status: final
- `scripts/render_hand_depth.py`
  - type: Python script
  - meaning: render hand depth from HaMeR projection outputs
  - status: final
- `scripts/render_p_exo_skeleton_on_black.py`
  - type: Python script
  - meaning: render `P_exo` skeleton on black background
  - status: final

## Quarantined files

- `_trash_review/outputs/pose/`
  - type: folder
  - meaning: failed old P_exo attempt using HaMeR `joints.npy` + `pred_cam_t_full`
  - status: obsolete
- `_trash_review/outputs/pose_depth/P_exo_pose_map.png`
  - type: PNG image
  - meaning: non-final pose visualization image
  - status: obsolete
- `_trash_review/outputs/hamer_projection/bbox_fallback_projection_debug.png`
  - type: PNG image
  - meaning: non-final projection diagnostic
  - status: obsolete
- `_trash_review/scripts/export_p_exo.py`
  - type: Python script
  - meaning: old failed P_exo exporter using HaMeR joints + `pred_cam_t_full`
  - status: obsolete

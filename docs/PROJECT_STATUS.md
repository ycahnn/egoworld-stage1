# Project Status

## Current achievement summary

The current EgoWorld Stage 1 reproduction workspace is in a working state for the final Stage 1 pipeline outputs. The main exocentric-to-hand-pose pipeline has been validated through depth estimation, hand bbox detection, HaMeR mesh/joints export, projection verification, hand-depth rendering, scale alignment, scaled depth generation, and P_exo export from 2D hand landmarks.

## What is successfully implemented

- MoGe depth estimation and `outputs/depth_raw.npy` generation
- `outputs/K_exo.npy` intrinsics export
- MediaPipe hand bounding box detection and `outputs/hand_bboxes.json`
- hand crop extraction for downstream HaMeR processing
- HaMeR mesh/joint export into `outputs/hamer/` with `*_vertices.npy`, `*_joints.npy`, `*_faces.npy`, and `hamer_metadata.json`
- final HaMeR projection verification via `outputs/hamer_projection/final_projection_debug.png`
- hand depth rendering generation in `outputs/hamer_depth/` with `hand_depth.npy` and `hand_mask.png`
- scaled depth alignment using hand depth and raw depth
- generating `outputs/scaled_depth/depth_scaled.npy` and `outputs/scaled_depth/exo_point_cloud_scaled.ply`
- exporting final `P_exo` from `outputs/pose_depth/` using 2D hand landmarks, scaled depth, and `K_exo`
- rendering the final black-background `P_exo` skeleton in `outputs/pose_depth/P_exo_skeleton_black.png`

## What is not implemented yet

- a true egocentric pose estimator (`P_ego`) is not implemented
- P_ego coordinate conversion and joint ordering are still pending
- no final Stage 2 or downstream task beyond P_exo generation is available

## Current final outputs

- `inputs/exo.jpg`
- `outputs/depth_raw.npy`
- `outputs/K_exo.npy`
- `outputs/hand_bboxes.json`
- `outputs/hamer/hamer_metadata.json`
- `outputs/hamer/*_vertices.npy`
- `outputs/hamer/*_faces.npy`
- `outputs/hamer/*_joints.npy`
- `outputs/hamer_projection/final_projection_debug.png`
- `outputs/hamer_projection/final_projection_report.md`
- `outputs/hamer_depth/hand_depth.npy`
- `outputs/hamer_depth/hand_mask.png`
- `outputs/scaled_depth/depth_scaled.npy`
- `outputs/scaled_depth/exo_point_cloud_scaled.ply`
- `outputs/pose_depth/P_exo.npy`
- `outputs/pose_depth/P_exo_2d.npy`
- `outputs/pose_depth/P_exo_valid.npy`
- `outputs/pose_depth/P_exo_metadata.json`
- `outputs/pose_depth/P_exo_projection_debug.png`
- `outputs/pose_depth/P_exo_skeleton_black.png`

## Next step: P_ego estimator

The next development step is to implement `P_ego`, an egocentric pose representation aligned to the same joint order and coordinate conventions as `P_exo`. Once `P_ego` is available, the workspace should support paired exocentric and egocentric pose outputs for the same frame.

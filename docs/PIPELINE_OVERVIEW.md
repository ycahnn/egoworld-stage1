# Pipeline Overview

This document describes the Stage 1 pipeline flow from an input exocentric RGB image to final exocentric pose outputs.

1. Input exo image
   - The pipeline starts with `inputs/exo.jpg` as the exocentric source image.

2. MoGe depth
   - A monocular depth estimator produces `outputs/depth_raw.npy` and related depth visualization files.

3. MediaPipe bbox
   - MediaPipe detects hand bounding boxes and saves `outputs/hand_bboxes.json`.

4. crop hands
   - Hand crops are extracted from the original image using the detected bounding boxes for HaMeR inference.

5. HaMeR mesh/joints
   - HaMeR inference generates per-hand mesh and joint outputs in `outputs/hamer/`, including `*_vertices.npy`, `*_joints.npy`, `*_faces.npy`, and `hamer_metadata.json`.

6. project mesh onto original image
   - The projected HaMeR mesh is verified in `outputs/hamer_projection/`, with the final approved result saved as `final_projection_debug.png`.

7. render hand_depth.npy
   - Hand depth is rendered into `outputs/hamer_depth/hand_depth.npy` and `hand_mask.png`.

8. compute scale factor from D_hand / D_exo
   - The pipeline computes a scale alignment between the hand depth and exocentric depth to produce a correctly scaled depth map.

9. create depth_scaled.npy
   - The scaled depth map is saved to `outputs/scaled_depth/depth_scaled.npy`.

10. create exo_point_cloud_scaled.ply
    - A scaled exocentric point cloud is exported as `outputs/scaled_depth/exo_point_cloud_scaled.ply`.

11. create P_exo from P_exo_2d + depth_scaled + K_exo
    - 2D hand landmark positions are lifted into 3D using the scaled depth map and intrinsics `outputs/K_exo.npy`.
    - Final pose outputs are saved under `outputs/pose_depth/` as `P_exo.npy`, `P_exo_2d.npy`, `P_exo_valid.npy`, and metadata.

12. render P_exo skeleton on black
    - The final exocentric skeleton is rendered on a black canvas and saved to `outputs/pose_depth/P_exo_skeleton_black.png`.

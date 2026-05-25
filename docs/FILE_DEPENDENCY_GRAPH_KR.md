# 파일 의존성 그래프

inputs/exo.jpg
  ↓ infer_depth_pointcloud.py
outputs/depth_raw.npy
outputs/K_exo.npy
outputs/exo_point_cloud.ply
outputs/depth_vis.png
outputs/depth_gray.png
outputs/depth_mask.png
outputs/depth_intrinsics.json

inputs/exo.jpg
  ↓ infer_hand_bbox.py
outputs/hand_bboxes.json
outputs/hand_bbox_debug.png

outputs/hand_bboxes.json + inputs/exo.jpg
  ↓ crop_hands_from_bboxes.py
outputs/hand_crops/
outputs/hand_crops/hand_crops_metadata.json
outputs/hand_crops/crop_debug.png

outputs/hand_bboxes.json + inputs/exo.jpg
  ↓ external/hamer/.hamer\Scripts\python.exe infer_hamer_from_bboxes.py
outputs/hamer/*_vertices.npy
outputs/hamer/*_faces.npy
outputs/hamer/*_joints.npy
outputs/hamer/*_mesh.obj
outputs/hamer/hamer_metadata.json
outputs/hamer/hamer_raw_output_summary.json
outputs/hamer/hamer_bbox_debug.png

outputs/hamer/*_vertices.npy + outputs/hamer/*_faces.npy + outputs/hand_bboxes.json + inputs/exo.jpg
  ↓ scripts/render_hand_depth.py
outputs/hamer_depth/hand_depth.npy
outputs/hamer_depth/hand_mask.png
outputs/hamer_depth/hand_depth_vis.png
outputs/hamer_depth/hand_depth_debug.png
outputs/hamer_depth/hand_depth_report.md

outputs/depth_raw.npy + outputs/hamer_depth/hand_depth.npy + outputs/hamer_depth/hand_mask.png + inputs/exo.jpg
  ↓ scripts/scale_depth_with_hand.py
outputs/scaled_depth/depth_scaled.npy
outputs/scaled_depth/depth_scaled_vis.png
outputs/scaled_depth/scale_valid_mask.png
outputs/scaled_depth/exo_point_cloud_scaled.ply
outputs/scaled_depth/scale_report.md
outputs/scaled_depth/scale_ratio_hist.png

outputs/scaled_depth/depth_scaled.npy + outputs/K_exo.npy + outputs/hand_bboxes.json + inputs/exo.jpg
  ↓ scripts/export_p_exo_from_depth.py
outputs/pose_depth/P_exo.npy
outputs/pose_depth/P_exo_2d.npy
outputs/pose_depth/P_exo_valid.npy
outputs/pose_depth/P_exo_metadata.json
outputs/pose_depth/P_exo_projection_debug.png
outputs/pose_depth/P_exo_report.md

outputs/pose_depth/P_exo.npy + outputs/pose_depth/P_exo_2d.npy + outputs/pose_depth/P_exo_valid.npy + outputs/K_exo.npy + inputs/exo.jpg
  ↓ scripts/render_p_exo_skeleton_on_black.py
outputs/pose_depth/P_exo_skeleton_black.png

outputs/hamer/hamer_metadata.json + outputs/hand_bboxes.json + inputs/exo.jpg
  ↓ scripts/verify_hamer_projection.py
outputs/hamer_projection/final_projection_debug.png
outputs/hamer_projection/final_projection_report.md
outputs/hamer_projection/bbox_fallback_projection_debug.png

outputs/depth_raw.npy
outputs/K_exo.npy
outputs/hand_bboxes.json
outputs/hamer/hamer_metadata.json
outputs/hamer_projection/final_projection_debug.png
outputs/hamer_depth/hand_depth.npy
outputs/hamer_depth/hand_mask.png
outputs/scaled_depth/depth_scaled.npy
outputs/scaled_depth/exo_point_cloud_scaled.ply
outputs/pose_depth/P_exo.npy
outputs/pose_depth/P_exo_2d.npy
outputs/pose_depth/P_exo_valid.npy
outputs/pose_depth/P_exo_projection_debug.png
outputs/pose_depth/P_exo_skeleton_black.png
  ↓ scripts/check_workspace_integrity.py
(최종 워크스페이스 검증)

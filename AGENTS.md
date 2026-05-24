# EgoWorld Stage 1 Agent Guidelines

## Project overview

This repository implements **EgoWorld Stage 1 only**. The focus is on:

- exocentric RGB image depth estimation
- RGB-D backprojection into a point cloud
- MediaPipe hand bounding box detection
- hand crop extraction for downstream hand pose inference

HaMeR is an external integration target, not the core repository implementation.

## Environment separation rule

- `.venv` is the main project environment.
  - Used for MoGe depth estimation
  - Open3D visualization
  - MediaPipe hand bbox detection
  - hand crop extraction
  - general Stage 1 Python logic

- `external/hamer/.hamer` is the HaMeR environment.
  - Used only for HaMeR core inference
  - MANO mesh/joints generation
  - any HaMeR-specific package imports

## Important rules

- Never install or use `detectron2` on Windows native for this Stage 1 workflow.
- Never use HaMeR renderer / `pyrender` / OpenGL for Stage 1 inference.
- Use MediaPipe hand bboxes, not detectron2/ViTPose, for hand localization.
- HaMeR integration must use `hand_side_for_hamer`, not `raw_handedness`.
- Do not modify the working MoGe depth pipeline unless specifically requested.
- Do not change the MediaPipe bbox detector unless asked.

## Current operational policy

- Keep the main `.venv` environment dedicated to Stage 1 components.
- Keep `external/hamer/.hamer` isolated for HaMeR execution.
- Any HaMeR workaround should avoid touching Stage 1 logic unless the issue is explicitly in the HaMeR integration path.
- Document cross-environment dependencies clearly when they arise.

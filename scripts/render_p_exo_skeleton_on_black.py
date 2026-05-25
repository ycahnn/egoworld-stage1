#!/usr/bin/env python3
"""Render P_exo skeleton on pure black background.

Defaults are set so this can be run from workspace root without args.

Usage:
  python scripts/render_p_exo_skeleton_on_black.py
  python scripts/render_p_exo_skeleton_on_black.py --input outputs/pose_depth/P_exo.npy --out outputs/pose_depth/P_exo_skeleton_black.png

Behavior:
 - Prefer `outputs/pose_depth/P_exo_2d.npy` for 2D points (original image pixel coords).
 - Otherwise reproject `P_exo.npy` using `outputs/K_exo.npy` (same formula used in pipeline).
 - Use `outputs/pose_depth/P_exo_valid.npy` when present to skip invalid joints/edges.
 - Canvas size: prefer `inputs/exo.jpg` image size; otherwise infer from 2D points or default to 1024x1024.
"""
import argparse
import json
from pathlib import Path
import sys
import os
#!/usr/bin/env python3
"""
Render P_exo skeleton on pure black background using a fixed-size canvas.

Note: the previous visualizer used plotting-backed save options which caused
automatic cropping/`bbox_inches='tight'` style behavior and produced a
smaller output image. This version draws directly onto a fixed-size pixel
canvas (via OpenCV) sized to match the original input image to avoid any
cropping or resizing.

This script prefers OpenCV (`cv2`) from the activated virtual environment.
Run explicitly with the workspace venv:
  .\.venv\Scripts\python.exe scripts/render_p_exo_skeleton_on_black.py

Defaults (no args):
  input: outputs/pose_depth/P_exo.npy
  p_exo_2d: outputs/pose_depth/P_exo_2d.npy (preferred)
  valid: outputs/pose_depth/P_exo_valid.npy
  K: outputs/K_exo.npy
  image: inputs/exo.jpg
  out: outputs/pose_depth/P_exo_skeleton_black.png
"""

import argparse
import sys
from pathlib import Path
import os

import numpy as np

try:
    import cv2
except Exception:
    cv2 = None


MEDIAPIPE_EDGES = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
]

FINGER_COLORS_BGR = {
    'thumb': (0,0,255),    # red
    'index': (0,255,255),  # yellow
    'middle': (0,255,0),   # green
    'ring': (255,255,0),   # cyan
    'pinky': (255,0,255),  # magenta
    'wrist': (255,255,255),# white
}


def joint_color_bgr(idx):
    if idx == 0:
        return FINGER_COLORS_BGR['wrist']
    if 1 <= idx <= 4:
        return FINGER_COLORS_BGR['thumb']
    if 5 <= idx <= 8:
        return FINGER_COLORS_BGR['index']
    if 9 <= idx <= 12:
        return FINGER_COLORS_BGR['middle']
    if 13 <= idx <= 16:
        return FINGER_COLORS_BGR['ring']
    if 17 <= idx <= 20:
        return FINGER_COLORS_BGR['pinky']
    return (128,128,128)


def reproject_from_3d(P_exo, K):
    fx = float(K[0,0]); fy = float(K[1,1]); cx = float(K[0,2]); cy = float(K[1,2])
    X = P_exo[:, 0]
    Y = P_exo[:, 1]
    Z = P_exo[:, 2]
    Z_safe = np.where(Z == 0, np.nan, Z)
    u = (X * fx) / Z_safe + cx
    v = (Y * fy) / Z_safe + cy
    proj = np.stack([u, v], axis=1)
    return proj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', default='inputs/exo.jpg')
    parser.add_argument('--p_exo', default='outputs/pose_depth/P_exo.npy')
    parser.add_argument('--p_exo_2d', default='outputs/pose_depth/P_exo_2d.npy')
    parser.add_argument('--valid', default='outputs/pose_depth/P_exo_valid.npy')
    parser.add_argument('--K', default='outputs/K_exo.npy')
    parser.add_argument('--out', default='outputs/pose_depth/P_exo_skeleton_black.png')
    args = parser.parse_args()

    print('Python executable:', sys.executable)

    # Require cv2 from the venv
    if cv2 is None:
        print('Error: OpenCV (cv2) not available in this interpreter.\nRun with the workspace venv: .\\.venv\\Scripts\\python.exe')
        sys.exit(2)

    img_path = Path(args.image)
    p_exo_path = Path(args.p_exo)
    p_exo_2d_path = Path(args.p_exo_2d)
    valid_path = Path(args.valid)
    K_path = Path(args.K)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove previous bad output if exists
    if out_path.exists():
        try:
            out_path.unlink()
        except Exception:
            pass

    # Load image to get exact canvas size
    if not img_path.exists():
        print('Input image not found:', img_path)
        sys.exit(1)
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if img is None:
        print('Failed to load image with cv2:', img_path)
        sys.exit(1)
    img_h, img_w = img.shape[:2]

    # Load or reproject 2D points
    used_source = None
    if p_exo_2d_path.exists():
        P2d = np.load(str(p_exo_2d_path))
        used_source = str(p_exo_2d_path)
    else:
        if not p_exo_path.exists():
            print('Missing P_exo and P_exo_2d:', p_exo_path, p_exo_2d_path)
            sys.exit(1)
        if not K_path.exists():
            print('Missing K_exo for reprojection:', K_path)
            sys.exit(1)
        P_exo = np.load(str(p_exo_path))
        K = np.load(str(K_path))
        P2d = reproject_from_3d(P_exo, K)
        used_source = f'reprojected from {p_exo_path} + {K_path}'

    if P2d.ndim != 2 or P2d.shape[1] != 2:
        raise ValueError('P_exo_2d must be shape (N,2) after loading/reprojection')

    N = P2d.shape[0]
    if N not in (21, 42):
        raise ValueError('Unexpected number of joints: expected 21 or 42, got %d' % N)
    num_hands = 1 if N == 21 else 2

    # Valid mask
    if valid_path.exists():
        valid = np.load(str(valid_path)).astype(bool)
    else:
        valid = np.isfinite(P2d).all(axis=1)

    # Create black canvas exactly matching original image size
    canvas = np.zeros((img_h, img_w, 3), dtype=np.uint8)

    joints_per_hand = 21
    for h_idx in range(num_hands):
        start = h_idx * joints_per_hand
        end = start + joints_per_hand
        hand2d = P2d[start:end]
        hand_valid = valid[start:end]

        # draw edges
        for a, b in MEDIAPIPE_EDGES:
            if not (hand_valid[a] and hand_valid[b]):
                continue
            pa = hand2d[a]
            pb = hand2d[b]
            if not (np.isfinite(pa).all() and np.isfinite(pb).all()):
                continue
            p1 = (int(round(float(pa[0]))), int(round(float(pa[1]))))
            p2 = (int(round(float(pb[0]))), int(round(float(pb[1]))))
            color = joint_color_bgr(b)
            cv2.line(canvas, p1, p2, color, thickness=3, lineType=cv2.LINE_AA)

        # draw joints
        for j in range(joints_per_hand):
            pj = hand2d[j]
            if not np.isfinite(pj).all():
                continue
            center = (int(round(float(pj[0]))), int(round(float(pj[1]))))
            color = joint_color_bgr(j)
            cv2.circle(canvas, center, 5, color, -1, lineType=cv2.LINE_AA)

    # Save output
    success = cv2.imwrite(str(out_path), canvas)
    if not success:
        print('Failed to write output image:', out_path)
        sys.exit(1)

    print('Python executable:', sys.executable)
    print('Used 2D source:', used_source)
    print('Image size:', img_w, 'x', img_h)
    print('Number of hands:', num_hands)
    print('Saved:', str(out_path))


if __name__ == '__main__':
    main()

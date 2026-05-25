#!/usr/bin/env python3
"""Export P_exo by lifting 2D hand landmarks using a scaled depth map and intrinsics.

Usage example:
python scripts/export_p_exo_from_depth.py --image inputs/exo.jpg --depth outputs/scaled_depth/depth_scaled.npy --K outputs/K_exo.npy --out outputs/pose_depth

This script follows the workspace requirements: it prefers landmarks from
outputs/hand_bboxes.json when available, otherwise runs MediaPipe Hands.
"""
import argparse
import json
import os
from pathlib import Path
import sys

import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception:
    mp = None


def load_json_landmarks(json_path, img_w, img_h):
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception:
        return None

    # Heuristic: look for a top-level list/dict containing hands with 'landmarks'
    hands = None
    if isinstance(data, dict):
        # common keys
        for key in ('hands', 'hand_bboxes', 'detections'):
            if key in data and isinstance(data[key], list):
                hands = data[key]
                break
        # sometimes stored as list under 'annotations' or directly as landmarks
        if hands is None:
            # search for any list of dicts that look like hands
            for v in data.values():
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    hands = v
                    break
    elif isinstance(data, list):
        hands = data

    if not hands:
        return None

    results = []
    for h in hands:
        lm = None
        handedness = None
        if isinstance(h, dict):
            # common field names
            for k in ('landmarks', 'keypoints', 'kps'):
                if k in h:
                    lm = h[k]
                    break
            for k in ('handedness', 'hand_label'):
                if k in h:
                    handedness = h[k]
                    break
        # If lm is nested list of length 21 with pairs or triples
        if lm and isinstance(lm, list) and len(lm) == 21:
            pts = []
            for p in lm:
                if isinstance(p, dict) and 'x' in p and 'y' in p:
                    x = p['x']; y = p['y']
                elif isinstance(p, (list, tuple)) and len(p) >= 2:
                    x = p[0]; y = p[1]
                else:
                    x = None; y = None
                if x is None:
                    pts = None
                    break
                # convert normalized to pixels if needed
                if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                    u = float(x) * img_w
                    v = float(y) * img_h
                else:
                    u = float(x)
                    v = float(y)
                pts.append((u, v))
            if pts is not None:
                results.append({'landmarks': pts, 'handedness': handedness})

    if len(results) == 0:
        return None
    return results


def run_mediapipe_on_image(img_bgr, max_num_hands=2, min_detection_confidence=0.5):
    if mp is None:
        raise RuntimeError('mediapipe not available; cannot run hand detector')
    mp_hands = mp.solutions.hands
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    with mp_hands.Hands(static_image_mode=True, max_num_hands=max_num_hands,
                        min_detection_confidence=min_detection_confidence) as hands:
        res = hands.process(img_rgb)
    if not res.multi_hand_landmarks:
        return []
    out = []
    h, w = img_bgr.shape[:2]
    for lm, hh in zip(res.multi_hand_landmarks, res.multi_handedness):
        pts = []
        for l in lm.landmark:
            x = l.x; y = l.y
            if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                pts.append((x * w, y * h))
            else:
                pts.append((x, y))
        handedness = None
        try:
            handedness = hh.classification[0].label
        except Exception:
            handedness = None
        out.append({'landmarks': pts, 'handedness': handedness})
    return out


def sample_depth_median(depth, u, v, radii=(3, 5, 10, 20)):
    h, w = depth.shape[:2]
    for r in radii:
        x0 = int(round(u)) - r
        x1 = int(round(u)) + r + 1
        y0 = int(round(v)) - r
        y1 = int(round(v)) + r + 1
        x0c = max(0, x0); x1c = min(w, x1)
        y0c = max(0, y0); y1c = min(h, y1)
        if x0c >= x1c or y0c >= y1c:
            continue
        patch = depth[y0c:y1c, x0c:x1c]
        if patch.size == 0:
            continue
        vals = patch[np.isfinite(patch) & (patch > 0)]
        if vals.size > 0:
            return float(np.median(vals)), r
    return None, None


def reorder_hands_by_label(hands):
    # Expect each hand dict has 'handedness' possibly 'Left'/'Right'
    left = [h for h in hands if h.get('handedness') in ('Left', 'LEFT', 'left')]
    right = [h for h in hands if h.get('handedness') in ('Right', 'RIGHT', 'right')]
    unknown = [h for h in hands if h not in left and h not in right]
    ordered = []
    if left:
        ordered.extend(left)
    if right:
        ordered.extend(right)
    # Append any unknowns by x-order (wrist x)
    if unknown:
        def mean_x(h):
            try:
                xs = [p[0] for p in h['landmarks']]
                return float(np.mean(xs))
            except Exception:
                return 1e9
        unknown_sorted = sorted(unknown, key=mean_x)
        ordered.extend(unknown_sorted)
    return ordered


def draw_debug_projection(img_bgr, proj_pts, orig_2d, valid_mask, save_path):
    img = img_bgr.copy()
    # draw original 2D landmarks in green, reprojected in blue, invalid in red
    for i, (o, p, v) in enumerate(zip(orig_2d, proj_pts, valid_mask)):
        ox, oy = int(round(o[0])), int(round(o[1]))
        px, py = int(round(p[0])), int(round(p[1])) if np.isfinite(p[0]) else (None, None)
        if v:
            cv2.drawMarker(img, (ox, oy), (0, 255, 0), cv2.MARKER_CROSS, 8, 2)
            if px is not None:
                cv2.drawMarker(img, (px, py), (255, 0, 0), cv2.MARKER_TILTED_CROSS, 8, 1)
        else:
            cv2.drawMarker(img, (ox, oy), (0, 0, 255), cv2.MARKER_STAR, 10, 2)
    cv2.imwrite(save_path, img)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--image', required=True)
    p.add_argument('--depth', required=True)
    p.add_argument('--K', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--verbose', action='store_true')
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(args.image)
    if img is None:
        print('Failed to read image:', args.image)
        sys.exit(1)
    h, w = img.shape[:2]

    depth = np.load(args.depth)
    if depth is None:
        print('Failed to load depth:', args.depth)
        sys.exit(1)
    if depth.shape[0] != h or depth.shape[1] != w:
        print('Warning: depth shape', depth.shape, 'does not match image shape', (h, w))

    K = np.load(args.K)
    if K.shape == (3, 3):
        fx = float(K[0, 0]); fy = float(K[1, 1]); cx = float(K[0, 2]); cy = float(K[1, 2])
    else:
        raise ValueError('K must be 3x3')

    # Try reading landmarks from outputs/hand_bboxes.json
    json_candidates = [
        'outputs/hand_bboxes.json',
        'inputs/hand_bboxes.json',
        'outputs/hand_bboxes.json'
    ]
    landmarks_source = None
    hands = None
    for jp in json_candidates:
        res = load_json_landmarks(jp, w, h)
        if res:
            hands = res
            landmarks_source = jp
            break

    if not hands:
        # run MediaPipe
        if mp is None:
            print('MediaPipe not installed and no landmarks in JSON. Install mediapipe or provide landmarks.')
            sys.exit(1)
        hands = run_mediapipe_on_image(img)
        landmarks_source = 'MediaPipe'

    if len(hands) == 0:
        print('No hands detected')
        sys.exit(1)

    # enforce stable order: left then right
    hands = reorder_hands_by_label(hands)
    hand_order = []
    all_2d = []
    for hdict in hands:
        all_2d.extend(hdict['landmarks'])
        hand_order.append(hdict.get('handedness') if hdict.get('handedness') else 'unknown')

    N = len(all_2d)
    P_exo = np.full((N, 3), np.nan, dtype=float)
    P_exo_2d = np.zeros((N, 2), dtype=float)
    P_valid = np.zeros((N,), dtype=bool)
    fallback_radii = []

    for i, (u, v) in enumerate(all_2d):
        P_exo_2d[i, 0] = float(u)
        P_exo_2d[i, 1] = float(v)
        z, used_r = sample_depth_median(depth, u, v, radii=(3, 5, 10, 20))
        fallback_radii.append(used_r)
        if z is None:
            P_valid[i] = False
            continue
        X = (float(u) - cx) * z / fx
        Y = (float(v) - cy) * z / fy
        P_exo[i, :] = [X, Y, z]
        P_valid[i] = True

    # Save outputs
    np.save(out_dir / 'P_exo.npy', P_exo)
    np.save(out_dir / 'P_exo_2d.npy', P_exo_2d)
    np.save(out_dir / 'P_exo_valid.npy', P_valid)

    metadata = {
        'coordinate_system': 'exo_camera_from_scaled_depth',
        'source_depth': str(args.depth),
        'source_intrinsics': str(args.K),
        'keypoint_source': landmarks_source,
        'hand_order': hand_order,
        'joint_order': ['mediapipe_landmark_%02d' % i for i in range(21)],
        'note': 'This P_exo is depth-lifted 2D hand landmarks, not raw HaMeR local joints'
    }
    with open(out_dir / 'P_exo_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    # create debug projection image
    proj_pts = np.full((N, 2), np.nan, dtype=float)
    for i in range(N):
        if P_valid[i]:
            X, Y, Z = P_exo[i]
            u_proj = (X * fx) / Z + cx
            v_proj = (Y * fy) / Z + cy
            proj_pts[i, 0] = u_proj
            proj_pts[i, 1] = v_proj

    debug_png = out_dir / 'P_exo_projection_debug.png'
    draw_debug_projection(img, proj_pts, P_exo_2d, P_valid, str(debug_png))

    # write a short report
    report_lines = []
    report_lines.append('# P_exo depth-lift report')
    report_lines.append('')
    report_lines.append(f'- image: {args.image}')
    report_lines.append(f'- depth: {args.depth}')
    report_lines.append(f'- intrinsics: {args.K}')
    report_lines.append(f'- keypoint_source: {landmarks_source}')
    report_lines.append(f'- num_keypoints: {N}')
    report_lines.append(f'- num_valid: {int(P_valid.sum())}')
    report_lines.append(f'- fallback_radii_counts: ' + json.dumps({
        str(r): int(sum(1 for rr in fallback_radii if rr == r)) for r in set([r for r in fallback_radii if r is not None])
    }))
    report_lines.append('')
    report_lines.append('Files saved:')
    report_lines.append(f'- {out_dir}/P_exo.npy')
    report_lines.append(f'- {out_dir}/P_exo_2d.npy')
    report_lines.append(f'- {out_dir}/P_exo_valid.npy')
    report_lines.append(f'- {out_dir}/P_exo_metadata.json')
    report_lines.append(f'- {out_dir}/P_exo_projection_debug.png')

    with open(out_dir / 'P_exo_report.md', 'w') as f:
        f.write('\n'.join(report_lines))

    print('Saved P_exo outputs to', str(out_dir))


if __name__ == '__main__':
    main()

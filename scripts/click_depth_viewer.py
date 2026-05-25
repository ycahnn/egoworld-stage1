#!/usr/bin/env python3
"""Interactive depth viewer: click pixels to inspect raw, scaled, and hand depth values."""

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


class DepthViewer:
    def __init__(self, image_path, raw_depth_path, scaled_depth_path, hand_depth_path, output_csv):
        self.image_path = Path(image_path)
        self.output_csv = Path(output_csv)
        self.clicks = []

        # Load image
        self.image = cv2.imread(str(self.image_path), cv2.IMREAD_COLOR)
        if self.image is None:
            raise FileNotFoundError(f"Image not found: {self.image_path}")
        self.display = self.image.copy()
        self.height, self.width = self.image.shape[:2]

        # Load depth maps
        self.raw_depth = np.load(str(raw_depth_path)) if raw_depth_path else None
        self.scaled_depth = np.load(str(scaled_depth_path)) if scaled_depth_path else None
        self.hand_depth = np.load(str(hand_depth_path)) if hand_depth_path else None

        # Validate shapes
        if self.raw_depth is not None and self.raw_depth.shape != (self.height, self.width):
            raise ValueError(f"Raw depth shape {self.raw_depth.shape} does not match image {(self.height, self.width)}")
        if self.scaled_depth is not None and self.scaled_depth.shape != (self.height, self.width):
            raise ValueError(f"Scaled depth shape {self.scaled_depth.shape} does not match image {(self.height, self.width)}")
        if self.hand_depth is not None and self.hand_depth.shape != (self.height, self.width):
            raise ValueError(f"Hand depth shape {self.hand_depth.shape} does not match image {(self.height, self.width)}")

        print(f"Image: {self.image_path}")
        print(f"  Size: {self.width}x{self.height}")
        if self.raw_depth is not None:
            print(f"  Raw depth loaded")
        if self.scaled_depth is not None:
            print(f"  Scaled depth loaded")
        if self.hand_depth is not None:
            print(f"  Hand depth loaded")
        print("\nClick on pixels to inspect depth values. Press ESC to exit and save.")

    def mouse_callback(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        # Get depth values at this pixel
        raw_val = self.raw_depth[y, x] if self.raw_depth is not None else None
        scaled_val = self.scaled_depth[y, x] if self.scaled_depth is not None else None
        hand_val = self.hand_depth[y, x] if self.hand_depth is not None else None

        # Check validity
        raw_valid = raw_val is not None and np.isfinite(raw_val) and raw_val > 0
        scaled_valid = scaled_val is not None and np.isfinite(scaled_val) and scaled_val > 0
        hand_valid = hand_val is not None and np.isfinite(hand_val) and hand_val > 0

        # Format output
        print(f"\nClick at ({x}, {y}):")
        if raw_valid:
            print(f"  Raw depth: {raw_val:.6f}")
        else:
            print(f"  Raw depth: invalid")
        if scaled_valid:
            print(f"  Scaled depth: {scaled_val:.6f}")
        else:
            print(f"  Scaled depth: invalid")
        if hand_valid:
            print(f"  Hand depth: {hand_val:.6f}")
        else:
            print(f"  Hand depth: invalid")

        # Store click
        click_data = {
            "x": x,
            "y": y,
            "raw_depth": raw_val if raw_val is not None else float("nan"),
            "raw_valid": raw_valid,
            "scaled_depth": scaled_val if scaled_val is not None else float("nan"),
            "scaled_valid": scaled_valid,
            "hand_depth": hand_val if hand_val is not None else float("nan"),
            "hand_valid": hand_valid,
        }
        self.clicks.append(click_data)

        # Draw on display
        cv2.circle(self.display, (x, y), 5, (0, 255, 0), -1)
        text = f"({x},{y})"
        cv2.putText(
            self.display,
            text,
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            lineType=cv2.LINE_AA,
        )
        cv2.imshow("Depth Viewer", self.display)

    def run(self):
        cv2.namedWindow("Depth Viewer")
        cv2.setMouseCallback("Depth Viewer", self.mouse_callback)
        cv2.imshow("Depth Viewer", self.display)

        while True:
            key = cv2.waitKey(0)
            if key == 27:  # ESC
                break

        cv2.destroyAllWindows()
        self.save_csv()

    def save_csv(self):
        if not self.clicks:
            print("No clicks recorded.")
            return

        fieldnames = [
            "x",
            "y",
            "raw_depth",
            "raw_valid",
            "scaled_depth",
            "scaled_valid",
            "hand_depth",
            "hand_valid",
        ]
        with open(str(self.output_csv), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.clicks)
        print(f"\nSaved {len(self.clicks)} clicks to {self.output_csv}")


def parse_args():
    parser = argparse.ArgumentParser(description="Interactive depth viewer")
    parser.add_argument("--image", required=True, help="Path to input RGB image")
    parser.add_argument("--raw", required=False, help="Path to raw depth npy")
    parser.add_argument("--scaled", required=False, help="Path to scaled depth npy")
    parser.add_argument("--hand", required=False, help="Path to hand depth npy")
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    image_path = project_root / args.image
    raw_depth_path = project_root / args.raw if args.raw else None
    scaled_depth_path = project_root / args.scaled if args.scaled else None
    hand_depth_path = project_root / args.hand if args.hand else None
    output_csv = project_root / "outputs" / "depth_clicks.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    viewer = DepthViewer(image_path, raw_depth_path, scaled_depth_path, hand_depth_path, output_csv)
    viewer.run()


if __name__ == "__main__":
    main()

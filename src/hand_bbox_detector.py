from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def _normalize_handedness(raw_handedness: str | None) -> str | None:
    if raw_handedness is None:
        return None
    return raw_handedness.capitalize()


def _flip_handedness(raw_handedness: str | None, flip: bool) -> str | None:
    normalized = _normalize_handedness(raw_handedness)
    if normalized is None or not flip:
        return normalized
    if normalized == "Left":
        return "Right"
    if normalized == "Right":
        return "Left"
    return normalized


def _hand_side_for_hamer(handedness: str | None) -> str | None:
    if handedness is None:
        return None
    return handedness.lower()


@dataclass
class HandBbox:
    x1: int
    y1: int
    x2: int
    y2: int
    raw_handedness: str | None = None
    handedness: str | None = None
    hand_side_for_hamer: str | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "raw_handedness": self.raw_handedness,
            "handedness": self.handedness,
            "hand_side_for_hamer": self.hand_side_for_hamer,
            "confidence": float(self.confidence) if self.confidence is not None else None,
        }


class HandBBoxDetector:
    """MediaPipe-based hand bounding-box detector."""

    def __init__(
        self,
        flip_handedness: bool = True,
        static_image_mode: bool = True,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.3,
        min_tracking_confidence: float = 0.3,
    ):
        self.flip_handedness = flip_handedness
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self._hands = mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )

    def predict(self, image_path: str) -> tuple[list[HandBbox], np.ndarray]:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Unable to load image: {image_path}")

        height, width = image.shape[:2]
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self._hands.process(image_rgb)

        bboxes: list[HandBbox] = []
        debug_image = image.copy()

        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                pixel_points = []
                for lm in hand_landmarks.landmark:
                    x_px = int(round(lm.x * width))
                    y_px = int(round(lm.y * height))
                    x_px = max(0, min(width - 1, x_px))
                    y_px = max(0, min(height - 1, y_px))
                    pixel_points.append((x_px, y_px))

                xs = [p[0] for p in pixel_points]
                ys = [p[1] for p in pixel_points]
                if not xs or not ys:
                    continue

                x_min = min(xs)
                x_max = max(xs)
                y_min = min(ys)
                y_max = max(ys)

                box_width = x_max - x_min
                box_height = y_max - y_min
                x_min = int(max(0, round(x_min - 0.1 * box_width)))
                x_max = int(min(width - 1, round(x_max + 0.1 * box_width)))
                y_min = int(max(0, round(y_min - 0.1 * box_height)))
                y_max = int(min(height - 1, round(y_max + 0.1 * box_height)))

                raw_handedness = None
                confidence = None
                if results.multi_handedness and len(results.multi_handedness) > hand_idx:
                    classification = results.multi_handedness[hand_idx].classification
                    if classification:
                        raw_handedness = _normalize_handedness(classification[0].label)
                        confidence = classification[0].score

                handedness = _flip_handedness(raw_handedness, self.flip_handedness)
                hand_side_for_hamer = _hand_side_for_hamer(handedness)

                bboxes.append(
                    HandBbox(
                        x1=x_min,
                        y1=y_min,
                        x2=x_max,
                        y2=y_max,
                        raw_handedness=raw_handedness,
                        handedness=handedness,
                        hand_side_for_hamer=hand_side_for_hamer,
                        confidence=confidence,
                    )
                )

                mp_drawing.draw_landmarks(
                    debug_image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2),
                )
                cv2.rectangle(debug_image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

                corrected_label = handedness if handedness is not None else "unknown"
                raw_label = raw_handedness if raw_handedness is not None else "unknown"
                cv2.putText(
                    debug_image,
                    f"Corrected: {corrected_label}",
                    (x_min, max(y_min - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    debug_image,
                    f"Raw: {raw_label}",
                    (x_min, max(y_min - 30, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 200, 200),
                    1,
                    cv2.LINE_AA,
                )

        return bboxes, debug_image

    def close(self) -> None:
        if self._hands is not None:
            self._hands.close()
            self._hands = None

    def __enter__(self) -> "HandBBoxDetector":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def save_hand_bboxes(
    image_path: str,
    image_width: int,
    image_height: int,
    flip_handedness: bool,
    bboxes: list[HandBbox],
    json_path: str,
) -> None:
    output = {
        "image_path": image_path,
        "image_width": image_width,
        "image_height": image_height,
        "flip_handedness": flip_handedness,
        "hands": [bbox.to_dict() for bbox in bboxes],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

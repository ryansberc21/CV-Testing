# Ryan Bercich
# University of St. Thomas - SCALE Microelectronics
# 20 July 2026
# chip_shift.py

# Measure a chip's vertical shift relative to a known-good reference image.

from __future__ import annotations # for Python 3.9 compatibility

import argparse
from pathlib import Path

import cv2 as cv
import numpy as np

"""
def arguments()
returns an argparse.Namespace
This function sets up the command-line argument parser and returns the parsed arguments.
i.e. python chip_shift.py image.jpg --reference reference.jpg --roi 130 0 40 190 --mm-per-pixel 0.1 --output annotated.jpg
"""
def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="image containing the chip")
    parser.add_argument(
        "--reference", type=Path, required=True,
        help="image of the chip in the desired (zero-shift) position",
    )
    parser.add_argument("--roi", nargs=4, type=int, metavar=("X", "Y", "W", "H"),
                        # Default values are chosen to cover the chip area in a typical image; adjust as needed.
                        default=(130, 0, 40, 190),
                        help="chip search region; default: 130 0 40 190")
    parser.add_argument("--mm-per-pixel", type=float,
                        help="optional vertical calibration")
    parser.add_argument("--output", type=Path,
                        help="save an annotated copy of the measured image")
    return parser.parse_args()


def contiguous_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    padded = np.pad(mask.astype(np.int8), (1, 1))
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1) - 1
    return list(zip(starts.tolist(), ends.tolist()))


def detect_chip(image: np.ndarray, roi: tuple[int, int, int, int]):
    x, y, width, height = roi
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    crop = gray[y:y + height, x:x + width]
    if crop.size == 0 or crop.shape != (height, width):
        raise ValueError(f"ROI {roi} lies outside the {gray.shape[1]}x{gray.shape[0]} image")

    crop = cv.GaussianBlur(crop, (5, 5), 0)
    threshold, dark = cv.threshold(
        crop, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU
    )
    dark = cv.morphologyEx(
        dark, cv.MORPH_CLOSE, cv.getStructuringElement(cv.MORPH_RECT, (5, 7))
    )

    # A chip crosses most of this narrow ROI; background clutter usually does not.
    occupied_rows = np.mean(dark > 0, axis=1) >= 0.60
    runs = [(start, end) for start, end in contiguous_runs(occupied_rows)
            if end - start + 1 >= 18]
    if not runs:
        raise RuntimeError("No chip found. Adjust --roi so it crosses the chip body.")

    start, end = max(runs, key=lambda run: run[1] - run[0])
    top, bottom = y + start, y + end
    center_y = (top + bottom) / 2.0
    confidence = float(np.mean(dark[start:end + 1] > 0))
    return center_y, (x, top, width, bottom - top + 1), threshold, confidence


def load(path: Path) -> np.ndarray:
    image = cv.imread(str(path))
    if image is None:
        raise SystemExit(f"Could not read image: {path}")
    return image


def label_panel(image: np.ndarray, label: str) -> None:
    cv.rectangle(image, (0, 0), (image.shape[1], 30), (0, 0, 0), -1)
    cv.putText(image, label, (8, 21), cv.FONT_HERSHEY_SIMPLEX,
               0.55, (255, 255, 255), 1, cv.LINE_AA)


def comparison_image(reference: np.ndarray, image: np.ndarray,
                     roi: tuple[int, int, int, int], reference_center: float,
                     center: float, box: tuple[int, int, int, int],
                     shift_px: float, direction: str) -> np.ndarray:
    if reference.shape != image.shape:
        raise ValueError("Reference and measured images must have the same dimensions")

    ref_panel = reference.copy()
    measured_panel = image.copy()
    difference = cv.absdiff(image, reference)
    difference = cv.applyColorMap(
        cv.cvtColor(difference, cv.COLOR_BGR2GRAY), cv.COLORMAP_TURBO
    )
    x, top, width, height = box
    roi_x, roi_y, roi_w, roi_h = roi
    ref_y, measured_y = round(reference_center), round(center)
    yellow, green = (0, 220, 255), (80, 255, 80)

    for panel in (ref_panel, measured_panel, difference):
        cv.rectangle(panel, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h),
                     (255, 180, 0), 1)
        cv.line(panel, (0, ref_y), (panel.shape[1] - 1, ref_y), yellow, 1)
    cv.rectangle(measured_panel, (x, top), (x + width, top + height), green, 2)
    cv.line(measured_panel, (0, measured_y),
            (measured_panel.shape[1] - 1, measured_y), green, 1)
    arrow_x = min(x + width + 16, measured_panel.shape[1] - 10)
    cv.arrowedLine(measured_panel, (arrow_x, ref_y), (arrow_x, measured_y),
                   (255, 255, 255), 2, tipLength=0.18)

    label_panel(ref_panel, "REFERENCE / desired position")
    label_panel(measured_panel, f"MEASURED / {abs(shift_px):.1f} px {direction}")
    label_panel(difference, "ABSOLUTE PIXEL DIFFERENCE")
    return np.hstack((ref_panel, measured_panel, difference))


def main() -> None:
    args = arguments()
    roi = tuple(args.roi)
    image = load(args.image)
    reference = load(args.reference)
    center, box, threshold, confidence = detect_chip(image, roi)
    reference_center, _, _, reference_confidence = detect_chip(reference, roi)

    # Image y increases downward, so positive means physically lower in the image.
    shift_px = center - reference_center
    direction = "down" if shift_px > 0 else "up" if shift_px < 0 else "centered"
    print(f"chip center:      y={center:.1f} px")
    print(f"reference center: y={reference_center:.1f} px")
    print(f"vertical shift:   {abs(shift_px):.1f} px {direction}")
    if args.mm_per_pixel is not None:
        shift_mm = abs(shift_px * args.mm_per_pixel)
        correction = "up" if direction == "down" else "down" if direction == "up" else "none"
        print(f"vertical shift:   {shift_mm:.3f} mm {direction}")
        print(f"robot correction: {shift_mm:.3f} mm {correction}")
    print(f"detection confidence: {confidence:.0%} "
          f"(reference {reference_confidence:.0%}, threshold {threshold:.0f})")

    if args.output:
        visualization = comparison_image(
            reference, image, roi, reference_center, center, box, shift_px, direction
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not cv.imwrite(str(args.output), visualization):
            raise SystemExit(f"Could not write output: {args.output}")
        print(f"annotated image:  {args.output}")


if __name__ == "__main__":
    main()

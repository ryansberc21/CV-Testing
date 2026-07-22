"""Interactive image viewer for exploring pixel-to-robot coordinate math.

Left-click a robot/tool reference point, then the chip center.  The overlay shows
the displacement in image pixels and, if a scale is supplied, in millimetres.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2 as cv


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=Path("Images"))
    parser.add_argument("--scale", type=int, default=3, help="display enlargement")
    parser.add_argument(
        "--mm-per-pixel-x", type=float, help="horizontal calibration scale"
    )
    parser.add_argument(
        "--mm-per-pixel-y", type=float, help="vertical calibration scale"
    )
    parser.add_argument(
        "--keep-image-y",
        action="store_true",
        help="make robot +Y point down like image +v (default robot +Y is up)",
    )
    return parser.parse_args()


class Viewer:
    def __init__(self, paths: list[Path], args: argparse.Namespace) -> None:
        self.paths = paths
        self.args = args
        self.index = 0
        self.points: list[tuple[int, int]] = []
        self.window = "Chip images | A/D: image  click: reference, chip  R: reset  Q: quit"

    def mouse(self, event: int, x: int, y: int, _flags: int, _data: object) -> None:
        if event == cv.EVENT_RBUTTONDOWN:
            self.points.clear()
        elif event == cv.EVENT_LBUTTONDOWN:
            point = (x // self.args.scale, y // self.args.scale)
            if len(self.points) == 2:
                self.points.clear()
            self.points.append(point)

    def draw(self):
        image = cv.imread(str(self.paths[self.index]))
        if image is None:
            raise RuntimeError(f"Could not read {self.paths[self.index]}")

        canvas = cv.resize(
            image, None, fx=self.args.scale, fy=self.args.scale,
            interpolation=cv.INTER_NEAREST,
        )
        s = self.args.scale
        cv.putText(canvas, self.paths[self.index].name, (12, 28),
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)

        colors = [(0, 220, 255), (80, 255, 80)]
        labels = ["robot reference", "chip center"]
        for i, (u, v) in enumerate(self.points):
            p = (u * s, v * s)
            cv.drawMarker(canvas, p, colors[i], cv.MARKER_CROSS, 22, 2)
            cv.putText(canvas, f"{labels[i]} ({u}, {v})", (p[0] + 8, p[1] - 8),
                       cv.FONT_HERSHEY_SIMPLEX, 0.52, colors[i], 1, cv.LINE_AA)

        if len(self.points) == 2:
            (u0, v0), (u1, v1) = self.points
            du, dv = u1 - u0, v1 - v0
            dy_sign = 1 if self.args.keep_image_y else -1
            cv.arrowedLine(canvas, (u0 * s, v0 * s), (u1 * s, v1 * s),
                           (255, 180, 0), 2, tipLength=0.08)
            lines = [f"pixel offset: du={du:+d}, dv={dv:+d}"]
            if self.args.mm_per_pixel_x is not None:
                sy = (self.args.mm_per_pixel_y
                      if self.args.mm_per_pixel_y is not None
                      else self.args.mm_per_pixel_x)
                dx_mm = du * self.args.mm_per_pixel_x
                dy_mm = dy_sign * dv * sy
                lines.append(f"robot offset: X={dx_mm:+.2f} mm, Y={dy_mm:+.2f} mm")
            else:
                lines.append("add --mm-per-pixel-x SCALE to convert to mm")
            for row, text in enumerate(lines):
                cv.putText(canvas, text, (12, canvas.shape[0] - 42 + row * 24),
                           cv.FONT_HERSHEY_SIMPLEX, 0.56, (255, 255, 255), 2, cv.LINE_AA)
        return canvas

    def run(self) -> None:
        cv.namedWindow(self.window, cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback(self.window, self.mouse)
        while True:
            cv.imshow(self.window, self.draw())
            key = cv.waitKey(30) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("d"), 83):
                self.index = (self.index + 1) % len(self.paths)
                self.points.clear()
            elif key in (ord("a"), 81):
                self.index = (self.index - 1) % len(self.paths)
                self.points.clear()
            elif key == ord("r"):
                self.points.clear()
        cv.destroyAllWindows()


def main() -> None:
    args = parse_args()
    paths = sorted(
        path for path in args.folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not paths:
        raise SystemExit(f"No images found in {args.folder.resolve()}")
    if args.scale < 1:
        raise SystemExit("--scale must be at least 1")
    Viewer(paths, args).run()


if __name__ == "__main__":
    main()

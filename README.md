# CV-Testing

Small OpenCV experiments for locating a chip relative to a robot gripper.

## Browse the captures and measure pixels

Run:

```powershell
python image_viewer.py
```

Use `A`/`D` (or the left/right arrows) to move through the files in `Images`.
Left-click the robot/tool reference point and then the chip center. The viewer
draws the vector and reports `(du, dv)` in pixels. Right-click or press `R` to
clear the points; press `Q` or Escape to quit.

After measuring a calibration target on the same camera plane, pass its scale:

```powershell
python image_viewer.py --mm-per-pixel-x 0.125
```

For non-square pixels/scales, also pass `--mm-per-pixel-y`. Image coordinates
start at the upper-left (`+u` right, `+v` down), while the viewer assumes robot
`+X` right and `+Y` up. Use `--keep-image-y` if the robot's `+Y` points down.

The displayed conversion is:

```text
X_mm = (u_chip - u_reference) * mm_per_pixel_x
Y_mm = -(v_chip - v_reference) * mm_per_pixel_y
```

This scale model is useful when the chip and calibration target lie on a plane
parallel to the camera. For an angled camera or motion across a larger work
area, calibrate a planar homography from at least four known pixel/robot point
pairs instead of using one constant scale.

## Measure up/down chip shift automatically

Choose one close-up image in which the chip is positioned correctly. Use that
as the zero reference when measuring another capture:

```powershell
python chip_shift.py Images/closeup_low.png `
  --reference Images/closeup_chip.png `
  --output measured.png
```

The result reports the chip centers and a signed direction in pixels. Add a
scale measured at the chip plane to get a robot correction in millimetres:

```powershell
python chip_shift.py Images/closeup_low.png `
  --reference Images/closeup_chip.png --mm-per-pixel 0.125
```

The default search strip is `x=130..169, y=0..189`, tuned to the included
320x240 close-up captures. If the camera moves, select a strip that crosses the
middle of the chip body with `--roi X Y WIDTH HEIGHT`. Keeping the camera,
gripper, exposure, and chip plane fixed is important for repeatable numbers.

When `--output` is provided, the saved visual aid has three panels: the desired
reference position, the measured position with a shift arrow, and a colorized
absolute pixel difference. Yellow marks the desired center and green marks the
detected chip center.

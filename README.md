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

# CV-Testing

Small OpenCV experiments for locating a chip relative to a robot gripper.

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

# Robotic Arm — CAD and Drawing Set

Fusion 360 model and drawing set for a articulated pick-and-place robotic arm.

| | |
|---|---|
| Model | `robotic arm.f3d` (Fusion 360 archive) |
| Drawing | 11 sheets, sheet 1 assembly with balloons + parts list |
| Author | Alexander Odey |
| Date | 31/08/2026 |
| Units | mm, g |
| Material | Steel throughout |

---

## What is actually modelled

Ten component instances, nine of which reach the parts list:

| Item | Component | Notes |
|---|---|---|
| 1 | Base | |
| 2 | Jaw | shoulder casting |
| 3 | Jaw_2 | |
| 4 | Jaw_3 | |
| 5 | Jaw_4 | |
| 6 | Jaw_5 | |
| 7 | Jaw_6 | |
| 8 | Jaw_6 (1) | |
| — | Jaw_6 (1) (1) | **hidden in the browser, missing from the parts list** |
| 10 | Jaw_6 (1)(Mirror) | opposing gripper finger |

### Measured dimensions, from the drawing sheets

| Quantity | Value |
|---|---|
| Overall height | 826.69 mm / 826.78 mm (two views) |
| Reach, retracted pose | 656.27 mm |
| Reach, extended pose | 857.5 mm |
| Base outer diameter | Ø220 mm |
| Base bolt circle | Ø180 mm |
| Base spigot | Ø198.55 mm |
| Shoulder flange | Ø94.8 mm |
| Gripper finger length | ~129 mm |
| Gripper pivot holes | Ø3.5, Ø3 mm |

Joint angles in the saved pose: -89°, 1°, -58°, -43°, 58°. All joints are
revolute, so with base rotation this is a **six-axis arm**, not three.

---

## Three sets of numbers that do not agree

Worth resolving before any of this goes in a report, because a marker who
follows a figure from one document to another will land on a contradiction.

**1. The reference paper** (`dofijte.pdf`) is Jadhav et al., *3-DOF Pick and
Place Robotic Arm*, ISTE Vol 47, Aug 2024. It is **someone else's published
work**, useful as a citation, not as a description of this model. Its arm is:

- 3 revolute joints, DH parameters 0.390 m offset, 0.240 m and 0.235 m links
- ~475 mm reach
- NEMA-class steppers, 20 kg·cm and 4.6 N·m holding torque, Arduino UNO

**2. The logbook plan** (`Pick-and-Place Arm Logbook.html`) assumes:

- 2 links, L1 = 250 mm, L2 = 150 mm, 400 mm reach
- 0.5 kg payload, aluminium flat plates, ~5.0 N·m shoulder torque
- NEMA 17 with a 20:1 gearbox

**3. This CAD model** is neither: roughly 830 mm tall with 857 mm of reach, six
axes, and steel throughout. Steel at that scale is far heavier than the
logbook's aluminium plates, so every torque and motor figure in the logbook is
wrong for this machine — almost certainly by an order of magnitude.

Pick one machine and make the other two documents follow it. The CAD is the
most defensible choice, since it is the thing that actually exists.

---

## Known issues in the drawing set

- **Parts list skips item 9.** It runs 1–8 then 10. `Jaw_6 (1) (1)` is
  unchecked in the browser, so it is excluded from the list while its balloon
  numbering still consumes a slot. Either show the component or renumber.
- **Sheet 1 balloon 1** points into empty space near the bottom right rather
  than at the Base.
- **Overlapping dimension text** on several sheets, e.g. `129.04`/`129.89` and
  `R4`/`Ø180` printing on top of each other. Auto-dimension placed them; they
  need dragging clear.
- **Duplicated overall dimension**, 306.51 mm appears twice on the Jaw sheet.

---

## What cannot be read from the `.f3d` here

The archive is a zip, but the geometry sits in compressed proprietary BREP
blobs and the metadata stream is binary. Component names, materials and mass
properties are **not** extractable outside Fusion.

So the numbers that matter most for the engineering calculations — mass, centre
of mass and moment of inertia per link — have to come out of Fusion by hand:

    select a component -> Properties -> Physical
    or: Inspect -> Section Analysis / Center of Mass

Recording them in a table here would let the torque and motor sizing rest on
the real model rather than on an assumed one.

---

## Files

```
robotic arm.f3d                     Fusion archive, the source of truth
dofijte.pdf                         reference paper (Jadhav et al.) — citation only
Assets/                             11 screenshots of the model and drawings
Pick-and-Place Arm Logbook.html     week 14-18 logbook plan (numbers need reconciling)
```

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

## Two machines, kept separate on purpose

Three different arms appear in this folder. Mixing their figures is the easiest
way to produce a report that contradicts itself, so the scoping is fixed:

**The arm** — this CAD model — is the mechanical design. Six revolute axes,
857.5 mm reach, ~830 mm tall, steel. Every dimension, mass and motor figure in
the report describes it.

**The worked example** is a two-link planar arm, L1 = 250 mm and L2 = 150 mm,
used in week 15 of the logbook and in `sim/` only. Six-axis inverse kinematics
is not a week's hand derivation, so the method is developed on a case small
enough to solve on paper and check in code, then applied to the real arm's DH
table. Its 400 mm reach and 0.5 kg payload describe nothing physical, and it is
fenced wherever it appears.

**The reference paper** (`dofijte.pdf`) is Jadhav et al., *3-DOF Pick and Place
Robotic Arm*, ISTE Vol 47, Aug 2024 — a 3-DOF arm with 240/235 mm links and
~475 mm reach. It is **someone else's published work**. Cite it for method; take
no numbers from it.

The trap to avoid: the logbook originally sized a NEMA 17 with a 20:1 gearbox at
about 5.0 N·m. That belongs to the 400 mm aluminium example. A steel arm at
857 mm needs far more, and the real figure only comes out once the mass table
below is filled from Fusion.

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

## Mass properties and the shoulder torque

Read from Fusion, Properties → Physical. Every component reports 7.85 g/cm³, so
steel is genuinely applied throughout.

| Component | Mass (kg) |
|---|---|
| Jaw (shoulder) | 18.908 |
| Jaw_2 | 7.904 |
| Jaw_3 | 11.365 |
| Jaw_4 | 4.842 |
| Jaw_5 | 2.682 |
| Jaw_6 | 0.600 |
| gripper fingers, 2 off | 0.277 each |
| **above the shoulder** | **46.855** |

**The shoulder torque is quoted as an upper bound, not a measurement.** The arm
was never posed straight out, and a centre of mass moves with the pose, so the
exact worst case is not available. Instead every gram is placed at full reach,
which can only overstate the moment:

    (46.855 + 2 payload) × 9.81 × 0.8575 = 411 N·m
    × safety factor 2                    = 822 N·m

This is rigorous rather than approximate — a drive meeting the bound meets the
real requirement whatever the true figure is — but it is pessimistic. The heavy
links sit near the shoulder and only the 0.28 kg fingers reach the end, so the
true value is likely well under half. Sizing against it buys a heavier drive
than strictly needed, which is a deliberate trade. **It must be reported as a
bound.**

At the shoulder that means roughly 82:1 off a 10 N·m industrial servo, or 274:1
through a harmonic drive off a 3 N·m one.

Separately, and exactly: the arm balances 370.6 mm horizontally from the column
at 373.8 mm up, giving a 170.4 N·m overturning moment for the base fixing. That
one needs no pose assumption.

To replace the bound with the exact figure later, pose the arm straight out and
horizontal, re-read every Center of Mass into `com_extended` in `sim/torque.py`,
set `SHOULDER_X_MM`, and run `python -m sim.torque --exact`.

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
docs/logbook.html                   week 14-18 logbook, scoped to this arm
sim/                                analysis scripts — see sim/README.md
tests/                              32 tests for the kinematics
outputs/figures/                    generated plots
```

## Running the analysis

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m sim.workspace
.venv/bin/python -m pytest tests/
```

`sim/torque.py` deliberately refuses to produce a number until the mass table
above is filled from Fusion. See `sim/README.md` for why.

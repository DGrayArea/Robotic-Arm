# sim — analysis scripts

Five short modules. None of them talks to Fusion; the CAD is opened by hand and
its numbers typed in.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python -m sim.arm          # kinematics self-check, no plot
.venv/bin/python -m sim.workspace    # -> outputs/figures/workspace.png
.venv/bin/python -m sim.trajectory   # -> outputs/figures/trajectory.png
.venv/bin/python -m sim.pid          # -> outputs/figures/pid_step_response.png
.venv/bin/python -m sim.torque       # refuses until the mass table is filled
.venv/bin/python -m pytest tests/    # 32 tests
```

## Which arm each module is about

This is the distinction that keeps the report honest, so it is worth stating
before touching anything.

| Module | Arm | Why |
|---|---|---|
| `arm.py` | **worked example**, 2 links, 400 mm | six-axis IK is not a week's hand derivation |
| `workspace.py` | **worked example** | plots what `arm.py` produces |
| `trajectory.py` | either | a trapezoidal profile's *shape* does not depend on scale |
| `pid.py` | either | second-order step response, same reason |
| `torque.py` | **the CAD model**, 857.5 mm, steel | the only module carrying real figures |

`workspace.png` is stamped **WORKED EXAMPLE** in the figure itself, because a
plot pasted into a report loses whatever caption sat next to it.

## `torque.py` refuses to run, on purpose

The mass table in it is empty and `shoulder_torque()` raises instead of
returning a number.

Mass, centre of mass and inertia live inside Fusion's proprietary geometry.
Nothing outside Fusion can read them out of the `.f3d`, so the only honest
source is Fusion itself:

    select the component -> Properties -> Physical
    read Mass, and Center of Mass relative to the joint below it

A placeholder that quietly produced "about 5 N·m" would be worse than an error,
because the motor selection downstream would look reasonable and be wrong by an
order of magnitude. Running `--demo` shows the output shape on visibly fake
masses, everything stamped `PLACEHOLDER`.

Even on those conservative fake numbers the shoulder needs roughly **300 N·m**
of design torque, which would want a **755:1** reduction off a 0.4 N·m motor.
That is the number that killed the old logbook's NEMA 17 and 20:1 gearbox: they
belonged to the 400 mm aluminium example, not to a steel arm reaching 857.5 mm.

## What the tests actually protect

`tests/test_arm.py` is mostly one idea. A sign error in θ₁ still returns
plausible angles, and a plot of them still looks like an arm — it only shows up
when you drive the angles forward, invert the result, and land somewhere else.
So the round trip is tested across a grid of poses, both elbow branches are
checked to reach the same point, and unreachable targets must raise rather than
clip. Silently snapping an unreachable target to the nearest reachable one is
how a machine ends up moving somewhere nobody asked it to.

The singularity tests assert the real relationship rather than a threshold
someone picked: `det(J) = L1·L2·sin θ₂`, so the falloff approaching full
extension is exactly the sine ratio.

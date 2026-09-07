"""
Joint torque for the REAL arm, from the CAD mass properties.

This module is about `robotic arm.f3d`, not the worked example in `arm.py`.

The mass table below is empty, and that is deliberate. Mass, centre of mass and
inertia live inside Fusion's proprietary geometry and cannot be read out of the
.f3d by any tool here, so the only honest source is Fusion itself:

    select a component -> Properties -> Physical
    read the Mass row, and the X of the Center of Mass row, in WORLD
    coordinates, with the arm posed straight out and horizontal

Set SHOULDER_X_MM the same way, once, from the shoulder joint. Every moment arm
is then computed rather than measured by hand.

Until those are filled in, `shoulder_torque()` raises rather than returning a
number. That is the point. A steel arm reaching 857.5 mm needs vastly more
torque than the 400 mm aluminium worked example, and a placeholder that quietly
produced "about 5 N.m" would send the motor selection to a drive an order of
magnitude too small, with nothing on screen to suggest anything was wrong.

There is a `--demo` mode that runs the arithmetic on visibly fake masses, so you
can see the shape of the output before you have the real ones. Everything it
prints is stamped PLACEHOLDER and none of it belongs in a report.

Run it:
    python -m sim.torque           # refuses, and tells you what to fill in
    python -m sim.torque --demo    # fake masses, clearly labelled
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

G = 9.81           # m/s^2
SAFETY_FACTOR = 2.0  # friction, assembly tolerance, and a margin on the estimate

# Worst case for any joint: the arm straight out and horizontal, so every mass
# above it sits at its maximum moment arm at once.
REACH_EXTENDED_MM = 857.5


# World X of the shoulder rotation axis, with the arm in the extended pose.
# Read it once from Fusion the same way as any centre of mass, then every
# moment arm below is computed rather than measured by hand.
SHOULDER_X_MM: float | None = None


@dataclass
class Link:
    """
    One component, exactly as Fusion reports it.

    Both fields come straight off Properties -> Physical, so nothing has to be
    worked out on paper:

        mass_kg   : the Mass row
        com_x_mm  : the X of the Center of Mass row, in WORLD coordinates,
                    with the arm posed straight out and horizontal

    The moment arm is com_x_mm - SHOULDER_X_MM, computed in `moment_arm_mm()`.
    Asking for a distance instead would mean doing that subtraction by hand for
    seven parts, which is seven chances to get a sign or a datum wrong.
    """
    name: str
    mass_kg: float | None = None
    com_x_mm: float | None = None

    def moment_arm_mm(self) -> float:
        if SHOULDER_X_MM is None:
            raise UnfilledMassTable("SHOULDER_X_MM is not set.")
        return self.com_x_mm - SHOULDER_X_MM


# Filled from Fusion. Names match the browser tree in the .f3d.
# Mass is pose-independent, so it can be read in whatever pose the model happens
# to be in. com_x_mm cannot: it has to be read with the arm straight out and
# horizontal, because that is the pose the worst-case moment arm is defined in.
# The two columns therefore get filled on separate passes.
LINKS: list[Link] = [
    # Fusion: 18907.772 g at 7.849 g/cm^3, so steel really is applied.
    Link("Jaw (shoulder)", mass_kg=18.908),
    Link("Jaw_2"),
    Link("Jaw_3"),
    Link("Jaw_4"),
    Link("Jaw_5"),
    Link("Jaw_6"),
    Link("Jaw_6 (1) + Mirror (gripper)"),
]

# Base is excluded on purpose: it sits below the shoulder axis, so it applies no
# moment about it. It matters for the floor-fixing calculation, not this one.


class UnfilledMassTable(RuntimeError):
    """Raised rather than guessing. See the module docstring."""


def _demo_table() -> list[Link]:
    """
    Visibly fake masses, for seeing the output shape only.

    Deliberately round numbers so nobody mistakes them for measurements.
    """
    return [
        Link("Jaw (shoulder)", 12.0, 120.0),
        Link("Jaw_2", 9.0, 260.0),
        Link("Jaw_3", 7.0, 400.0),
        Link("Jaw_4", 4.0, 560.0),
        Link("Jaw_5", 3.0, 680.0),
        Link("Jaw_6", 2.0, 780.0),
        Link("Jaw_6 (1) + Mirror (gripper)", 1.5, 840.0),
    ]


def shoulder_torque(
    payload_kg: float,
    links: list[Link] | None = None,
    safety_factor: float = SAFETY_FACTOR,
) -> dict:
    """
    Static holding torque at the shoulder, arm extended horizontally.

        T = sum( m_i * g * r_i ) * SF

    Every link above the joint contributes its own weight at its own centre of
    mass, so the sum runs outward from the joint to the tool. This is the one
    number the whole drive selection rests on.
    """
    links = links if links is not None else LINKS

    no_mass = [l.name for l in links if l.mass_kg is None]
    no_com = [l.name for l in links if l.com_x_mm is None]
    if no_mass or no_com or SHOULDER_X_MM is None:
        parts = ["Mass table is not filled in, so there is no torque to report.\n"]
        if no_mass:
            parts.append(
                "\n  Missing MASS. Read in any pose, it does not depend on one:\n"
                + "".join(f"    - {n}\n" for n in no_mass))
        pending = list(no_com)
        if SHOULDER_X_MM is None:
            pending.append("SHOULDER_X_MM (the shoulder joint itself)")
        if pending:
            parts.append(
                "\n  Missing CENTRE OF MASS. Pose the arm straight out and\n"
                "  horizontal FIRST: the worst case is defined in that pose, and\n"
                "  a folded pose gives a smaller, wrong answer.\n"
                + "".join(f"    - {n}\n" for n in pending))
        parts.append(
            "\n  Both come from Properties -> Physical, in WORLD coordinates.\n"
            "  Output format meanwhile: python -m sim.torque --demo\n")
        raise UnfilledMassTable("".join(parts))

    rows = []
    total = 0.0
    for link in links:
        arm_mm = link.moment_arm_mm()
        moment = link.mass_kg * G * (arm_mm / 1000.0)
        total += moment
        rows.append((link.name, link.mass_kg, arm_mm, moment))

    payload_moment = payload_kg * G * (REACH_EXTENDED_MM / 1000.0)
    total += payload_moment
    rows.append(("payload", payload_kg, REACH_EXTENDED_MM, payload_moment))

    return {
        "rows": rows,
        "static_nm": total,
        "design_nm": total * safety_factor,
        "safety_factor": safety_factor,
    }


def gear_ratio_for(design_nm: float, motor_nm: float) -> float:
    """
    Ratio needed to get `design_nm` out of a motor rated `motor_nm`.

    Remember the cost: a gearbox multiplies torque and divides speed in the same
    ratio. Pick one big enough for a steel arm and the cycle time is what pays
    for it, which is the check in week 17 of the logbook.
    """
    return design_nm / motor_nm


def _report(payload_kg: float, links: list[Link], placeholder: bool) -> None:
    result = shoulder_torque(payload_kg, links)

    if placeholder:
        print("=" * 68)
        print("  PLACEHOLDER MASSES - NOT MEASUREMENTS - NOT FOR THE REPORT")
        print("=" * 68)

    print(f"\n  Shoulder torque, arm extended horizontally at "
          f"{REACH_EXTENDED_MM:.1f} mm\n")
    print(f"  {'component':<32}{'mass kg':>9}{'r mm':>9}{'N.m':>10}")
    print("  " + "-" * 60)
    for name, mass, com, moment in result["rows"]:
        print(f"  {name:<32}{mass:>9.2f}{com:>9.1f}{moment:>10.2f}")
    print("  " + "-" * 60)
    print(f"  {'static total':<32}{'':>9}{'':>9}{result['static_nm']:>10.2f}")
    print(f"  {'x safety factor ' + str(result['safety_factor']):<32}"
          f"{'':>9}{'':>9}{result['design_nm']:>10.2f}")

    print(f"\n  Gear ratio needed, by motor rating:")
    for motor_nm in (0.4, 1.0, 3.0, 10.0):
        ratio = gear_ratio_for(result["design_nm"], motor_nm)
        print(f"    {motor_nm:>5.1f} N.m motor  ->  {ratio:>7.1f}:1")

    if placeholder:
        print("\n  Again: the masses above are invented. Fill LINKS from Fusion.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                        help="run with visibly fake masses to see the output shape")
    parser.add_argument("--payload", type=float, default=2.0,
                        help="payload mass in kg (default 2.0)")
    args = parser.parse_args()

    if args.demo:
        global SHOULDER_X_MM
        SHOULDER_X_MM = 0.0   # fake table is already measured from the joint
        _report(args.payload, _demo_table(), placeholder=True)
        return

    try:
        _report(args.payload, LINKS, placeholder=False)
    except UnfilledMassTable as exc:
        print(f"\n{exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

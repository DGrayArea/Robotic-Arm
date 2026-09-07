"""
Joint torque for the REAL arm, from the CAD mass properties.

This module is about `robotic arm.f3d`, not the worked example in `arm.py`.

The arm was never posed straight out, so the exact worst-case torque is not
available: a centre of mass moves with the pose, and the saved pose is folded.
The design therefore rests on an UPPER BOUND, which needs only the masses:

    put every gram at full reach -> 411 N.m, or 822 N.m with the safety factor

That is rigorous rather than approximate. Placing mass further out than it can
physically go can only overstate the moment, so a drive meeting the bound meets
the real requirement whatever the true figure turns out to be. The cost is that
the bound is pessimistic: the heavy links sit near the shoulder and only the
0.28 kg fingers reach the end, so the true value is likely well under half.
Sizing against it buys a heavier drive than strictly needed, which is a
deliberate and defensible trade, but it has to be reported as a bound and never
as a measurement.

To replace it with the exact figure later: pose the arm straight out and
horizontal, re-read every Center of Mass into `com_extended`, set SHOULDER_X_MM,
and run with --exact.

Run it:
    python -m sim.torque           # the bound, and the base overturning moment
    python -m sim.torque --exact   # worst case; refuses until the pose is read
    python -m sim.torque --demo    # fake masses, to see the output shape
"""

from __future__ import annotations

import argparse
import math
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

        mass_kg      : the Mass row. Pose-independent.
        com_saved    : the Center of Mass row, (x, y, z) in world mm, as read in
                       the SAVED (folded) pose the model was in.
        com_extended : the same row re-read with the arm straight out and
                       horizontal. This is the one the worst case needs.

    Both centres are kept because they answer different questions and are easy
    to confuse. The saved pose gives where the arm balances as it sits, which is
    what the base fixing has to resist. Only the extended pose gives the maximum
    joint torque.
    """
    name: str
    mass_kg: float | None = None
    com_saved: tuple[float, float, float] | None = None
    com_extended: tuple[float, float, float] | None = None


# Filled from Fusion. Names match the browser tree in the .f3d.
# Mass is pose-independent, so it can be read in whatever pose the model happens
# to be in. com_x_mm cannot: it has to be read with the arm straight out and
# horizontal, because that is the pose the worst-case moment arm is defined in.
# The two columns therefore get filled on separate passes.
LINKS: list[Link] = [
    # Mass and centre of mass read from Fusion, Properties -> Physical.
    # Every component reports 7.85 g/cm^3, so steel is genuinely applied
    # throughout and no part was left on a default material.
    #
    # com_saved is the FOLDED pose the model was saved in. It is NOT the pose
    # the worst-case joint torque is defined in, so it must not be used for
    # drive selection. com_extended is still to be read.
    Link("Jaw (shoulder)",           18.908, (-397.590, 165.139,  410.476)),
    Link("Jaw_2",                     7.904, (-251.204, 323.253,  240.363)),
    Link("Jaw_3",                    11.365, (-231.360, 468.502,   81.216)),
    Link("Jaw_4",                     4.842, (-209.608, 737.122,   38.532)),
    Link("Jaw_5",                     2.682, (-159.327, 770.937,   -5.280)),
    Link("Jaw_6",                     0.600, (-119.672, 762.482,  -36.455)),
    Link("Jaw_6 (1) finger",          0.277, ( -77.480, 778.967,  -95.095)),
    Link("Jaw_6 (1)(Mirror) finger",  0.277, ( -63.594, 731.495,  -61.011)),
]

# Jaw_6 (1) (1) is excluded: hidden in the browser and absent from the parts
# list, which is the numbering gap the README flags. Were it included it adds
# 0.277 kg, about 0.6% of the total, so it changes no engineering conclusion --
# the drawing still needs fixing.


def assembly_com(links: list[Link] | None = None) -> dict:
    """
    Centre of mass of the whole arm above the shoulder, in the saved pose.

    Exact, and needs no joint position: it is just the mass-weighted mean of the
    component centres. Useful in its own right, because where the arm balances
    is what the base fixing and the tipping check have to resist.

    Pose-dependent, so this describes the arm as saved and nothing else.
    """
    links = links if links is not None else LINKS
    missing = [l.name for l in links if l.mass_kg is None or l.com_saved is None]
    if missing:
        raise UnfilledMassTable("Missing mass or centre for: " + ", ".join(missing))

    total = sum(l.mass_kg for l in links)
    cx, cy, cz = (
        sum(l.mass_kg * l.com_saved[i] for l in links) / total for i in range(3)
    )
    return {"total_kg": total, "com_mm": (cx, cy, cz)}


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
    no_com = [l.name for l in links if l.com_extended is None]
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
        arm_mm = link.com_extended[0] - SHOULDER_X_MM
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


def upper_bound_torque(payload_kg: float,
                       links: list[Link] | None = None,
                       safety_factor: float = SAFETY_FACTOR) -> dict:
    """
    Strict upper bound on shoulder torque, from masses alone.

    Pretend every gram sits at full reach:

        T_max = ( sum(m_i) + payload ) * g * REACH_EXTENDED

    No centre of mass is needed, and no pose, because putting every mass at the
    furthest point it could possibly occupy can only overstate the moment. The
    true figure is strictly smaller, since the heavy links sit close to the
    shoulder and only the light gripper is out at the end.

    That makes this usable now and safe to size a drive against: a motor that
    meets the bound meets the real requirement. It is not a substitute for the
    exact number, because sizing against a bound that is 2-3x too high buys a
    drive far heavier and more expensive than the arm needs.
    """
    links = links if links is not None else LINKS
    missing = [l.name for l in links if l.mass_kg is None]
    if missing:
        raise UnfilledMassTable(
            "Masses missing for: " + ", ".join(missing))

    arm_kg = sum(l.mass_kg for l in links)
    total_kg = arm_kg + payload_kg
    bound = total_kg * G * (REACH_EXTENDED_MM / 1000.0)
    return {
        "arm_kg": arm_kg,
        "payload_kg": payload_kg,
        "total_kg": total_kg,
        "bound_nm": bound,
        "design_nm": bound * safety_factor,
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
    parser.add_argument("--exact", action="store_true",
                        help="worst-case figure; needs the extended-pose centres")
    parser.add_argument("--demo", action="store_true",
                        help="visibly fake masses, to see the output shape")
    parser.add_argument("--payload", type=float, default=2.0,
                        help="payload mass in kg (default 2.0)")
    args = parser.parse_args()

    if args.demo:
        global SHOULDER_X_MM
        SHOULDER_X_MM = 0.0
        _report(args.payload, _demo_table(), placeholder=True)
        return

    if args.exact:
        try:
            _report(args.payload, LINKS, placeholder=False)
        except UnfilledMassTable as exc:
            print(f"\n{exc}")
            raise SystemExit(1)
        return

    # Default: the bound. The arm was never posed straight out, so the exact
    # worst case cannot be computed, and this is what the design rests on.
    r = upper_bound_torque(args.payload)
    com = assembly_com()
    cx, cy, cz = com["com_mm"]
    horiz = math.hypot(cx, cz)

    print("\n  SHOULDER TORQUE - UPPER BOUND")
    print("  " + "=" * 58)
    print("  Every gram placed at full reach, which can only overstate the")
    print("  moment. The true worst case is lower, but is not computed here:")
    print("  it needs the centres of mass re-read with the arm straight out.")
    print("  Quote this as a bound, never as a measurement.\n")
    print(f"    arm above the shoulder   {r['arm_kg']:>9.3f} kg")
    print(f"    payload                  {r['payload_kg']:>9.3f} kg")
    print(f"    total                    {r['total_kg']:>9.3f} kg")
    print(f"    lever, full reach        {REACH_EXTENDED_MM/1000:>9.4f} m")
    print("    " + "-" * 38)
    print(f"    bound                    {r['bound_nm']:>9.1f} N.m")
    print(f"    x SF {r['safety_factor']}                  "
          f"{r['design_nm']:>9.1f} N.m  <- size against this\n")

    print("  Reduction needed at the shoulder:\n")
    print(f"    {'motor':>10}{'ratio':>12}   {'class of drive':<28}")
    print("    " + "-" * 52)
    for motor_nm, kind in ((1.0, "small servo"),
                           (3.0, "mid servo, harmonic drive"),
                           (10.0, "industrial servo, planetary"),
                           (30.0, "large servo, low reduction")):
        ratio = gear_ratio_for(r["design_nm"], motor_nm)
        print(f"    {motor_nm:>7.1f} N.m{ratio:>10.1f}:1   {kind:<28}")

    print("\n  Where the arm balances, in the SAVED pose (exact, no bound):")
    print(f"    centre of mass   ({cx:.1f}, {cy:.1f}, {cz:.1f}) mm")
    print(f"    {horiz:.1f} mm horizontally from the column, {cy:.1f} mm up")
    print(f"    overturning moment on the base fixing: "
          f"{r['arm_kg'] * G * horiz / 1000:.1f} N.m\n")


if __name__ == "__main__":
    main()

"""
Two-link planar arm: forward and inverse kinematics.

THIS IS THE WORKED EXAMPLE, NOT THE CAD MODEL.

The arm in `robotic arm.f3d` has six revolute axes and 857.5 mm of reach. Its
inverse kinematics is not something you derive by hand in a week, and a
six-axis solver would be a black box you could not defend in a viva.

So the method is developed here on a two-link planar arm, which is small enough
to solve on paper and check against code, and which still carries every idea
that matters: a forward map, an inverse map with two solution branches, a
bounded workspace, and a singularity at full extension. Week 15 Friday of the
logbook applies the same method to the real arm's DH table.

The numbers below describe nothing physical. L1 = 250 mm and L2 = 150 mm were
chosen because they make the annulus obvious, not because anything is that size.

Run it:
    python -m sim.arm          # self-check, no plot
"""

from __future__ import annotations

import math

import numpy as np

# Worked-example link lengths, in mm. Not the CAD model's.
L1 = 250.0
L2 = 150.0

# The reachable annulus falls straight out of the two link lengths.
REACH_MAX = L1 + L2          # 400 mm, both links straight
REACH_MIN = abs(L1 - L2)     # 100 mm, folded back on itself


def forward(theta1: float, theta2: float) -> tuple[float, float]:
    """
    Joint angles (radians) -> tool position (mm).

    theta2 is measured from the extension of link 1, not from horizontal. That
    convention is the commonest source of sign errors in this derivation, which
    is why `round_trip_error` below exists.
    """
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2)
    return float(x), float(y)


def inverse(x: float, y: float, elbow_up: bool = True) -> tuple[float, float]:
    """
    Tool position (mm) -> joint angles (radians), by the cosine rule.

    Two solutions reach the same point, elbow-up and elbow-down; the sign of
    theta2 picks between them. Elbow-up is the default because it keeps the
    forearm clear of the conveyor guard.

    Raises ValueError outside the annulus rather than returning a clipped angle,
    because silently snapping an unreachable target to the nearest reachable one
    is how a robot ends up moving somewhere nobody asked it to go.
    """
    r = math.hypot(x, y)
    if not (REACH_MIN - 1e-9 <= r <= REACH_MAX + 1e-9):
        raise ValueError(
            f"({x:.1f}, {y:.1f}) is {r:.1f} mm from the base, outside the "
            f"reachable annulus {REACH_MIN:.0f}-{REACH_MAX:.0f} mm"
        )

    cos_t2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    theta2 = math.acos(float(np.clip(cos_t2, -1.0, 1.0)))
    if not elbow_up:
        theta2 = -theta2

    theta1 = math.atan2(y, x) - math.atan2(
        L2 * math.sin(theta2), L1 + L2 * math.cos(theta2)
    )
    return theta1, theta2


def round_trip_error(theta1: float, theta2: float, elbow_up: bool = True) -> float:
    """
    Drive angles through forward then inverse and report how far the recovered
    position drifts, in mm.

    This is the test that catches a sign error. A wrong sign on theta1 still
    produces plausible-looking angles; it only shows up when you go round the
    loop and land somewhere else.
    """
    x, y = forward(theta1, theta2)
    t1_back, t2_back = inverse(x, y, elbow_up=elbow_up)
    x_back, y_back = forward(t1_back, t2_back)
    return math.hypot(x - x_back, y - y_back)


def jacobian_determinant(theta2: float) -> float:
    """
    det(J) for this arm reduces to L1*L2*sin(theta2).

    It goes to zero at theta2 = 0 (fully extended) and theta2 = pi (fully
    folded). Near there the arm loses a degree of freedom: a small tool
    movement demands a very large joint speed, which no real motor can supply.
    Hence the software limit in the logbook.
    """
    return L1 * L2 * math.sin(theta2)


def _self_check() -> None:
    print(__doc__.strip().splitlines()[0])
    print(f"  L1 = {L1:.0f} mm, L2 = {L2:.0f} mm  (worked example)")
    print(f"  reachable annulus: {REACH_MIN:.0f} to {REACH_MAX:.0f} mm\n")

    print("  round-trip error over a sweep of poses:")
    worst = 0.0
    for t1 in np.linspace(-math.pi / 2, math.pi / 2, 9):
        for t2 in np.linspace(0.15, math.pi - 0.15, 9):
            worst = max(worst, round_trip_error(float(t1), float(t2)))
    print(f"    worst case {worst:.3e} mm  ({'ok' if worst < 1e-6 else 'FAIL'})")

    print("\n  fully extended is the singularity:")
    for t2_deg in (30, 10, 2, 0):
        d = jacobian_determinant(math.radians(t2_deg))
        print(f"    theta2 = {t2_deg:>2}deg   det(J) = {d:>9.1f}")

    print("\n  unreachable targets are refused, not clipped:")
    for target in ((900.0, 0.0), (10.0, 0.0)):
        try:
            inverse(*target)
        except ValueError as exc:
            print(f"    {target} -> {exc}")


if __name__ == "__main__":
    _self_check()

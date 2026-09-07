"""
Trapezoidal velocity profile for one joint move.

Applies to any joint on either arm: the SHAPE of a trapezoidal profile does not
depend on scale, only the axis values do. The move plotted here is a 90 degree
shoulder sweep, which is the sort of thing the real arm does between the
conveyor and a bin.

What the plot is for: the acceleration trace is a square wave, and those
instantaneous steps are jerk. On a long steel arm jerk is what excites the
structure and leaves the tool ringing after the move has nominally finished.
The fix, if it shows up, is an S-curve profile that ramps acceleration instead
of stepping it. Saying that in the report is worth more than the plot itself.

Run it:
    python -m sim.trajectory
    python -m sim.trajectory --angle 90 --vmax 60 --amax 120
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "figures"

INK, ACCENT, MARK, MUTED = "#171D21", "#0E6E88", "#B4531C", "#58656B"


def profile(angle_deg: float, vmax: float, amax: float, n: int = 900):
    """
    Position, velocity and acceleration against time.

    vmax in deg/s, amax in deg/s^2. If the move is too short to reach vmax the
    profile degenerates to a triangle, which is handled rather than ignored --
    short moves are the common case in a pick-and-place cycle, so getting this
    branch wrong understates the cycle time.
    """
    t_ramp = vmax / amax
    d_ramp = 0.5 * amax * t_ramp ** 2

    if 2 * d_ramp >= angle_deg:            # triangular: never reaches vmax
        t_ramp = float(np.sqrt(angle_deg / amax))
        t_flat = 0.0
        peak_v = amax * t_ramp
    else:                                   # trapezoidal
        t_flat = (angle_deg - 2 * d_ramp) / vmax
        peak_v = vmax

    total = 2 * t_ramp + t_flat
    t = np.linspace(0, total, n)

    a = np.where(t < t_ramp, amax,
        np.where(t < t_ramp + t_flat, 0.0, -amax))

    v = np.where(t < t_ramp, amax * t,
        np.where(t < t_ramp + t_flat, peak_v,
                 peak_v - amax * (t - t_ramp - t_flat)))
    v = np.clip(v, 0, None)

    p = np.where(t < t_ramp, 0.5 * amax * t ** 2,
        np.where(t < t_ramp + t_flat,
                 d_ramp + peak_v * (t - t_ramp),
                 angle_deg - 0.5 * amax * (total - t) ** 2))

    return t, p, v, a, {"total": total, "t_ramp": t_ramp,
                        "t_flat": t_flat, "peak_v": peak_v,
                        "triangular": t_flat == 0.0}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--angle", type=float, default=90.0, help="move, degrees")
    ap.add_argument("--vmax", type=float, default=60.0, help="deg/s")
    ap.add_argument("--amax", type=float, default=120.0, help="deg/s^2")
    args = ap.parse_args()

    t, p, v, a, info = profile(args.angle, args.vmax, args.amax)
    OUT.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)

    axes[0].plot(t, p, color=MUTED, lw=1.8)
    axes[0].set_ylabel("position (deg)")
    axes[0].set_title(f"Trapezoidal profile — {args.angle:.0f}deg move, "
                      f"vmax {args.vmax:.0f} deg/s, amax {args.amax:.0f} deg/s²")

    axes[1].plot(t, v, color=ACCENT, lw=2)
    axes[1].set_ylabel("velocity (deg/s)")

    axes[2].plot(t, a, color=MARK, lw=2)
    axes[2].set_ylabel("acceleration (deg/s²)")
    axes[2].set_xlabel("time (s)")
    axes[2].annotate("step in acceleration = jerk",
                     xy=(info["t_ramp"], 0), xytext=(info["t_ramp"] * 1.35,
                     args.amax * 0.55), fontsize=8.5, color=MARK,
                     arrowprops=dict(arrowstyle="->", color=MARK, lw=1))

    for ax in axes:
        ax.grid(alpha=0.2)
        for boundary in (info["t_ramp"], info["t_ramp"] + info["t_flat"]):
            ax.axvline(boundary, color=MUTED, ls=":", lw=1)

    fig.tight_layout()
    path = OUT / "trajectory.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)

    shape = "triangular (move too short to reach vmax)" if info["triangular"] else "trapezoidal"
    print(f"  profile: {shape}")
    print(f"  ramp {info['t_ramp']:.3f} s, cruise {info['t_flat']:.3f} s, "
          f"peak {info['peak_v']:.1f} deg/s")
    print(f"  move time: {info['total']:.3f} s")
    print(f"  final position: {p[-1]:.2f} deg (target {args.angle:.2f})")
    print(f"  wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

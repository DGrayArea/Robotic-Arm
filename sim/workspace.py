"""
Plot the reachable workspace of the worked-example arm.

WORKED EXAMPLE, NOT THE CAD MODEL. See sim/arm.py for why.

The point of doing this in code rather than drawing it: the annulus is not
assumed anywhere. Both joints are swept across their range, every resulting tool
position is scattered, and the shape appears because the equations produce it.
Drawing two circles from the answer proves nothing.

Run it:
    python -m sim.workspace
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")  # write a file, no window
import matplotlib.pyplot as plt  # noqa: E402

from sim.arm import L1, L2, REACH_MAX, REACH_MIN, forward  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "figures"

INK, ACCENT, MARK = "#171D21", "#0E6E88", "#B4531C"


def sweep(n: int = 240) -> tuple[np.ndarray, np.ndarray]:
    """Every reachable tool position, from the kinematics alone."""
    t1 = np.linspace(-math.pi, math.pi, n)
    t2 = np.linspace(-math.pi, math.pi, n)
    T1, T2 = np.meshgrid(t1, t2)
    X = L1 * np.cos(T1) + L2 * np.cos(T1 + T2)
    Y = L1 * np.sin(T1) + L2 * np.sin(T1 + T2)
    return X.ravel(), Y.ravel()


def main() -> None:
    x, y = sweep()
    OUT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    ax.scatter(x, y, s=1.2, alpha=0.30, color=ACCENT, linewidths=0,
               label="reachable, swept from the equations")

    # The bounds, drawn afterwards, to check they agree with the scatter.
    for r, colour, style, label in (
        (REACH_MAX, MARK, "--", f"L1+L2 = {REACH_MAX:.0f} mm"),
        (REACH_MIN, MARK, "-", f"|L1-L2| = {REACH_MIN:.0f} mm"),
    ):
        ax.add_patch(plt.Circle((0, 0), r, fill=False, ec=colour,
                                ls=style, lw=1.6, zorder=3))
        ax.plot([], [], color=colour, ls=style, lw=1.6, label=label)

    ax.plot(0, 0, "o", color=INK, ms=6, zorder=4)
    ax.set_aspect("equal")
    lim = REACH_MAX * 1.15
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("Reachable workspace — worked example, L1=250 L2=150")
    ax.grid(alpha=0.18)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    fig.text(0.5, 0.015,
             "WORKED EXAMPLE — not the six-axis CAD model",
             ha="center", fontsize=8.5, color=MARK)

    path = OUT / "workspace.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    inside = np.hypot(x, y)
    print(f"  swept {len(x):,} poses")
    print(f"  radius range reached: {inside.min():.1f} to {inside.max():.1f} mm")
    print(f"  bounds from L1,L2   : {REACH_MIN:.1f} to {REACH_MAX:.1f} mm")
    print(f"  wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

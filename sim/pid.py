"""
Closed-loop step response of one joint under PID.

The joint is modelled as a second-order system, inertia and viscous damping,
with a constant gravity load. That load is the reason integral action is not
optional here: proportional and derivative terms both go to zero as the error
does, so a P or PD controller settles wherever the proportional effort happens
to balance gravity, which is short of target. Only the integral term keeps
pushing once the error is small.

The shapes are scale-independent, so this demonstrates the method for either
arm. The gains are not tuned for the real machine and would need redoing once
the inertia is known from the CAD.

Run it:
    python -m sim.pid
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "figures"

INK, ACCENT, MARK, MUTED = "#171D21", "#0E6E88", "#B4531C", "#58656B"

# Joint model. J is a stand-in until the CAD gives a real inertia.
J = 0.8          # kg*m^2, rotor + link about the joint
B = 0.35         # N*m*s/rad, viscous damping
GRAVITY_LOAD = 4.0   # N*m, constant disturbance holding the arm down

SETPOINT = 1.0   # rad
DT = 0.002
T_END = 6.0


def simulate(kp: float, ki: float, kd: float,
             gravity: float = GRAVITY_LOAD) -> tuple[np.ndarray, np.ndarray]:
    """Euler integration of J*theta'' + B*theta' = u - gravity."""
    steps = int(T_END / DT)
    t = np.linspace(0, T_END, steps)
    theta = np.zeros(steps)
    omega = 0.0
    integral = 0.0
    prev_err = SETPOINT

    for i in range(1, steps):
        err = SETPOINT - theta[i - 1]
        integral += err * DT
        derivative = (err - prev_err) / DT
        prev_err = err

        u = kp * err + ki * integral + kd * derivative
        alpha = (u - B * omega - gravity) / J
        omega += alpha * DT
        theta[i] = theta[i - 1] + omega * DT

    return t, theta


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    cases = [
        ("P only — oscillates, centred below target", 40.0,  0.0,  0.0, MUTED, ":"),
        ("PD — no offset removal, still short",       40.0,  0.0,  8.0, MUTED, "--"),
        ("PID under-damped — payload swings",         90.0, 60.0,  4.0, MARK,  "-"),
        ("PID slightly over-damped — chosen",         45.0, 25.0, 18.0, ACCENT, "-"),
    ]

    fig, ax = plt.subplots(figsize=(8.4, 5))
    ax.axhline(SETPOINT, color=INK, ls="--", lw=1, alpha=0.6)
    ax.text(T_END * 0.985, SETPOINT + 0.02, "target", ha="right",
            fontsize=8.5, color=INK)

    summary = []
    for label, kp, ki, kd, colour, style in cases:
        t, theta = simulate(kp, ki, kd)
        lw = 2.2 if colour == ACCENT else 1.5
        ax.plot(t, theta, color=colour, ls=style, lw=lw, label=label)

        final = theta[-1]
        overshoot = (theta.max() - SETPOINT) / SETPOINT * 100
        summary.append((label, final, SETPOINT - final, max(overshoot, 0.0)))

    ax.set_xlabel("time (s)")
    ax.set_ylabel("joint angle (rad)")
    ax.set_title("Step response under a constant gravity load")
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()

    path = OUT / "pid_step_response.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)

    print(f"  {'controller':<40}{'final':>8}{'offset':>9}{'overshoot':>11}")
    print("  " + "-" * 68)
    for label, final, offset, overshoot in summary:
        print(f"  {label:<40}{final:>8.3f}{offset:>9.3f}{overshoot:>10.1f}%")
    print(f"\n  wrote {path.relative_to(ROOT)}")
    print("  Note the steady-state offset on the two rows without integral action:")
    print("  that gap is gravity, and no amount of proportional gain removes it.")


if __name__ == "__main__":
    main()

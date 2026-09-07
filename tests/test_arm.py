"""
Tests for the worked-example kinematics.

The one that matters is the round trip. A sign error in theta1 still returns
plausible-looking angles, and a plot of them still looks like an arm; it only
shows up when you drive the angles forward, invert the result, and land
somewhere else. That is the bug this catches, and it is the reason week 15 of
the logbook codes the kinematics rather than stopping at the hand derivation.
"""

from __future__ import annotations

import math

import pytest

from sim.arm import (
    L1,
    L2,
    REACH_MAX,
    REACH_MIN,
    forward,
    inverse,
    jacobian_determinant,
    round_trip_error,
)


class TestForward:
    def test_fully_extended_reaches_the_outer_bound(self):
        x, y = forward(0.0, 0.0)
        assert x == pytest.approx(REACH_MAX)
        assert y == pytest.approx(0.0)

    def test_folded_back_reaches_the_inner_bound(self):
        x, y = forward(0.0, math.pi)
        assert x == pytest.approx(REACH_MIN)
        assert y == pytest.approx(0.0, abs=1e-9)

    def test_straight_up(self):
        x, y = forward(math.pi / 2, 0.0)
        assert x == pytest.approx(0.0, abs=1e-9)
        assert y == pytest.approx(REACH_MAX)


class TestInverse:
    @pytest.mark.parametrize("theta1", [-1.2, -0.4, 0.0, 0.7, 1.4])
    @pytest.mark.parametrize("theta2", [0.2, 0.9, 1.8, 2.6])
    def test_round_trip_is_exact(self, theta1, theta2):
        assert round_trip_error(theta1, theta2) < 1e-9

    def test_both_elbow_branches_reach_the_same_point(self):
        target = (300.0, 120.0)
        up = inverse(*target, elbow_up=True)
        down = inverse(*target, elbow_up=False)

        assert forward(*up) == pytest.approx(target, abs=1e-9)
        assert forward(*down) == pytest.approx(target, abs=1e-9)
        # Genuinely different poses reaching one point.
        assert up[1] == pytest.approx(-down[1])
        assert up != down

    @pytest.mark.parametrize("target", [
        (900.0, 0.0),    # past full extension
        (10.0, 0.0),     # inside the dead zone
        (0.0, 0.0),      # the base itself
    ])
    def test_unreachable_targets_raise_rather_than_clip(self, target):
        # Silently snapping to the nearest reachable point is how a machine ends
        # up moving somewhere nobody asked it to.
        with pytest.raises(ValueError, match="outside the reachable annulus"):
            inverse(*target)

    def test_the_bounds_themselves_are_reachable(self):
        for r in (REACH_MIN, REACH_MAX):
            t1, t2 = inverse(r, 0.0)
            x, y = forward(t1, t2)
            assert math.hypot(x, y) == pytest.approx(r, abs=1e-6)


class TestSingularity:
    def test_determinant_vanishes_at_full_extension(self):
        assert jacobian_determinant(0.0) == pytest.approx(0.0)

    def test_determinant_vanishes_when_fully_folded(self):
        # Tolerance is scaled to L1*L2: sin(pi) is not exactly zero in floating
        # point, so the product carries that error up to ~1e-12 of 37500.
        assert jacobian_determinant(math.pi) == pytest.approx(0.0, abs=1e-6)

    def test_determinant_is_largest_at_a_right_angle(self):
        at_90 = abs(jacobian_determinant(math.pi / 2))
        assert at_90 == pytest.approx(L1 * L2)
        for theta2 in (0.3, 1.0, 2.4, 2.9):
            assert abs(jacobian_determinant(theta2)) <= at_90 + 1e-9

    def test_conditioning_collapses_approaching_the_boundary(self):
        # This is why the logbook adds a software limit rather than trusting the
        # solver: the arm is still solvable here, just not drivable.
        #
        # det(J) = L1*L2*sin(theta2), so the falloff is exactly the sine ratio.
        # Asserting that rather than an invented threshold: at 2 degrees the
        # determinant is about 7% of its value at 30, so a tool move near the
        # boundary demands roughly 14x the joint speed for the same result.
        angles = (30, 10, 2)
        dets = [abs(jacobian_determinant(math.radians(d))) for d in angles]
        assert dets[0] > dets[1] > dets[2]

        expected = math.sin(math.radians(2)) / math.sin(math.radians(30))
        assert dets[2] / dets[0] == pytest.approx(expected, rel=1e-9)
        assert expected < 0.10

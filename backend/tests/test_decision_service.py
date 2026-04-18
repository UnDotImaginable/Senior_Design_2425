"""
Unit tests for services/decision_service.py

Tests the get_pending_command function which was updated in this PR to:
- Accept None values for g_now, g_future, and b_charge
- Return grid_with_gerror when price data is unavailable
- Return grid_with_berror when battery charge is unknown
- Use >= instead of > for g_future vs g_now comparison (equal prices now favour charging)
"""
import sys
import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.decision_service import get_pending_command


class TestGetPendingCommand:
    # ── Error / None input cases (new in this PR) ─────────────────────────────

    def test_g_now_none_returns_grid_error(self):
        result = get_pending_command(g_now=None, g_future=0.20, b_charge=50.0)
        assert result["command"] == "switch_to_grid"
        assert "grid" in result["reason"].lower() or "price" in result["reason"].lower()
        assert "ERROR" in result["reason"]

    def test_g_future_none_returns_grid_error(self):
        result = get_pending_command(g_now=0.15, g_future=None, b_charge=50.0)
        assert result["command"] == "switch_to_grid"
        assert "ERROR" in result["reason"]

    def test_both_prices_none_returns_grid_error(self):
        result = get_pending_command(g_now=None, g_future=None, b_charge=50.0)
        assert result["command"] == "switch_to_grid"
        assert "ERROR" in result["reason"]

    def test_b_charge_none_returns_battery_error(self):
        result = get_pending_command(g_now=0.15, g_future=0.28, b_charge=None)
        assert result["command"] == "switch_to_grid"
        assert "ERROR" in result["reason"]
        assert "battery" in result["reason"].lower()

    def test_all_none_returns_grid_error_not_battery_error(self):
        """Price errors take priority over battery errors (checked first in code)."""
        result = get_pending_command(g_now=None, g_future=None, b_charge=None)
        assert result["command"] == "switch_to_grid"
        # Should hit grid price error before battery error
        assert "grid" in result["reason"].lower() or "price" in result["reason"].lower()

    # ── Future more expensive → charge battery (use grid now) ─────────────────

    def test_future_more_expensive_returns_grid(self):
        result = get_pending_command(g_now=0.15, g_future=0.28, b_charge=60.0)
        assert result["command"] == "switch_to_grid"
        assert "ERROR" not in result["reason"]

    def test_future_more_expensive_with_empty_battery_still_grid(self):
        """Even with empty battery, if future is expensive we charge via grid."""
        result = get_pending_command(g_now=0.15, g_future=0.28, b_charge=0.0)
        assert result["command"] == "switch_to_grid"

    # ── Equal prices → charge battery (new >= behaviour added in this PR) ────

    def test_equal_prices_returns_grid(self):
        """PR changed > to >=: equal prices should now favour charging (grid)."""
        result = get_pending_command(g_now=0.15, g_future=0.15, b_charge=50.0)
        assert result["command"] == "switch_to_grid"

    def test_equal_zero_prices_returns_grid(self):
        result = get_pending_command(g_now=0.0, g_future=0.0, b_charge=80.0)
        assert result["command"] == "switch_to_grid"

    # ── Future cheaper → discharge battery ────────────────────────────────────

    def test_future_cheaper_with_charge_returns_battery(self):
        result = get_pending_command(g_now=0.28, g_future=0.08, b_charge=70.0)
        assert result["command"] == "switch_to_battery"

    def test_future_cheaper_battery_at_1_percent_uses_battery(self):
        """b_charge > 0 even at 1% should prefer battery."""
        result = get_pending_command(g_now=0.28, g_future=0.08, b_charge=1.0)
        assert result["command"] == "switch_to_battery"

    def test_future_cheaper_empty_battery_falls_back_to_grid(self):
        result = get_pending_command(g_now=0.28, g_future=0.08, b_charge=0.0)
        assert result["command"] == "switch_to_grid"
        assert "empty" in result["reason"].lower() or "battery" in result["reason"].lower()

    # ── Return value structure ─────────────────────────────────────────────────

    def test_return_value_always_has_command_and_reason(self):
        cases = [
            (None, None, None),
            (None, 0.2, 50.0),
            (0.15, None, 50.0),
            (0.15, 0.28, None),
            (0.15, 0.28, 60.0),
            (0.28, 0.08, 60.0),
            (0.28, 0.08, 0.0),
            (0.15, 0.15, 50.0),
        ]
        for g_now, g_future, b_charge in cases:
            result = get_pending_command(g_now, g_future, b_charge)
            assert "command" in result, f"Missing 'command' for inputs {g_now}, {g_future}, {b_charge}"
            assert "reason" in result, f"Missing 'reason' for inputs {g_now}, {g_future}, {b_charge}"
            assert result["command"] in {"switch_to_battery", "switch_to_grid"}

    def test_battery_command_reason_is_non_empty(self):
        result = get_pending_command(g_now=0.28, g_future=0.08, b_charge=50.0)
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 0

    # ── Boundary / regression cases ───────────────────────────────────────────

    def test_future_just_below_current_triggers_battery(self):
        """g_future < g_now by a tiny amount should trigger battery mode."""
        result = get_pending_command(g_now=0.15, g_future=0.14999, b_charge=50.0)
        assert result["command"] == "switch_to_battery"

    def test_future_just_above_current_triggers_grid(self):
        result = get_pending_command(g_now=0.15, g_future=0.15001, b_charge=50.0)
        assert result["command"] == "switch_to_grid"

    def test_negative_prices_handled(self):
        """Negative LMP prices can occur on the grid; code should not crash."""
        result = get_pending_command(g_now=-5.0, g_future=-10.0, b_charge=50.0)
        # g_future < g_now → battery mode
        assert result["command"] == "switch_to_battery"

    def test_large_price_spread(self):
        result = get_pending_command(g_now=1000.0, g_future=1.0, b_charge=99.0)
        assert result["command"] == "switch_to_battery"
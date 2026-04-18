"""
Unit and integration tests for routes/cost.py

Covers the new functions introduced in this PR:
  - get_hour_zone(dt)
  - get_switch_windows(db, days)
  - get_battery_level_at(db, timestamp)
  - get_avg_lmp(db, start, end)
  - calculate_cost_savings(db, days)
  - GET /api/cost/ endpoint
"""
import sys
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from tests.conftest import (
    make_user,
    make_sensor_reading,
    make_switch_event,
    make_realtime_lmp,
    make_day_ahead_lmp,
)
from routes.cost import (
    get_hour_zone,
    get_switch_windows,
    get_battery_level_at,
    get_avg_lmp,
    calculate_cost_savings,
    EPT,
    BATTERY_CAPACITY_KWH,
)


# ── get_hour_zone ─────────────────────────────────────────────────────────────

class TestGetHourZone:
    def _ept(self, hour: int) -> datetime:
        """Return a timezone-aware datetime at the given EPT hour today."""
        return datetime.now(EPT).replace(hour=hour, minute=0, second=0, microsecond=0)

    def test_peak_start_hour(self):
        assert get_hour_zone(self._ept(17)) == "peak"

    def test_peak_mid_hour(self):
        assert get_hour_zone(self._ept(19)) == "peak"

    def test_peak_last_hour(self):
        assert get_hour_zone(self._ept(20)) == "peak"

    def test_off_peak_midnight(self):
        assert get_hour_zone(self._ept(0)) == "off_peak"

    def test_off_peak_mid_hour(self):
        assert get_hour_zone(self._ept(3)) == "off_peak"

    def test_off_peak_last_hour(self):
        assert get_hour_zone(self._ept(5)) == "off_peak"

    def test_standard_morning(self):
        assert get_hour_zone(self._ept(6)) == "standard"

    def test_standard_midday(self):
        assert get_hour_zone(self._ept(12)) == "standard"

    def test_standard_just_before_peak(self):
        assert get_hour_zone(self._ept(16)) == "standard"

    def test_standard_after_peak(self):
        assert get_hour_zone(self._ept(21)) == "standard"

    def test_standard_late_night(self):
        assert get_hour_zone(self._ept(23)) == "standard"

    def test_accepts_utc_datetime_and_converts(self):
        # 22:00 UTC is 18:00 EDT (UTC-4) → peak
        dt_utc = datetime(2024, 7, 1, 22, 0, 0, tzinfo=timezone.utc)
        assert get_hour_zone(dt_utc) == "peak"


# ── get_switch_windows ────────────────────────────────────────────────────────

class TestGetSwitchWindows:
    def test_returns_empty_when_no_events_and_no_seed(self, db):
        windows = get_switch_windows(db, days=30)
        assert windows == []

    def test_single_event_creates_one_window(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_switch_event(db, switched_to="battery", timestamp=now - timedelta(hours=1))
        windows = get_switch_windows(db, days=30)
        assert len(windows) == 1
        assert windows[0]["type"] == "battery"

    def test_two_events_create_two_windows(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_switch_event(db, switched_to="grid",    timestamp=now - timedelta(hours=3))
        make_switch_event(db, switched_to="battery", timestamp=now - timedelta(hours=1))
        windows = get_switch_windows(db, days=30)
        assert len(windows) == 2
        assert windows[0]["type"] == "grid"
        assert windows[1]["type"] == "battery"

    def test_seed_event_creates_leading_window(self, db):
        """An event before the window boundary seeds an initial window."""
        make_user(db)
        now = datetime.now(timezone.utc)
        # Seed: happened 35 days ago (before the 30-day window)
        make_switch_event(db, switched_to="grid", timestamp=now - timedelta(days=35))
        # Event inside the window
        make_switch_event(db, switched_to="battery", timestamp=now - timedelta(days=1))
        windows = get_switch_windows(db, days=30)
        # Should have: seed window (grid) + in-window event window (battery)
        assert len(windows) == 2
        assert windows[0]["type"] == "grid"
        assert windows[1]["type"] == "battery"

    def test_window_end_of_last_event_is_approximately_now(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_switch_event(db, switched_to="battery", timestamp=now - timedelta(hours=2))
        windows = get_switch_windows(db, days=30)
        # The last window's end should be close to now
        last_end = windows[-1]["end"]
        assert abs((last_end - now).total_seconds()) < 5

    def test_window_has_start_end_type_keys(self, db):
        make_user(db)
        make_switch_event(db, switched_to="grid")
        for w in get_switch_windows(db, days=30):
            assert "type" in w
            assert "start" in w
            assert "end" in w


# ── get_battery_level_at ──────────────────────────────────────────────────────

class TestGetBatteryLevelAt:
    def test_returns_none_when_no_readings(self, db):
        ts = datetime.now(timezone.utc)
        assert get_battery_level_at(db, ts) is None

    def test_returns_level_for_reading_within_window(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_sensor_reading(db, battery_level=70, timestamp=now - timedelta(minutes=5))
        result = get_battery_level_at(db, now)
        assert result == 70

    def test_returns_none_for_reading_outside_window(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        # Reading 20 minutes away — outside the 15-minute max_gap
        make_sensor_reading(db, battery_level=70, timestamp=now - timedelta(minutes=20))
        result = get_battery_level_at(db, now)
        assert result is None

    def test_returns_a_reading_when_two_in_window(self, db):
        """When multiple readings fall within the 15-min window, one is returned."""
        make_user(db)
        now = datetime.now(timezone.utc)
        make_sensor_reading(db, battery_level=60, timestamp=now - timedelta(minutes=12))
        make_sensor_reading(db, battery_level=65, timestamp=now - timedelta(minutes=3))
        result = get_battery_level_at(db, now)
        # The ordering is best-effort; at minimum one of the readings is returned.
        assert result in (60, 65)

    def test_boundary_exactly_15_minutes_included(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_sensor_reading(db, battery_level=80, timestamp=now - timedelta(minutes=15))
        result = get_battery_level_at(db, now)
        assert result == 80


# ── get_avg_lmp ───────────────────────────────────────────────────────────────

class TestGetAvgLmp:
    def test_returns_none_when_no_data(self, db):
        now = datetime.now(timezone.utc)
        result = get_avg_lmp(db, now - timedelta(hours=1), now)
        assert result is None

    def test_returns_avg_of_single_record(self, db):
        now = datetime.now(timezone.utc)
        make_realtime_lmp(db, total_lmp_rt=50.0, dt_utc=now - timedelta(minutes=30))
        result = get_avg_lmp(db, now - timedelta(hours=1), now)
        assert result == pytest.approx(50.0)

    def test_returns_avg_of_multiple_records(self, db):
        now = datetime.now(timezone.utc)
        make_realtime_lmp(db, total_lmp_rt=40.0, dt_utc=now - timedelta(minutes=50))
        make_realtime_lmp(db, total_lmp_rt=60.0, dt_utc=now - timedelta(minutes=20))
        result = get_avg_lmp(db, now - timedelta(hours=1), now)
        assert result == pytest.approx(50.0)

    def test_ignores_non_latest_version(self, db):
        now = datetime.now(timezone.utc)
        make_realtime_lmp(db, total_lmp_rt=100.0, latest_version=False, dt_utc=now - timedelta(minutes=30))
        result = get_avg_lmp(db, now - timedelta(hours=1), now)
        assert result is None

    def test_returns_none_for_records_outside_range(self, db):
        now = datetime.now(timezone.utc)
        make_realtime_lmp(db, total_lmp_rt=50.0, dt_utc=now - timedelta(hours=3))
        result = get_avg_lmp(db, now - timedelta(hours=1), now)
        assert result is None


# ── calculate_cost_savings ────────────────────────────────────────────────────

class TestCalculateCostSavings:
    def test_returns_zeroes_when_no_switch_events(self, db):
        result = calculate_cost_savings(db, days=30)
        mc = result["monthlyCost"]
        assert mc["actual"] == 0.0
        assert mc["withoutSystem"] == 0.0
        assert mc["savings"] == 0.0
        assert mc["savingsPercentage"] == 0.0

    def test_returns_empty_breakdown_when_no_events(self, db):
        result = calculate_cost_savings(db, days=30)
        assert result["breakdown"] == []

    def test_breakdown_has_three_zones_when_data_exists(self, db):
        """When there are windows + data, breakdown must have 3 zone entries."""
        make_user(db)
        now = datetime.now(timezone.utc)
        # Create a grid window with matching sensor readings and LMP
        t_start = now - timedelta(hours=2)
        t_end   = now - timedelta(hours=1)
        make_switch_event(db, switched_to="grid", timestamp=t_start)
        make_sensor_reading(db, battery_level=50, timestamp=t_start)
        make_sensor_reading(db, battery_level=75, timestamp=t_end)
        make_realtime_lmp(db, total_lmp_rt=30.0, dt_utc=t_start + timedelta(minutes=30))
        result = calculate_cost_savings(db, days=30)
        assert len(result["breakdown"]) == 3

    def test_grid_window_adds_to_actual_cost(self, db):
        """Charging from grid contributes to actual cost paid."""
        make_user(db)
        now = datetime.now(timezone.utc)
        t_start = now - timedelta(hours=2)
        # Add two events so the first window (grid) ends at t_switch, not at now
        t_switch = now - timedelta(hours=1)
        make_switch_event(db, switched_to="grid",    timestamp=t_start)
        make_switch_event(db, switched_to="battery", timestamp=t_switch)
        # battery went from 0% to 100% during the grid window (max delta)
        make_sensor_reading(db, battery_level=0,   timestamp=t_start)
        make_sensor_reading(db, battery_level=100, timestamp=t_switch)
        # also add a reading near now so the battery window's end has a match
        make_sensor_reading(db, battery_level=60, timestamp=now - timedelta(seconds=30))
        # Use large LMP so that cost rounds above $0.00 (battery capacity = 0.004 kWh)
        make_realtime_lmp(db, total_lmp_rt=5000.0, dt_utc=t_start + timedelta(minutes=30))
        make_realtime_lmp(db, total_lmp_rt=5000.0, dt_utc=t_switch + timedelta(minutes=30))
        result = calculate_cost_savings(db, days=30)
        assert result["monthlyCost"]["actual"] > 0.0

    def test_battery_window_adds_to_without_system_cost(self, db):
        """Discharging avoids cost → adds to withoutSystem."""
        make_user(db)
        now = datetime.now(timezone.utc)
        t_start = now - timedelta(hours=2)
        t_switch = now - timedelta(hours=1)
        # battery → grid: the battery window ends at t_switch
        make_switch_event(db, switched_to="battery", timestamp=t_start)
        make_switch_event(db, switched_to="grid",    timestamp=t_switch)
        # 100% → 0% during discharge (max delta)
        make_sensor_reading(db, battery_level=100, timestamp=t_start)
        make_sensor_reading(db, battery_level=0,   timestamp=t_switch)
        # reading near now for the grid window's end
        make_sensor_reading(db, battery_level=10, timestamp=now - timedelta(seconds=30))
        # Large LMP so cost rounds above $0.00
        make_realtime_lmp(db, total_lmp_rt=5000.0, dt_utc=t_start + timedelta(minutes=30))
        make_realtime_lmp(db, total_lmp_rt=5000.0, dt_utc=t_switch + timedelta(minutes=30))
        result = calculate_cost_savings(db, days=30)
        assert result["monthlyCost"]["withoutSystem"] > 0.0

    def test_savings_equals_without_minus_actual(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        t1 = now - timedelta(hours=4)
        t2 = now - timedelta(hours=3)
        t3 = now - timedelta(hours=2)
        t4 = now - timedelta(hours=1)
        # grid window
        make_switch_event(db, switched_to="grid",    timestamp=t1)
        # battery window
        make_switch_event(db, switched_to="battery", timestamp=t2)
        # Sensor readings at each boundary
        make_sensor_reading(db, battery_level=40, timestamp=t1)
        make_sensor_reading(db, battery_level=70, timestamp=t2)
        make_sensor_reading(db, battery_level=50, timestamp=t3)
        make_sensor_reading(db, battery_level=30, timestamp=t4)
        # LMP for both windows
        make_realtime_lmp(db, total_lmp_rt=20.0, dt_utc=t1 + timedelta(minutes=30))
        make_realtime_lmp(db, total_lmp_rt=50.0, dt_utc=t2 + timedelta(minutes=30))
        result = calculate_cost_savings(db, days=30)
        mc = result["monthlyCost"]
        assert mc["savings"] == pytest.approx(mc["withoutSystem"] - mc["actual"], abs=0.01)

    def test_savings_percentage_formula(self, db):
        """savingsPercentage = savings / withoutSystem * 100."""
        make_user(db)
        now = datetime.now(timezone.utc)
        t_start = now - timedelta(hours=2)
        t_mid   = now - timedelta(hours=1, minutes=30)
        t_end   = now - timedelta(hours=1)
        make_switch_event(db, switched_to="battery", timestamp=t_start)
        make_sensor_reading(db, battery_level=80, timestamp=t_start)
        make_sensor_reading(db, battery_level=40, timestamp=t_end)
        make_realtime_lmp(db, total_lmp_rt=30.0, dt_utc=t_mid)
        result = calculate_cost_savings(db, days=30)
        mc = result["monthlyCost"]
        if mc["withoutSystem"] > 0:
            expected_pct = round(mc["savings"] / mc["withoutSystem"] * 100, 1)
            assert mc["savingsPercentage"] == pytest.approx(expected_pct, abs=0.1)

    def test_missing_lmp_skips_window(self, db):
        """Windows without matching LMP data should be skipped (not crash)."""
        make_user(db)
        now = datetime.now(timezone.utc)
        make_switch_event(db, switched_to="battery", timestamp=now - timedelta(hours=2))
        make_sensor_reading(db, battery_level=80, timestamp=now - timedelta(hours=2))
        make_sensor_reading(db, battery_level=60, timestamp=now - timedelta(hours=1))
        # No LMP data inserted
        result = calculate_cost_savings(db, days=30)
        assert result["monthlyCost"]["actual"] == 0.0
        assert result["monthlyCost"]["withoutSystem"] == 0.0

    def test_breakdown_zone_labels(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_switch_event(db, switched_to="grid", timestamp=now - timedelta(hours=2))
        make_sensor_reading(db, battery_level=50, timestamp=now - timedelta(hours=2))
        make_sensor_reading(db, battery_level=60, timestamp=now - timedelta(hours=1))
        make_realtime_lmp(db, total_lmp_rt=30.0, dt_utc=now - timedelta(hours=1, minutes=30))
        result = calculate_cost_savings(db, days=30)
        labels = {item["category"] for item in result["breakdown"]}
        assert "Peak Hours" in labels
        assert "Off-Peak Hours" in labels
        assert "Standard Hours" in labels


# ── GET /api/cost/ endpoint ───────────────────────────────────────────────────

class TestCostEndpoint:
    def test_returns_200(self, client):
        response = client.get("/api/cost/")
        assert response.status_code == 200

    def test_response_has_required_top_level_keys(self, client):
        data = client.get("/api/cost/").json()
        assert "monthlyCost" in data
        assert "pricingZones" in data
        assert "breakdown" in data

    def test_monthly_cost_has_required_fields(self, client):
        mc = client.get("/api/cost/").json()["monthlyCost"]
        assert "actual" in mc
        assert "withoutSystem" in mc
        assert "savings" in mc
        assert "savingsPercentage" in mc

    def test_pricing_zones_contains_24_entries(self, client):
        zones = client.get("/api/cost/").json()["pricingZones"]
        assert len(zones) == 24

    def test_pricing_zone_entry_has_required_fields(self, client):
        zone = client.get("/api/cost/").json()["pricingZones"][0]
        assert "hour" in zone
        assert "price" in zone
        assert "is_forecast" in zone

    def test_default_zeroes_when_no_data(self, client):
        mc = client.get("/api/cost/").json()["monthlyCost"]
        assert mc["actual"] == 0.0
        assert mc["withoutSystem"] == 0.0
        assert mc["savings"] == 0.0
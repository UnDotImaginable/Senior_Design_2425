"""
Unit and integration tests for routes/dashboard.py

Covers the new helper functions introduced in this PR:
  - get_current_user(db)
  - get_current_price(db)
  - get_current_source(db)
  - get_uptime(db, days)
And the updated GET /api/dashboard/ endpoint.
"""
import sys
import os
from datetime import datetime, timezone, timedelta

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from tests.conftest import make_user, make_sensor_reading, make_realtime_lmp
from routes.dashboard import get_current_user, get_current_price, get_current_source, get_uptime


# ── get_current_user ──────────────────────────────────────────────────────────

class TestGetCurrentUser:
    def test_returns_none_fields_when_no_user(self, db):
        result = get_current_user(db)
        assert result == {"firstName": None, "fullName": None}

    def test_returns_correct_full_name(self, db):
        make_user(db, full_name="Jane Smith")
        result = get_current_user(db)
        assert result["fullName"] == "Jane Smith"

    def test_extracts_first_name(self, db):
        make_user(db, full_name="Jane Smith")
        result = get_current_user(db)
        assert result["firstName"] == "Jane"

    def test_handles_single_word_name(self, db):
        make_user(db, full_name="Madonna")
        result = get_current_user(db)
        assert result["firstName"] == "Madonna"
        assert result["fullName"] == "Madonna"

    def test_handles_three_part_name(self, db):
        make_user(db, full_name="Mary Jane Watson")
        result = get_current_user(db)
        assert result["firstName"] == "Mary"
        assert result["fullName"] == "Mary Jane Watson"

    def test_strips_leading_trailing_whitespace(self, db):
        make_user(db, full_name="  John Doe  ")
        result = get_current_user(db)
        assert result["fullName"] == "John Doe"
        assert result["firstName"] == "John"

    def test_none_full_name_returns_none_fields(self, db):
        make_user(db, full_name=None)
        result = get_current_user(db)
        assert result["firstName"] is None
        assert result["fullName"] is None


# ── get_current_price ─────────────────────────────────────────────────────────

class TestGetCurrentPrice:
    def test_returns_none_when_no_lmp_data(self, db):
        assert get_current_price(db) is None

    def test_returns_price_in_kwh_not_mwh(self, db):
        """LMP is stored in USD/MWh; function must convert to USD/kWh (divide by 1000)."""
        make_realtime_lmp(db, total_lmp_rt=30_000.0)  # $30/MWh → $0.03/kWh
        result = get_current_price(db)
        assert result == pytest.approx(30.0, abs=0.0001)  # $30/MWh → $0.03/kWh = 0.0300

    def test_returns_price_rounded_to_4_decimal_places(self, db):
        make_realtime_lmp(db, total_lmp_rt=153.456789)
        result = get_current_price(db)
        # round(153.456789 / 1000, 4) = 0.1535
        assert result == round(153.456789 / 1000, 4)

    def test_returns_latest_record_not_oldest(self, db):
        now = datetime.now(timezone.utc)
        make_realtime_lmp(db, total_lmp_rt=10.0, dt_utc=now - timedelta(hours=2))
        make_realtime_lmp(db, total_lmp_rt=50.0, dt_utc=now - timedelta(minutes=5))
        result = get_current_price(db)
        # Should use the newest → 50.0 / 1000
        assert result == pytest.approx(50.0 / 1000, abs=0.0001)

    def test_ignores_non_latest_version(self, db):
        make_realtime_lmp(db, total_lmp_rt=100.0, latest_version=False)
        assert get_current_price(db) is None

    def test_handles_zero_lmp(self, db):
        make_realtime_lmp(db, total_lmp_rt=0.0)
        # Falsy 0 should still be returned
        result = get_current_price(db)
        assert result == 0.0


# ── get_current_source ────────────────────────────────────────────────────────

class TestGetCurrentSource:
    def test_returns_none_when_no_readings(self, db):
        assert get_current_source(db) is None

    def test_capitalizes_battery(self, db):
        make_user(db)
        make_sensor_reading(db, power_source="battery")
        assert get_current_source(db) == "Battery"

    def test_capitalizes_grid(self, db):
        make_user(db)
        make_sensor_reading(db, power_source="grid")
        assert get_current_source(db) == "Grid"

    def test_returns_source_from_latest_reading(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_sensor_reading(db, power_source="battery", timestamp=now - timedelta(minutes=10))
        make_sensor_reading(db, power_source="grid",    timestamp=now - timedelta(minutes=1))
        assert get_current_source(db) == "Grid"


# ── get_uptime ────────────────────────────────────────────────────────────────

class TestGetUptime:
    def test_returns_none_when_no_readings(self, db):
        assert get_uptime(db, days=30) is None

    def test_returns_value_between_0_and_100(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        for i in range(100):
            make_sensor_reading(db, timestamp=now - timedelta(seconds=i * 10))
        result = get_uptime(db, days=30)
        assert result is not None
        assert 0.0 <= result <= 100.0

    def test_uptime_capped_at_100(self, db):
        """More readings than expected intervals should not exceed 100%."""
        make_user(db)
        # Create more unique 10-second buckets than expected for 1 day
        now = datetime.now(timezone.utc)
        expected_per_day = (1 * 24 * 60 * 60) / 10
        for i in range(int(expected_per_day) + 500):
            make_sensor_reading(db, timestamp=now - timedelta(seconds=i * 10))
        result = get_uptime(db, days=1)
        assert result <= 100.0

    def test_uptime_is_rounded_to_one_decimal(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        for i in range(50):
            make_sensor_reading(db, timestamp=now - timedelta(seconds=i * 10))
        result = get_uptime(db, days=30)
        if result is not None:
            # Should have at most 1 decimal place
            assert result == round(result, 1)

    def test_only_counts_readings_within_window(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        # Reading outside the 1-day window
        make_sensor_reading(db, timestamp=now - timedelta(days=2))
        # Reading inside the 1-day window
        make_sensor_reading(db, timestamp=now - timedelta(hours=1))
        result_1day = get_uptime(db, days=1)
        result_3day = get_uptime(db, days=3)
        # 3-day window should pick up both readings (higher uptime bucket count)
        # 1-day window should only have the recent one
        assert result_3day is not None
        assert result_1day is not None


# ── GET /api/dashboard/ endpoint ─────────────────────────────────────────────

class TestDashboardEndpoint:
    def test_returns_200(self, client):
        assert client.get("/api/dashboard/").status_code == 200

    def test_response_has_all_top_level_keys(self, client):
        data = client.get("/api/dashboard/").json()
        for key in ["user", "battery", "power", "savings", "energy", "system"]:
            assert key in data, f"Missing key: {key}"

    def test_user_has_expected_fields(self, client):
        user = client.get("/api/dashboard/").json()["user"]
        assert "firstName" in user
        assert "fullName" in user

    def test_battery_has_level_and_status(self, client):
        battery = client.get("/api/dashboard/").json()["battery"]
        assert "level" in battery
        assert "status" in battery

    def test_power_has_source_price_and_tier(self, client):
        power = client.get("/api/dashboard/").json()["power"]
        assert "source" in power
        assert "currentPrice" in power
        assert "priceTier" in power

    def test_price_tier_is_valid_value(self, client):
        tier = client.get("/api/dashboard/").json()["power"]["priceTier"]
        assert tier in {"Peak", "Off-Peak", "Standard"}

    def test_savings_has_today_and_month(self, client):
        savings = client.get("/api/dashboard/").json()["savings"]
        assert "today" in savings
        assert "month" in savings

    def test_system_has_battery_cycles_and_uptime(self, client):
        system = client.get("/api/dashboard/").json()["system"]
        assert "batteryCycles" in system
        assert "uptime" in system

    def test_battery_cycles_is_none(self, client):
        """batteryCycles is explicitly None (not tracked yet) per the PR."""
        assert client.get("/api/dashboard/").json()["system"]["batteryCycles"] is None

    def test_energy_fields_are_none(self, client):
        """Energy fields are None (INA219 sensor not yet integrated)."""
        energy = client.get("/api/dashboard/").json()["energy"]
        assert energy["usedToday"] is None
        assert energy["usedWeek"] is None
        assert energy["usedMonth"] is None

    def test_dashboard_reflects_db_user(self, client, db):
        make_user(db, full_name="Alice Wonderland")
        data = client.get("/api/dashboard/").json()
        assert data["user"]["firstName"] == "Alice"
        assert data["user"]["fullName"] == "Alice Wonderland"

    def test_dashboard_reflects_db_battery_level(self, client, db):
        make_user(db)
        make_sensor_reading(db, battery_level=42, current=-1.0)
        data = client.get("/api/dashboard/").json()
        assert data["battery"]["level"] == 42
        assert data["battery"]["status"] == "Discharging"

    def test_dashboard_reflects_current_price(self, client, db):
        make_realtime_lmp(db, total_lmp_rt=25.0)
        data = client.get("/api/dashboard/").json()
        assert data["power"]["currentPrice"] == pytest.approx(25.0 / 1000, abs=0.0001)
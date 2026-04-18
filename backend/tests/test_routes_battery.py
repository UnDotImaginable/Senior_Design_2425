"""
Unit and integration tests for routes/battery.py

Covers the new helper functions introduced in this PR:
  - get_battery_level(db)
  - get_battery_status(db)
  - get_recent_activity(db, limit)
And the updated GET /api/battery/ endpoint.
"""
import sys
import os
from datetime import datetime, timezone, timedelta

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from tests.conftest import make_user, make_sensor_reading, make_switch_event
from routes.battery import get_battery_level, get_battery_status, get_recent_activity


# ── get_battery_level ─────────────────────────────────────────────────────────

class TestGetBatteryLevel:
    def test_returns_none_when_no_readings(self, db):
        assert get_battery_level(db) is None

    def test_returns_battery_level_from_latest_reading(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=82)
        assert get_battery_level(db) == 82

    def test_returns_latest_reading_when_multiple_exist(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_sensor_reading(db, battery_level=60, timestamp=now - timedelta(minutes=5))
        make_sensor_reading(db, battery_level=75, timestamp=now - timedelta(minutes=1))
        assert get_battery_level(db) == 75

    def test_returns_none_when_table_empty(self, db):
        # No user, no readings — count check should short-circuit to None
        assert get_battery_level(db) is None

    def test_returns_zero_battery_level(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=0)
        # battery_level=0 is falsy but should be returned as 0, not None
        assert get_battery_level(db) == 0

    def test_returns_full_battery_level(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=100)
        assert get_battery_level(db) == 100


# ── get_battery_status ────────────────────────────────────────────────────────

class TestGetBatteryStatus:
    def test_returns_unknown_when_no_readings(self, db):
        assert get_battery_status(db) == "Unknown"

    def test_returns_full_when_battery_level_100(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=100, current=-1.0)
        # Should return "Full" regardless of current
        assert get_battery_status(db) == "Full"

    def test_returns_unknown_when_current_is_none(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=75, current=None)
        assert get_battery_status(db) == "Unknown"

    def test_returns_charging_when_current_positive(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=50, current=2.5)
        assert get_battery_status(db) == "Charging"

    def test_returns_discharging_when_current_negative(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=50, current=-2.5)
        assert get_battery_status(db) == "Discharging"

    def test_returns_idle_when_current_zero(self, db):
        make_user(db)
        make_sensor_reading(db, battery_level=50, current=0.0)
        assert get_battery_status(db) == "Idle"

    def test_uses_most_recent_reading(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_sensor_reading(db, battery_level=50, current=-2.0, timestamp=now - timedelta(minutes=10))
        make_sensor_reading(db, battery_level=55, current=1.5, timestamp=now - timedelta(minutes=1))
        assert get_battery_status(db) == "Charging"


# ── get_recent_activity ───────────────────────────────────────────────────────

class TestGetRecentActivity:
    def test_returns_empty_list_when_no_events(self, db):
        assert get_recent_activity(db) == []

    def test_battery_switch_has_correct_action_and_icon(self, db):
        make_user(db)
        make_switch_event(db, switched_to="battery", reason="Peak rate detected")
        activity = get_recent_activity(db)
        assert len(activity) == 1
        assert activity[0]["action"] == "SWITCHED TO BATTERY POWER"
        assert activity[0]["icon"] == "🔋"
        assert activity[0]["details"] == "Peak rate detected"

    def test_grid_switch_has_correct_action_and_icon(self, db):
        make_user(db)
        make_switch_event(db, switched_to="grid", reason="Off-peak rate")
        activity = get_recent_activity(db)
        assert len(activity) == 1
        assert activity[0]["action"] == "SWITCHED TO GRID POWER"
        assert activity[0]["icon"] == "🔌"
        assert activity[0]["details"] == "Off-peak rate"

    def test_none_reason_shows_default_message(self, db):
        make_user(db)
        make_switch_event(db, switched_to="battery", reason=None)
        activity = get_recent_activity(db)
        assert activity[0]["details"] == "No reason provided"

    def test_activity_includes_timestamp_iso_string(self, db):
        make_user(db)
        make_switch_event(db, switched_to="grid")
        activity = get_recent_activity(db)
        # Should be a valid ISO-formatted string
        ts = activity[0]["timestamp"]
        assert isinstance(ts, str)
        # Should be parseable
        datetime.fromisoformat(ts)

    def test_limit_parameter_respected(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        for i in range(15):
            make_switch_event(db, switched_to="battery", timestamp=now - timedelta(minutes=i))
        activity = get_recent_activity(db, limit=5)
        assert len(activity) == 5

    def test_default_limit_is_10(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        for i in range(15):
            make_switch_event(db, switched_to="grid", timestamp=now - timedelta(minutes=i))
        activity = get_recent_activity(db)
        assert len(activity) == 10

    def test_activity_is_ordered_most_recent_first(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_switch_event(db, switched_to="grid",    reason="first",  timestamp=now - timedelta(hours=2))
        make_switch_event(db, switched_to="battery", reason="second", timestamp=now - timedelta(hours=1))
        make_switch_event(db, switched_to="grid",    reason="third",  timestamp=now - timedelta(minutes=5))
        activity = get_recent_activity(db)
        assert activity[0]["details"] == "third"
        assert activity[1]["details"] == "second"
        assert activity[2]["details"] == "first"


# ── GET /api/battery/ endpoint ────────────────────────────────────────────────

class TestBatteryEndpoint:
    def test_endpoint_returns_200(self, client):
        response = client.get("/api/battery/")
        assert response.status_code == 200

    def test_response_has_status_and_recent_activity_keys(self, client):
        data = client.get("/api/battery/").json()
        assert "status" in data
        assert "recentActivity" in data

    def test_status_has_required_fields(self, client):
        status = client.get("/api/battery/").json()["status"]
        assert "level" in status
        assert "status" in status
        assert "capacity" in status
        assert "health" in status

    def test_level_is_none_when_no_readings(self, client):
        data = client.get("/api/battery/").json()
        assert data["status"]["level"] is None

    def test_level_reflects_db_value(self, client, db):
        make_user(db)
        make_sensor_reading(db, battery_level=65, current=-1.0)
        data = client.get("/api/battery/").json()
        assert data["status"]["level"] == 65

    def test_status_reflects_db_value(self, client, db):
        make_user(db)
        make_sensor_reading(db, battery_level=50, current=1.0)
        data = client.get("/api/battery/").json()
        assert data["status"]["status"] == "Charging"

    def test_recent_activity_empty_when_no_events(self, client):
        data = client.get("/api/battery/").json()
        assert data["recentActivity"] == []

    def test_recent_activity_populated_from_db(self, client, db):
        make_user(db)
        make_switch_event(db, switched_to="battery", reason="Test reason")
        data = client.get("/api/battery/").json()
        assert len(data["recentActivity"]) == 1
        assert data["recentActivity"][0]["action"] == "SWITCHED TO BATTERY POWER"

    def test_history_limit_query_param(self, client, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        for i in range(8):
            make_switch_event(db, switched_to="grid", timestamp=now - timedelta(minutes=i))
        data = client.get("/api/battery/?history_limit=3").json()
        assert len(data["recentActivity"]) == 3
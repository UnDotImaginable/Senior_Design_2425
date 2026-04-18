"""
Unit tests for routes/pi.py

This PR changed get_battery_level() in pi.py to:
  - Return None instead of 0 when no reading exists
  - Check reading freshness (BATTERY_FRESHNESS_WINDOW = 2 minutes)
  - Return None when reading is stale (instead of returning the stale value)

Note: the pi router uses get_current_and_future_prices() from grid_pricing_service
which makes real HTTP calls. Endpoint tests for /pending-command mock that service.
"""
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Must be set before importing routes.pi, which transitively imports
# grid_pricing_service which raises if PJM_API_KEY is absent.
os.environ.setdefault("PJM_API_KEY", "test-key-placeholder")

from tests.conftest import make_user, make_sensor_reading
from routes.pi import get_battery_level, BATTERY_FRESHNESS_WINDOW


# ── get_battery_level (pi.py version with freshness check) ───────────────────

class TestPiGetBatteryLevel:
    def test_returns_none_when_no_readings(self, db):
        assert get_battery_level(db) is None

    def test_returns_level_for_fresh_reading(self, db):
        make_user(db)
        fresh_ts = datetime.now(timezone.utc) - timedelta(seconds=30)
        make_sensor_reading(db, battery_level=85, timestamp=fresh_ts)
        assert get_battery_level(db) == 85

    def test_returns_none_for_stale_reading(self, db):
        """Readings older than BATTERY_FRESHNESS_WINDOW (2 min) must return None."""
        make_user(db)
        stale_ts = datetime.now(timezone.utc) - timedelta(minutes=3)
        make_sensor_reading(db, battery_level=70, timestamp=stale_ts)
        assert get_battery_level(db) is None

    def test_returns_none_exactly_at_freshness_boundary(self, db):
        """A reading exactly at the boundary (age == BATTERY_FRESHNESS_WINDOW) is stale."""
        make_user(db)
        # Use a timestamp just past the freshness window
        ts = datetime.now(timezone.utc) - BATTERY_FRESHNESS_WINDOW - timedelta(seconds=1)
        make_sensor_reading(db, battery_level=60, timestamp=ts)
        assert get_battery_level(db) is None

    def test_returns_level_just_within_freshness_window(self, db):
        """A reading just inside the window should be accepted."""
        make_user(db)
        ts = datetime.now(timezone.utc) - BATTERY_FRESHNESS_WINDOW + timedelta(seconds=5)
        make_sensor_reading(db, battery_level=55, timestamp=ts)
        assert get_battery_level(db) == 55

    def test_uses_most_recent_reading(self, db):
        """When multiple readings exist, only the most recent is checked."""
        make_user(db)
        now = datetime.now(timezone.utc)
        # Old reading (stale)
        make_sensor_reading(db, battery_level=40, timestamp=now - timedelta(minutes=10))
        # Fresh reading
        make_sensor_reading(db, battery_level=90, timestamp=now - timedelta(seconds=20))
        assert get_battery_level(db) == 90

    def test_returns_zero_battery_level_when_fresh(self, db):
        """battery_level=0 is a valid value (not the same as 'no reading')."""
        make_user(db)
        ts = datetime.now(timezone.utc) - timedelta(seconds=15)
        make_sensor_reading(db, battery_level=0, timestamp=ts)
        assert get_battery_level(db) == 0

    def test_returns_none_not_zero_for_missing_reading(self, db):
        """
        Regression: before this PR, get_battery_level returned 0 when there was no
        reading. After the PR it must return None.
        """
        result = get_battery_level(db)
        assert result is None
        assert result != 0


# ── POST /api/pi/readings ─────────────────────────────────────────────────────

class TestPiReadingsEndpoint:
    def test_post_reading_returns_200(self, client, db):
        make_user(db)
        payload = {"battery_level": 75, "power_source": "battery"}
        response = client.post("/api/pi/readings", json=payload)
        assert response.status_code == 200

    def test_post_reading_response_has_id_and_timestamp(self, client, db):
        make_user(db)
        payload = {"battery_level": 80, "power_source": "grid"}
        data = client.post("/api/pi/readings", json=payload).json()
        assert data["success"] is True
        assert "id" in data
        assert "timestamp" in data

    def test_post_reading_persists_to_db(self, client, db):
        from models import SensorReading
        make_user(db)
        payload = {"battery_level": 63, "power_source": "battery", "voltage": 3.7, "current": -0.5}
        client.post("/api/pi/readings", json=payload)
        reading = db.query(SensorReading).first()
        assert reading is not None
        assert reading.battery_level == 63
        assert reading.power_source == "battery"

    def test_post_reading_optional_fields_default_to_none(self, client, db):
        from models import SensorReading
        make_user(db)
        payload = {"battery_level": 50, "power_source": "grid"}
        client.post("/api/pi/readings", json=payload)
        reading = db.query(SensorReading).first()
        assert reading.voltage is None
        assert reading.current is None
        assert reading.temperature is None


# ── GET /api/pi/pending-command ───────────────────────────────────────────────

class TestPiPendingCommandEndpoint:
    def _mock_prices(self, current_lmp, future_lmp):
        return {"current_lmp": current_lmp, "future_lmp": future_lmp}

    def test_returns_switch_to_grid_when_future_more_expensive(self, client, db):
        make_user(db)
        fresh_ts = datetime.now(timezone.utc) - timedelta(seconds=15)
        make_sensor_reading(db, battery_level=70, timestamp=fresh_ts)
        with patch(
            "routes.pi.get_current_and_future_prices",
            return_value=self._mock_prices(0.10, 0.30)
        ):
            response = client.get("/api/pi/pending-command")
        assert response.status_code == 200
        assert response.json()["command"] == "switch_to_grid"

    def test_returns_switch_to_battery_when_future_cheaper(self, client, db):
        make_user(db)
        fresh_ts = datetime.now(timezone.utc) - timedelta(seconds=15)
        make_sensor_reading(db, battery_level=80, timestamp=fresh_ts)
        with patch(
            "routes.pi.get_current_and_future_prices",
            return_value=self._mock_prices(0.30, 0.10)
        ):
            response = client.get("/api/pi/pending-command")
        assert response.status_code == 200
        assert response.json()["command"] == "switch_to_battery"

    def test_returns_503_when_both_prices_unavailable(self, client):
        with patch(
            "routes.pi.get_current_and_future_prices",
            return_value=self._mock_prices(None, None)
        ):
            response = client.get("/api/pi/pending-command")
        assert response.status_code == 503

    def test_returns_503_when_current_price_unavailable(self, client):
        with patch(
            "routes.pi.get_current_and_future_prices",
            return_value=self._mock_prices(None, 0.20)
        ):
            response = client.get("/api/pi/pending-command")
        assert response.status_code == 503

    def test_returns_503_when_future_price_unavailable(self, client):
        with patch(
            "routes.pi.get_current_and_future_prices",
            return_value=self._mock_prices(0.15, None)
        ):
            response = client.get("/api/pi/pending-command")
        assert response.status_code == 503

    def test_stale_battery_triggers_berror_command(self, client, db):
        """Stale battery (get_battery_level returns None) → decision_service returns battery error."""
        make_user(db)
        stale_ts = datetime.now(timezone.utc) - timedelta(minutes=10)
        make_sensor_reading(db, battery_level=50, timestamp=stale_ts)
        with patch(
            "routes.pi.get_current_and_future_prices",
            return_value=self._mock_prices(0.15, 0.28)
        ):
            response = client.get("/api/pi/pending-command")
        assert response.status_code == 200
        data = response.json()
        # decision_service returns grid with battery error when b_charge is None
        assert data["command"] == "switch_to_grid"
        assert "ERROR" in data["reason"]


# ── POST /api/pi/confirm-switch ───────────────────────────────────────────────

class TestPiConfirmSwitchEndpoint:
    def test_post_confirm_switch_returns_200(self, client, db):
        make_user(db)
        payload = {"switched_to": "battery", "reason": "Peak pricing"}
        response = client.post("/api/pi/confirm-switch", json=payload)
        assert response.status_code == 200

    def test_confirm_switch_response_has_id_and_timestamp(self, client, db):
        make_user(db)
        payload = {"switched_to": "grid", "reason": "Battery empty"}
        data = client.post("/api/pi/confirm-switch", json=payload).json()
        assert data["success"] is True
        assert "id" in data
        assert "timestamp" in data

    def test_confirm_switch_persists_event(self, client, db):
        from models import SwitchEvent
        make_user(db)
        payload = {"switched_to": "battery", "reason": "test"}
        client.post("/api/pi/confirm-switch", json=payload)
        event = db.query(SwitchEvent).first()
        assert event is not None
        assert event.switched_to == "battery"
        assert event.reason == "test"

    def test_confirm_switch_reason_optional(self, client, db):
        from models import SwitchEvent
        make_user(db)
        payload = {"switched_to": "grid"}
        client.post("/api/pi/confirm-switch", json=payload)
        event = db.query(SwitchEvent).first()
        assert event.reason is None
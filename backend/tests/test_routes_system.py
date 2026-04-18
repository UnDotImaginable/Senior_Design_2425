"""
Unit and integration tests for routes/system.py

Covers the new code introduced in this PR:
  - get_latest_pi_status(db)
  - pi_active logic (< 300 seconds)
  - GET /api/system/ endpoint (all fields now sourced from PiStatus model)
"""
import sys
import os
from datetime import datetime, timezone, timedelta

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from tests.conftest import make_user, make_sensor_reading, make_pi_status
from routes.system import get_latest_pi_status


# ── get_latest_pi_status ──────────────────────────────────────────────────────

class TestGetLatestPiStatus:
    def test_returns_none_when_no_records(self, db):
        assert get_latest_pi_status(db) is None

    def test_returns_single_record(self, db):
        make_user(db)
        ps = make_pi_status(db, device_id="RPi-4B-TEST")
        result = get_latest_pi_status(db)
        assert result is not None
        assert result.device_id == "RPi-4B-TEST"

    def test_returns_most_recent_record(self, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        make_pi_status(db, device_id="old-pi",    timestamp=now - timedelta(hours=2))
        make_pi_status(db, device_id="recent-pi", timestamp=now - timedelta(minutes=1))
        result = get_latest_pi_status(db)
        assert result.device_id == "recent-pi"

    def test_filters_by_user_id_1(self, db):
        """Only user_id=1 records should be returned."""
        make_user(db, user_id=1, email="user1@test.com")
        make_user(db, user_id=2, email="user2@test.com")
        now = datetime.now(timezone.utc)
        make_pi_status(db, user_id=2, device_id="other-user-pi", timestamp=now)
        # No pi_status for user 1 → should return None
        result = get_latest_pi_status(db)
        assert result is None


# ── pi_active determination ───────────────────────────────────────────────────

class TestSystemPiActive:
    """
    The pi_active flag is True when the latest PiStatus timestamp is < 300s old.
    We test this via the endpoint response.
    """

    def test_pi_active_when_recent_status(self, client, db):
        make_user(db)
        recent_ts = datetime.now(timezone.utc) - timedelta(seconds=60)
        make_pi_status(db, timestamp=recent_ts)
        data = client.get("/api/system/").json()
        assert data["health"]["raspberryPi"] == "Active"

    def test_pi_inactive_when_stale_status(self, client, db):
        make_user(db)
        stale_ts = datetime.now(timezone.utc) - timedelta(seconds=400)
        make_pi_status(db, timestamp=stale_ts)
        data = client.get("/api/system/").json()
        assert data["health"]["raspberryPi"] == "Inactive"

    def test_pi_inactive_when_no_status(self, client):
        data = client.get("/api/system/").json()
        assert data["health"]["raspberryPi"] == "Inactive"

    def test_pi_inactive_at_exactly_300_seconds(self, client, db):
        """Boundary: exactly 300 seconds is NOT < 300, so should be Inactive."""
        make_user(db)
        ts = datetime.now(timezone.utc) - timedelta(seconds=300)
        make_pi_status(db, timestamp=ts)
        data = client.get("/api/system/").json()
        assert data["health"]["raspberryPi"] == "Inactive"

    def test_pi_active_at_299_seconds(self, client, db):
        make_user(db)
        ts = datetime.now(timezone.utc) - timedelta(seconds=299)
        make_pi_status(db, timestamp=ts)
        data = client.get("/api/system/").json()
        assert data["health"]["raspberryPi"] == "Active"


# ── GET /api/system/ endpoint ─────────────────────────────────────────────────

class TestSystemEndpoint:
    def test_returns_200(self, client):
        assert client.get("/api/system/").status_code == 200

    def test_response_has_health_and_device_keys(self, client):
        data = client.get("/api/system/").json()
        assert "health" in data
        assert "device" in data

    def test_health_has_required_fields(self, client):
        health = client.get("/api/system/").json()["health"]
        for field in ["system", "apiConnection", "raspberryPi", "lastUpdate", "uptime"]:
            assert field in health, f"Missing field: {field}"

    def test_device_has_required_fields(self, client):
        device = client.get("/api/system/").json()["device"]
        for field in ["deviceId", "firmware", "ipAddress", "cpu", "memory"]:
            assert field in device, f"Missing field: {field}"

    def test_memory_has_used_and_total(self, client):
        memory = client.get("/api/system/").json()["device"]["memory"]
        assert "used" in memory
        assert "total" in memory

    def test_system_is_always_online(self, client):
        assert client.get("/api/system/").json()["health"]["system"] == "Online"

    def test_api_connection_is_always_connected(self, client):
        assert client.get("/api/system/").json()["health"]["apiConnection"] == "Connected"

    def test_all_device_fields_none_when_no_pi_status(self, client):
        device = client.get("/api/system/").json()["device"]
        assert device["deviceId"] is None
        assert device["firmware"] is None
        assert device["ipAddress"] is None
        assert device["cpu"] is None
        assert device["memory"]["used"] is None
        assert device["memory"]["total"] is None

    def test_last_update_none_when_no_pi_status(self, client):
        assert client.get("/api/system/").json()["health"]["lastUpdate"] is None

    def test_device_fields_populated_from_pi_status(self, client, db):
        make_user(db)
        make_pi_status(
            db,
            device_id="RPi-4B-A7F2",
            firmware="v2.0.0",
            ip_address="10.0.0.5",
            cpu_percent=42.0,
            memory_used_gb=1.5,
            memory_total_gb=4.0,
            timestamp=datetime.now(timezone.utc) - timedelta(seconds=30),
        )
        data = client.get("/api/system/").json()
        device = data["device"]
        assert device["deviceId"] == "RPi-4B-A7F2"
        assert device["firmware"] == "v2.0.0"
        assert device["ipAddress"] == "10.0.0.5"
        assert device["cpu"] == 42.0
        assert device["memory"]["used"] == 1.5
        assert device["memory"]["total"] == 4.0

    def test_last_update_is_iso_string_when_pi_present(self, client, db):
        make_user(db)
        make_pi_status(db, timestamp=datetime.now(timezone.utc) - timedelta(seconds=30))
        last_update = client.get("/api/system/").json()["health"]["lastUpdate"]
        assert isinstance(last_update, str)
        datetime.fromisoformat(last_update)  # Should be parseable

    def test_uptime_none_when_no_sensor_readings(self, client):
        assert client.get("/api/system/").json()["health"]["uptime"] is None

    def test_uptime_present_when_sensor_readings_exist(self, client, db):
        make_user(db)
        now = datetime.now(timezone.utc)
        for i in range(30):
            make_sensor_reading(db, timestamp=now - timedelta(seconds=i * 10))
        uptime = client.get("/api/system/").json()["health"]["uptime"]
        assert uptime is not None
        assert 0.0 <= uptime <= 100.0
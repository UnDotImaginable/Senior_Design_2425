"""
Tests for new/modified models introduced in this PR:
  - models/pi_status.py (new model)
  - models/user.py (pi_status relationship added)
  - models/__init__.py (PiStatus export added)
"""
import sys
import os
from datetime import datetime, timezone

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from tests.conftest import make_user, make_pi_status


# ── PiStatus model ────────────────────────────────────────────────────────────

class TestPiStatusModel:
    def test_can_create_pi_status_record(self, db):
        make_user(db)
        from models import PiStatus
        ps = PiStatus(
            user_id=1,
            device_id="RPi-4B-A7F2",
            firmware="v1.2.4",
            ip_address="192.168.1.142",
            cpu_percent=24.0,
            memory_used_gb=1.2,
            memory_total_gb=4.0,
        )
        db.add(ps)
        db.commit()
        db.refresh(ps)
        assert ps.id is not None

    def test_table_name_is_pi_status(self):
        from models import PiStatus
        assert PiStatus.__tablename__ == "pi_status"

    def test_required_user_id(self, db):
        from models import PiStatus
        from sqlalchemy.exc import IntegrityError
        ps = PiStatus()  # No user_id
        db.add(ps)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_optional_fields_default_to_none(self, db):
        make_user(db)
        from models import PiStatus
        ps = PiStatus(user_id=1)
        db.add(ps)
        db.commit()
        db.refresh(ps)
        assert ps.device_id is None
        assert ps.firmware is None
        assert ps.ip_address is None
        assert ps.cpu_percent is None
        assert ps.memory_used_gb is None
        assert ps.memory_total_gb is None

    def test_timestamp_auto_populated(self, db):
        make_user(db)
        from models import PiStatus
        ps = PiStatus(user_id=1)
        db.add(ps)
        db.commit()
        db.refresh(ps)
        assert ps.timestamp is not None

    def test_repr_format(self, db):
        make_user(db)
        from models import PiStatus
        ps = PiStatus(
            user_id=1,
            device_id="RPi-TEST",
            cpu_percent=55.5,
        )
        # Set timestamp explicitly so repr is deterministic
        ps.timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        db.add(ps)
        db.commit()
        db.refresh(ps)
        r = repr(ps)
        assert "PiStatus" in r
        assert "RPi-TEST" in r
        assert "55.5" in r

    def test_repr_with_none_fields(self, db):
        make_user(db)
        from models import PiStatus
        ps = PiStatus(user_id=1)
        db.add(ps)
        db.commit()
        db.refresh(ps)
        # Should not raise
        r = repr(ps)
        assert "PiStatus" in r

    def test_all_fields_persist_and_round_trip(self, db):
        make_user(db)
        ts = datetime(2024, 6, 1, 10, 0, 0)  # naive, as stored by SQLite
        from models import PiStatus
        ps = PiStatus(
            user_id=1,
            device_id="RPi-UNIT",
            firmware="v3.0.0",
            ip_address="10.0.0.1",
            cpu_percent=12.3,
            memory_used_gb=0.8,
            memory_total_gb=2.0,
            timestamp=ts,
        )
        db.add(ps)
        db.commit()

        fetched = db.query(PiStatus).filter(PiStatus.id == ps.id).one()
        assert fetched.device_id == "RPi-UNIT"
        assert fetched.firmware == "v3.0.0"
        assert fetched.ip_address == "10.0.0.1"
        assert fetched.cpu_percent == pytest.approx(12.3)
        assert fetched.memory_used_gb == pytest.approx(0.8)
        assert fetched.memory_total_gb == pytest.approx(2.0)


# ── User.pi_status relationship ───────────────────────────────────────────────

class TestUserPiStatusRelationship:
    def test_user_pi_status_relationship_is_accessible(self, db):
        user = make_user(db)
        make_pi_status(db, user_id=user.id, device_id="RPi-REL-TEST")
        db.refresh(user)
        assert len(user.pi_status) == 1
        assert user.pi_status[0].device_id == "RPi-REL-TEST"

    def test_user_pi_status_empty_when_no_records(self, db):
        user = make_user(db)
        db.refresh(user)
        assert user.pi_status == []

    def test_multiple_pi_statuses_linked_to_user(self, db):
        user = make_user(db)
        make_pi_status(db, user_id=user.id, device_id="Pi-1")
        make_pi_status(db, user_id=user.id, device_id="Pi-2")
        db.refresh(user)
        assert len(user.pi_status) == 2

    def test_back_populates_from_pi_status_to_user(self, db):
        user = make_user(db)
        ps = make_pi_status(db, user_id=user.id)
        db.refresh(ps)
        assert ps.user is not None
        assert ps.user.id == user.id


# ── models/__init__.py exports ────────────────────────────────────────────────

class TestModelsInit:
    def test_pi_status_importable_from_models(self):
        from models import PiStatus
        assert PiStatus is not None

    def test_pi_status_in_all(self):
        import models
        assert "PiStatus" in models.__all__

    def test_existing_exports_still_present(self):
        """Ensure adding PiStatus didn't remove any existing exports."""
        import models
        for name in ["User", "SensorReading", "SwitchEvent", "DayAheadLMP", "ItscedLMP", "RealtimeLMP"]:
            assert name in models.__all__, f"Missing from __all__: {name}"
            assert hasattr(models, name), f"Not importable: {name}"
"""
Shared pytest fixtures for PowerOptim backend tests.
Uses an in-memory SQLite database so tests never touch the production file.
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# grid_pricing_service raises at import time if PJM_API_KEY is absent.
# Set a dummy value so the module can be imported in the test environment.
os.environ.setdefault("PJM_API_KEY", "test-key-placeholder")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Make sure backend/ is on the import path when tests run from either
# the repo root or from backend/tests/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ── database ──────────────────────────────────────────────────────────────────

from database.database import Base, get_db
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool forces all sessions (including those spawned inside TestClient's
# ASGI runner) to reuse the same underlying connection.  This is required for
# SQLite :memory: databases, which are per-connection by default.
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def create_tables():
    """Create all tables before each test and drop them afterwards."""
    # Import all models so their metadata is registered on Base before create_all
    import models  # noqa: F401 – side-effect: registers all model classes
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Yield a fresh SQLAlchemy session backed by the in-memory test database."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ── FastAPI test client ────────────────────────────────────────────────────────

@pytest.fixture
def client(db):
    """
    Return a Starlette TestClient wired to the test DB.
    The get_db dependency is overridden so routes use the same in-memory session.
    """
    # Import app here (after sys.path is set) to avoid scheduler/startup side-effects
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from routes import battery, cost, dashboard, energy, system, pi as pi_routes
    from fastapi import APIRouter

    test_app = FastAPI()
    api_router = APIRouter(prefix="/api")
    api_router.include_router(dashboard.router)
    api_router.include_router(battery.router)
    api_router.include_router(cost.router)
    api_router.include_router(energy.router)
    api_router.include_router(system.router)
    api_router.include_router(pi_routes.router)
    test_app.include_router(api_router)

    def override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle managed by the `db` fixture

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as c:
        yield c


# ── Data helpers ───────────────────────────────────────────────────────────────

def make_user(db, user_id=1, full_name="John Doe", email="john@example.com"):
    from models import User
    user = User(id=user_id, email=email, hashed_password="hash", full_name=full_name, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_sensor_reading(
    db,
    user_id=1,
    battery_level=75,
    power_source="battery",
    current=None,
    voltage=None,
    temperature=None,
    timestamp=None,
):
    from models import SensorReading
    r = SensorReading(
        user_id=user_id,
        battery_level=battery_level,
        power_source=power_source,
        current=current,
        voltage=voltage,
        temperature=temperature,
    )
    if timestamp is not None:
        r.timestamp = timestamp
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def make_switch_event(db, user_id=1, switched_to="battery", reason=None, timestamp=None):
    from models import SwitchEvent
    e = SwitchEvent(user_id=user_id, switched_to=switched_to, reason=reason)
    if timestamp is not None:
        e.timestamp = timestamp
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def make_realtime_lmp(db, total_lmp_rt=30.0, latest_version=True, dt_utc=None):
    from models import RealtimeLMP
    if dt_utc is None:
        dt_utc = datetime.now(timezone.utc) - timedelta(minutes=1)
    lmp = RealtimeLMP(
        datetime_beginning_utc=dt_utc,
        datetime_beginning_ept=dt_utc,
        pricing_node_id=1,
        pricing_node_name="TEST_NODE",
        pricing_node_type="HUB",
        voltage="500",
        equipment="TEST",
        transmission_zone="ZONE",
        system_energy_price_rt=25.0,
        total_lmp_rt=total_lmp_rt,
        congestion_price_rt=3.0,
        marginal_loss_price_rt=2.0,
        latest_version=latest_version,
        version_number=1,
        valid_until=dt_utc + timedelta(minutes=5),
    )
    db.add(lmp)
    db.commit()
    db.refresh(lmp)
    return lmp


def make_day_ahead_lmp(db, total_lmp_da=40.0, latest_version=True, dt_utc=None):
    from models import DayAheadLMP
    if dt_utc is None:
        dt_utc = datetime.now(timezone.utc) + timedelta(hours=2)
    lmp = DayAheadLMP(
        datetime_beginning_utc=dt_utc,
        datetime_beginning_ept=dt_utc,
        pricing_node_id=1,
        pricing_node_name="TEST_NODE",
        pricing_node_type="HUB",
        voltage="500",
        equipment="TEST",
        transmission_zone="ZONE",
        system_energy_price_da=35.0,
        total_lmp_da=total_lmp_da,
        congestion_price_da=3.0,
        marginal_loss_price_da=2.0,
        latest_version=latest_version,
        version_number=1,
        valid_until=dt_utc + timedelta(hours=1),
    )
    db.add(lmp)
    db.commit()
    db.refresh(lmp)
    return lmp


def make_pi_status(
    db,
    user_id=1,
    device_id="RPi-4B-A7F2",
    firmware="v1.2.4",
    ip_address="192.168.1.142",
    cpu_percent=24.0,
    memory_used_gb=1.2,
    memory_total_gb=4.0,
    timestamp=None,
):
    from models import PiStatus
    ps = PiStatus(
        user_id=user_id,
        device_id=device_id,
        firmware=firmware,
        ip_address=ip_address,
        cpu_percent=cpu_percent,
        memory_used_gb=memory_used_gb,
        memory_total_gb=memory_total_gb,
    )
    if timestamp is not None:
        ps.timestamp = timestamp
    db.add(ps)
    db.commit()
    db.refresh(ps)
    return ps
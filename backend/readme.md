# Backend Work - Before Hardware Arrives

## ✅ What You Can Build Now (No Hardware Needed)

### 1. **Database Models** (High Priority)
Create your database schema in `models/`

**models/user.py:**
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**models/energy_reading.py:**
```python
class EnergyReading(Base):
    __tablename__ = "energy_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    power_source = Column(String)  # "grid" or "battery"
    energy_consumption = Column(Float)  # kWh
    electricity_price = Column(Float)  # $/kWh
    battery_level = Column(Integer)  # percentage
    cost = Column(Float)  # dollars
```

**models/battery_status.py:**
```python
class BatteryStatus(Base):
    __tablename__ = "battery_status"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(Integer)  # percentage
    voltage = Column(Float)  # volts
    current = Column(Float)  # amps
    temperature = Column(Float)  # celsius
    health = Column(Integer)  # percentage
    status = Column(String)  # "charging", "discharging", "idle"
    cycles = Column(Integer)  # total charge cycles
```

### 2. **Authentication System** (High Priority)
Build JWT authentication in `routes/auth.py`

**What to implement:**
- User registration endpoint
- Login endpoint (returns JWT token)
- Password hashing with bcrypt
- JWT token generation and verification
- Protected route decorator

**Why now?**
Your frontend needs this to test login functionality!

### 3. **Database Setup** (High Priority)
Create `database.py` in root:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./poweroptim.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. **Mock Data Service** (Medium Priority)
Create `services/mock_data.py`:

Generate realistic fake data that simulates what the Raspberry Pi will send:
- Hourly energy readings for past week
- Battery status changes over time
- Pricing data (simulating time-of-use rates)
- Power source switching events

**Why?**
So your frontend can display real-looking charts NOW, and you just swap the data source later!

### 5. **API Routes** (Medium Priority)
Organize endpoints in `routes/`:

**routes/dashboard.py:**
- GET /api/dashboard - Overview stats
- GET /api/recent-activity - Last 10 events

**routes/energy.py:**
- GET /api/energy/hourly?date=2024-01-15
- GET /api/energy/daily?start=2024-01&end=2024-02
- GET /api/energy/monthly

**routes/battery.py:**
- GET /api/battery/status - Current status
- GET /api/battery/history?hours=24
- GET /api/battery/health

**routes/pricing.py:**
- GET /api/pricing/current
- GET /api/pricing/forecast - Next 24 hours

### 6. **Configuration Management** (Low Priority)
Create `config.py`:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # App
    app_name: str = "PowerOptim"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./poweroptim.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Keys (for electricity pricing API)
    pricing_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 7. **Error Handling** (Low Priority)
Create `utils/exceptions.py`:

Custom exception handlers for common errors:
- User not found
- Invalid credentials
- Database connection errors
- External API failures

### 8. **Testing** (Medium Priority)
Create `tests/` folder:

Write tests for:
- Authentication endpoints
- Database models
- Mock data generation
- API response formats

**Why now?**
Catch bugs early, and hardware integration will be smoother!

### 9. **External API Integration** (Medium Priority)
Research and integrate electricity pricing API:

**Options:**
- EIA (Energy Information Administration) API
- Utility company API
- Mock pricing service

Create `services/pricing_service.py` to fetch real-time rates.

### 10. **Documentation** (Low Priority)
- Add docstrings to all functions
- Create API documentation beyond FastAPI's auto-docs
- Document database schema
- Create architecture diagrams

---

## 🎯 Recommended Order

**Week 1-2:**
1. ✅ Logging setup
2. Database models
3. Database setup
4. Mock data service

**Week 3-4:**
5. Authentication system
6. API routes (organized by feature)
7. Connect frontend to backend with mock data

**Week 5-6:**
8. Testing
9. External API integration
10. Error handling

**When hardware arrives:**
11. Create `services/raspberry_pi.py`
12. Swap mock data for real hardware data
13. Test and debug hardware integration

---

## 💡 Pro Tips

1. **Use Mock Data Liberally**
   - Don't wait for hardware
   - Frontend developers can build UI now
   - Just swap data source later

2. **Test with Postman/Thunder Client**
   - Test your endpoints as you build
   - Save example requests
   - Share with team

3. **Version Your Database Schema**
   - Use Alembic for migrations
   - Makes schema changes easier

4. **Document As You Go**
   - Future you will thank you
   - Teammates will thank you

5. **Git Branches**
   - One feature per branch
   - Merge to main when tested

---

## 📦 Dependencies to Add

```bash
# Database & ORM
pip install sqlalchemy alembic

# Authentication
pip install passlib[bcrypt] python-jose[cryptography]

# Environment variables
pip install python-dotenv

# Validation
pip install pydantic

# Testing
pip install pytest pytest-asyncio httpx

# After installing, update requirements.txt:
pip freeze > requirements.txt
```

---

## 🎓 Learning Resources

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/en/14/orm/
- **JWT Authentication**: https://fastapi.tiangolo.com/tutorial/security/
- **Testing FastAPI**: https://fastapi.tiangolo.com/tutorial/testing/
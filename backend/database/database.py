"""
Database configuration and session management for PowerOptim
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import get_logger

logger = get_logger(__name__)

# Database URL - SQLite for development
# For production, change to: postgresql://user:password@localhost/poweroptim
# MAKE SURE TO CHANGE THIS ONCE IT GOES UP TO AWS EC2
SQLALCHEMY_DATABASE_URL = "sqlite:///./poweroptim.db"

# Create database engine
# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def init_db():
    """
    Create all database tables
    Call this once when starting the app
    """
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def get_db():
    """
    Dependency function for FastAPI routes
    Provides a database session and closes it after use
    
    Usage in route:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
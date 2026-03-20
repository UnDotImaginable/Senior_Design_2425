"""
Energy usage routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from utils import get_logger
import random

logger = get_logger(__name__)

router = APIRouter(prefix="/energy", tags=["Energy"])


@router.get("/")
async def get_energy_data(db: Session = Depends(get_db)):
    """
    Get all energy usage data for the Energy page
    Returns summary stats and chart data for hourly and weekly usage
    """
    logger.info("Energy data requested")
    
    # TODO: Replace with real database queries
    # For now, return dummy data
    
    # Generate 24 hours of dummy data (0:00 to 23:00)
    hourly_usage = [
        {
            "hour": f"{i}:00",
            "usage": round(random.uniform(0.5, 2.5), 2)  # Random kWh between 0.5 and 2.5
        }
        for i in range(24)
    ]
    
    # Generate 7 days of dummy data (Mon-Sun)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_usage = [
        {
            "day": day,
            "usage": round(random.uniform(15.0, 25.0), 1)  # Random kWh between 15 and 25
        }
        for day in days
    ]
    
    energy_data = {
        "summary": {
            "today": 18.4,      # kWh
            "week": 124.8,      # kWh
            "month": 487.2      # kWh
        },
        "hourlyUsage": hourly_usage,
        "weeklyUsage": weekly_usage
    }
    
    logger.debug(f"Returning energy data with {len(hourly_usage)} hourly points and {len(weekly_usage)} daily points")
    
    return energy_data
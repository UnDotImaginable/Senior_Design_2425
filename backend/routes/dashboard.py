"""
Dashboard routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Get all dashboard overview data
    Returns everything needed to display the dashboard page
    """
    logger.info("Dashboard data requested")
    
    # For now, return dummy data
    dashboard_data = {
        "user": {
            "firstName": "John",
            "fullName": "John Doe"
        },
        "battery": {
            "level": 78,
            "status": "Discharging"
        },
        "power": {
            "source": "Battery",  # "Battery" or "Grid"
            "currentPrice": 0.28,
            "priceTier": "Peak"  # "Off-Peak", "Standard", "Peak"
        },
        "savings": {
            "today": 2.13,
            "month": 28.40
        },
        "energy": {
            "usedToday": 18.4,  # kWh
            "usedWeek": 124.8,
            "usedMonth": 487.2
        },
        "system": {
            "batteryCycles": 47,
            "uptime": 99.2  # percentage
        }
    }
    
    logger.debug(f"Returning dashboard data: {dashboard_data}")
    
    return dashboard_data
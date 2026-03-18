"""
Battery status routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/battery", tags=["Battery"])


@router.get("/")
async def get_battery_data(db: Session = Depends(get_db)):
    """
    Get battery status and recent activity
    Returns current battery metrics and switching history for battery page
    """
    logger.info("Battery data requested")
    
    # TODO: Replace with real database queries
    # For now, return dummy data
    
    battery_data = {
        "status": {
            "level": 78,                    # percentage
            "status": "Discharging",        # "Charging", "Discharging", "Idle", "Full"
            "capacity": 10.0,               # kWh
            "health": 98                    # percentage
        },
        "recentActivity": [
            {
                "action": "SWITCHED TO BATTERY POWER",
                "details": "Peak rate detected ($0.28/kWh)",
                "timestamp": "2h ago",
                "icon": "🔋"
            },
            {
                "action": "STARTED BATTERY CHARGING",
                "details": "Off-peak rate ($0.08/kWh)",
                "timestamp": "5h ago",
                "icon": "⚡"
            },
            {
                "action": "SWITCHED TO GRID POWER",
                "details": "Battery fully charged",
                "timestamp": "7h ago",
                "icon": "🔌"
            }
        ]
    }
    
    logger.debug(f"Returning battery data: level={battery_data['status']['level']}%, status={battery_data['status']['status']}")
    
    return battery_data
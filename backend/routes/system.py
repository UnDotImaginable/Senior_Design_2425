"""
System status routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/")
async def get_system_data(db: Session = Depends(get_db)):
    """
    Get system status and device information for the system tab
    Returns system health metrics and Raspberry Pi device info
    """
    logger.info("System data requested")
    
    # TODO: Replace with real system metrics from Raspberry Pi
    # For now, return dummy data
    
    system_data = {
        "health": {
            "system": "Online",
            "apiConnection": "Connected",
            "raspberryPi": "Active",
            "lastUpdate": "2 mins ago",
            "uptime": "15d 7h 23m"
        },
        "device": {
            "deviceId": "RPi-4B-A7F2",
            "firmware": "v1.2.4",
            "ipAddress": "192.168.1.142",
            "cpu": 24,              # percentage
            "memory": {
                "used": 1.2,        # GB
                "total": 4.0        # GB
            }
        }
    }
    
    logger.debug(f"Returning system data: system={system_data['health']['system']}, raspberryPi={system_data['health']['raspberryPi']}")
    
    return system_data
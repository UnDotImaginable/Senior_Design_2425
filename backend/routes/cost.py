"""
Cost and savings routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/cost", tags=["Cost"])


@router.get("/")
async def get_cost_data(db: Session = Depends(get_db)):
    """
    Get cost analysis and savings data for the cost tab
    Returns monthly cost comparison, pricing zones, and cost breakdown
    """
    logger.info("Cost data requested")
    
    # TODO: Replace with real database queries and calculations
    # For now, return dummy data
    
    # Generate 24 hours of pricing data
    # Off-peak (0-6): $0.08, Standard (6-17, 21-24): $0.15, Peak (17-21): $0.28
    pricing_zones = []
    for i in range(24):
        if 0 <= i < 6:
            price = 0.08  # Off-peak
        elif 17 <= i < 21:
            price = 0.28  # Peak
        else:
            price = 0.15  # Standard
        
        pricing_zones.append({
            "hour": f"{i}:00",
            "price": price
        })
    
    cost_data = {
        "monthlyCost": {
            "withSystem": 42.80,        # Estimated cost with PowerOptim
            "withoutSystem": 71.20,     # Grid-only estimate
            "savings": 28.40,           # Monthly savings
            "savingsPercentage": 40     # Percentage reduction
        },
        "pricingZones": pricing_zones,
        "breakdown": [
            {
                "category": "Peak Hours (Grid)",
                "description": "High-cost electricity usage",
                "cost": 18.20,
                "percentage": 42
            },
            {
                "category": "Off-Peak (Battery Charging)",
                "description": "Low-cost charging windows",
                "cost": 12.40,
                "percentage": 29
            },
            {
                "category": "Battery Usage",
                "description": "Stored energy deployment",
                "cost": 12.20,
                "percentage": 29
            }
        ]
    }
    
    logger.debug(f"Returning cost data: monthly savings=${cost_data['monthlyCost']['savings']}")
    
    return cost_data
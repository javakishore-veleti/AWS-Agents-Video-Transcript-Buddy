"""
Usage Routes - REST endpoints for usage tracking and billing.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from config.database import get_db
from services.usage_service import UsageService, PRICING
from api.models.response_models import BaseResponse
from api.dependencies.auth import get_current_user
from models.user import User
from models.subscription import TIERS

router = APIRouter()


@router.get(
    "/summary",
    response_model=BaseResponse,
    summary="Get usage summary",
    description="Get current month usage summary for the authenticated user"
)
async def get_usage_summary(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage summary for current user.
    
    - **month**: Optional month (1-12), defaults to current
    - **year**: Optional year, defaults to current
    """
    usage_service = UsageService(db)
    summary = usage_service.get_user_usage_summary(
        user_id=current_user.id,
        month=month,
        year=year
    )
    
    return BaseResponse(
        success=True,
        message="Usage summary retrieved",
        data=summary
    )


@router.get(
    "/limits",
    response_model=BaseResponse,
    summary="Check usage limits",
    description="Check remaining quota for uploads and queries"
)
async def check_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check current limits for uploads and queries.
    """
    usage_service = UsageService(db)
    
    upload_limit = usage_service.check_limit(current_user.id, "UPLOAD")
    query_limit = usage_service.check_limit(current_user.id, "QUERY")
    
    return BaseResponse(
        success=True,
        message="Limits retrieved",
        data={
            "tier": current_user.tier,
            "uploads": upload_limit,
            "queries": query_limit
        }
    )


@router.get(
    "/pricing",
    response_model=BaseResponse,
    summary="Get pricing info",
    description="Get current pricing for pay-as-you-go charges"
)
async def get_pricing():
    """
    Get current pricing information (public endpoint).
    """
    tiers_info = {}
    for tier_name, tier in TIERS.items():
        tiers_info[tier_name.value] = {
            "monthly_price": tier.monthly_price,
            "max_uploads": tier.max_uploads,
            "max_queries": tier.max_queries,
            "max_file_size_mb": tier.max_file_size_mb
        }
    
    return BaseResponse(
        success=True,
        message="Pricing information",
        data={
            "tiers": tiers_info,
            "pay_as_you_go": PRICING
        }
    )
"""
Usage Service - Track uploads, queries, and costs per user.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from .interfaces.usage_service_interface import IUsageService
from models.user import User
from models.usage import UsageRecord, UsageType
from models.subscription import get_tier_limits

logger = logging.getLogger(__name__)


# Pay-as-you-go pricing
PRICING = {
    "upload_per_mb": 0.10,
    "query_simple": 0.01,
    "query_complex": 0.05,
    "transcription_per_minute": 0.006,
    "model_surcharge": {
        "gpt-4": 0.03,
        "claude": 0.02,
    },
    "innovation_fee_percent": 0.15,
}


class UsageService(IUsageService):
    """Service for tracking usage and costs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_upload(
        self,
        user_id: str,
        file_size_bytes: int,
        filename: str
    ) -> Dict[str, Any]:
        """Record a file upload."""
        
        # Calculate cost based on file size
        size_mb = file_size_bytes / (1024 * 1024)
        base_cost = size_mb * PRICING["upload_per_mb"]
        total_cost = base_cost * (1 + PRICING["innovation_fee_percent"])
        
        record = UsageRecord(
            user_id=user_id,
            usage_type=UsageType.UPLOAD.value,
            quantity=1,
            file_size_bytes=file_size_bytes,
            base_cost=round(base_cost, 4),
            total_cost=round(total_cost, 4),
            description=f"Upload: {filename}"
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        logger.info(f"Recorded upload for user {user_id}: {filename}")
        
        return {
            "id": record.id,
            "type": record.usage_type,
            "cost": record.total_cost
        }
    
    def record_query(
        self,
        user_id: str,
        is_complex: bool,
        model_used: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record a query."""
        
        usage_type = UsageType.QUERY_COMPLEX if is_complex else UsageType.QUERY_SIMPLE
        base_cost = PRICING["query_complex"] if is_complex else PRICING["query_simple"]
        
        # Model surcharge
        model_surcharge = 0.0
        if model_used and model_used in PRICING["model_surcharge"]:
            model_surcharge = PRICING["model_surcharge"][model_used]
        
        subtotal = base_cost + model_surcharge
        total_cost = subtotal * (1 + PRICING["innovation_fee_percent"])
        
        record = UsageRecord(
            user_id=user_id,
            usage_type=usage_type.value,
            quantity=1,
            model_used=model_used,
            base_cost=round(base_cost, 4),
            model_surcharge=round(model_surcharge, 4),
            total_cost=round(total_cost, 4),
            description=f"Query ({usage_type.value})"
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        logger.info(f"Recorded query for user {user_id}: {usage_type.value}")
        
        return {
            "id": record.id,
            "type": record.usage_type,
            "cost": record.total_cost
        }
    
    def get_user_usage_summary(
        self,
        user_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get usage summary for a user."""
        
        now = datetime.utcnow()
        month = month or now.month
        year = year or now.year
        
        # Query usage records for the month
        query = self.db.query(UsageRecord).filter(
            UsageRecord.user_id == user_id,
            extract('month', UsageRecord.created_at) == month,
            extract('year', UsageRecord.created_at) == year
        )
        
        records = query.all()
        
        # Aggregate by type
        uploads = [r for r in records if r.usage_type == UsageType.UPLOAD.value]
        simple_queries = [r for r in records if r.usage_type == UsageType.QUERY_SIMPLE.value]
        complex_queries = [r for r in records if r.usage_type == UsageType.QUERY_COMPLEX.value]
        
        total_cost = sum(r.total_cost for r in records)
        
        return {
            "user_id": user_id,
            "period": f"{year}-{month:02d}",
            "uploads": {
                "count": len(uploads),
                "cost": round(sum(r.total_cost for r in uploads), 2)
            },
            "queries": {
                "simple_count": len(simple_queries),
                "complex_count": len(complex_queries),
                "total_count": len(simple_queries) + len(complex_queries),
                "cost": round(sum(r.total_cost for r in simple_queries + complex_queries), 2)
            },
            "total_cost": round(total_cost, 2)
        }
    
    def check_limit(
        self,
        user_id: str,
        usage_type: str
    ) -> Dict[str, Any]:
        """Check if user is within tier limits."""
        
        # Get user and tier
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"allowed": False, "reason": "User not found"}
        
        tier_limits = get_tier_limits(user.tier)
        
        # Get current month usage
        now = datetime.utcnow()
        summary = self.get_user_usage_summary(user_id, now.month, now.year)
        
        if usage_type == "UPLOAD":
            max_allowed = tier_limits.max_uploads
            current = summary["uploads"]["count"]
        else:  # QUERY
            max_allowed = tier_limits.max_queries
            current = summary["queries"]["total_count"]
        
        # -1 means unlimited
        if max_allowed == -1:
            return {
                "allowed": True,
                "current": current,
                "limit": "unlimited",
                "remaining": "unlimited"
            }
        
        allowed = current < max_allowed
        
        return {
            "allowed": allowed,
            "current": current,
            "limit": max_allowed,
            "remaining": max(0, max_allowed - current),
            "reason": None if allowed else f"Monthly {usage_type.lower()} limit reached"
        }
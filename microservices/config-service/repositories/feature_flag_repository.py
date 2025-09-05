"""
Feature flag repository for database operations
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from ..models.feature_flag import FeatureFlag, EnvironmentType
from ..schemas.feature_flag import FeatureFlagCreate, FeatureFlagUpdate


class FeatureFlagRepository:
    """Repository for feature flag operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, flag_data: FeatureFlagCreate) -> FeatureFlag:
        """Create a new feature flag"""
        # Check if flag key already exists
        existing = self.get_by_key(flag_data.flag_key)
        if existing:
            raise ValueError(f"Feature flag already exists: {flag_data.flag_key}")
        
        db_flag = FeatureFlag(**flag_data.dict())
        self.db.add(db_flag)
        self.db.commit()
        self.db.refresh(db_flag)
        return db_flag
    
    def get_by_id(self, flag_id: int) -> Optional[FeatureFlag]:
        """Get feature flag by ID"""
        return self.db.query(FeatureFlag).filter(
            FeatureFlag.id == flag_id
        ).first()
    
    def get_by_key(self, flag_key: str) -> Optional[FeatureFlag]:
        """Get feature flag by key"""
        return self.db.query(FeatureFlag).filter(
            FeatureFlag.flag_key == flag_key
        ).first()
    
    def get_flags(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[FeatureFlag]:
        """Get feature flags with filters"""
        query = self.db.query(FeatureFlag)
        
        filters = []
        
        # Environment filter
        if environment:
            filters.append(
                or_(
                    FeatureFlag.environment == environment,
                    FeatureFlag.environment == EnvironmentType.ALL
                )
            )
        
        # Service filter
        if service_name is not None:
            filters.append(FeatureFlag.service_name == service_name)
        
        # Enabled filter
        if is_enabled is not None:
            filters.append(FeatureFlag.is_enabled == is_enabled)
        
        # Expiration filter
        if not include_expired:
            filters.append(
                or_(
                    FeatureFlag.expires_at.is_(None),
                    FeatureFlag.expires_at > datetime.utcnow()
                )
            )
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.offset(skip).limit(limit).all()
    
    def get_flags_as_dict(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, bool]:
        """Get feature flags as a key-value dictionary with evaluation"""
        flags = self.get_flags(
            environment=environment,
            service_name=service_name,
            is_enabled=True,
            include_expired=False,
            limit=1000  # Get all flags
        )
        
        result = {}
        for flag in flags:
            result[flag.flag_key] = flag.should_be_enabled_for_user(user_id)
        
        return result
    
    def evaluate_flag(
        self,
        flag_key: str,
        user_id: Optional[int] = None,
        environment: Optional[EnvironmentType] = None
    ) -> Dict[str, any]:
        """Evaluate a specific feature flag for a user"""
        flag = self.get_by_key(flag_key)
        
        if not flag:
            return {
                "flag_key": flag_key,
                "is_enabled": False,
                "user_qualified": False,
                "reason": "Flag not found",
                "rollout_percentage": 0,
                "expires_at": None
            }
        
        # Check environment match
        if environment and flag.environment not in [environment, EnvironmentType.ALL]:
            return {
                "flag_key": flag_key,
                "is_enabled": False,
                "user_qualified": False,
                "reason": f"Environment mismatch: flag is for {flag.environment}, requested {environment}",
                "rollout_percentage": flag.rollout_percentage,
                "expires_at": flag.expires_at
            }
        
        # Check if flag is expired
        if flag.is_expired():
            return {
                "flag_key": flag_key,
                "is_enabled": False,
                "user_qualified": False,
                "reason": f"Flag expired at {flag.expires_at}",
                "rollout_percentage": flag.rollout_percentage,
                "expires_at": flag.expires_at
            }
        
        # Check if flag is enabled
        if not flag.is_enabled:
            return {
                "flag_key": flag_key,
                "is_enabled": False,
                "user_qualified": False,
                "reason": "Flag is disabled",
                "rollout_percentage": flag.rollout_percentage,
                "expires_at": flag.expires_at
            }
        
        # Evaluate rollout
        user_qualified = flag.should_be_enabled_for_user(user_id)
        reason = "User qualifies for rollout" if user_qualified else f"User does not qualify for {flag.rollout_percentage}% rollout"
        
        return {
            "flag_key": flag_key,
            "is_enabled": flag.is_enabled,
            "user_qualified": user_qualified,
            "reason": reason,
            "rollout_percentage": flag.rollout_percentage,
            "expires_at": flag.expires_at
        }
    
    def update(
        self,
        flag_id: int,
        flag_data: FeatureFlagUpdate
    ) -> Optional[FeatureFlag]:
        """Update feature flag"""
        db_flag = self.get_by_id(flag_id)
        if not db_flag:
            return None
        
        # Update fields
        update_data = flag_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_flag, field, value)
        
        self.db.commit()
        self.db.refresh(db_flag)
        return db_flag
    
    def delete(self, flag_id: int) -> bool:
        """Delete feature flag"""
        db_flag = self.get_by_id(flag_id)
        if not db_flag:
            return False
        
        self.db.delete(db_flag)
        self.db.commit()
        return True
    
    def count_flags(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        include_expired: bool = False
    ) -> int:
        """Count feature flags with filters"""
        query = self.db.query(FeatureFlag)
        
        filters = []
        
        if environment:
            filters.append(
                or_(
                    FeatureFlag.environment == environment,
                    FeatureFlag.environment == EnvironmentType.ALL
                )
            )
        
        if service_name is not None:
            filters.append(FeatureFlag.service_name == service_name)
        
        if is_enabled is not None:
            filters.append(FeatureFlag.is_enabled == is_enabled)
        
        if not include_expired:
            filters.append(
                or_(
                    FeatureFlag.expires_at.is_(None),
                    FeatureFlag.expires_at > datetime.utcnow()
                )
            )
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()
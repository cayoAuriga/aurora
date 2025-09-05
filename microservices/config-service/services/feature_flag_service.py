"""
Feature flag service business logic
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from ..repositories.feature_flag_repository import FeatureFlagRepository
from ..schemas.feature_flag import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    FeatureFlagEvaluation,
    BulkFeatureFlagResponse,
    EnvironmentType
)
from ..models.feature_flag import FeatureFlag
from shared.errors import NotFoundError, ValidationError


class FeatureFlagService:
    """Business logic for feature flag management"""
    
    def __init__(self, db: Session):
        self.repository = FeatureFlagRepository(db)
    
    def create_feature_flag(
        self,
        flag_data: FeatureFlagCreate
    ) -> FeatureFlagResponse:
        """Create a new feature flag"""
        try:
            flag = self.repository.create(flag_data)
            return FeatureFlagResponse.from_orm(flag)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def get_feature_flag(self, flag_id: int) -> FeatureFlagResponse:
        """Get feature flag by ID"""
        flag = self.repository.get_by_id(flag_id)
        if not flag:
            raise NotFoundError("Feature flag", str(flag_id))
        
        return FeatureFlagResponse.from_orm(flag)
    
    def get_feature_flag_by_key(self, flag_key: str) -> Optional[FeatureFlagResponse]:
        """Get feature flag by key"""
        flag = self.repository.get_by_key(flag_key)
        if not flag:
            return None
        
        return FeatureFlagResponse.from_orm(flag)
    
    def get_feature_flags(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[FeatureFlagResponse]:
        """Get feature flags with filters"""
        flags = self.repository.get_flags(
            environment=environment,
            service_name=service_name,
            is_enabled=is_enabled,
            include_expired=include_expired,
            skip=skip,
            limit=limit
        )
        
        return [FeatureFlagResponse.from_orm(flag) for flag in flags]
    
    def get_bulk_feature_flags(
        self,
        environment: Optional[EnvironmentType] = None,
        service_name: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> BulkFeatureFlagResponse:
        """Get feature flags as key-value pairs with evaluation"""
        flags_dict = self.repository.get_flags_as_dict(
            environment=environment,
            service_name=service_name,
            user_id=user_id
        )
        
        total_count = self.repository.count_flags(
            environment=environment,
            service_name=service_name,
            is_enabled=True,
            include_expired=False
        )
        
        return BulkFeatureFlagResponse(
            flags=flags_dict,
            total_count=total_count,
            environment=environment.value if environment else "all",
            service_name=service_name,
            user_id=user_id
        )
    
    def evaluate_feature_flag(
        self,
        flag_key: str,
        user_id: Optional[int] = None,
        environment: Optional[EnvironmentType] = None
    ) -> FeatureFlagEvaluation:
        """Evaluate a feature flag for a specific user"""
        evaluation = self.repository.evaluate_flag(flag_key, user_id, environment)
        
        return FeatureFlagEvaluation(
            flag_key=evaluation["flag_key"],
            is_enabled=evaluation["is_enabled"],
            rollout_percentage=evaluation["rollout_percentage"],
            user_qualified=evaluation["user_qualified"],
            reason=evaluation["reason"],
            expires_at=evaluation["expires_at"]
        )
    
    def update_feature_flag(
        self,
        flag_id: int,
        flag_data: FeatureFlagUpdate
    ) -> FeatureFlagResponse:
        """Update feature flag"""
        flag = self.repository.update(flag_id, flag_data)
        if not flag:
            raise NotFoundError("Feature flag", str(flag_id))
        
        return FeatureFlagResponse.from_orm(flag)
    
    def delete_feature_flag(self, flag_id: int) -> bool:
        """Delete feature flag"""
        success = self.repository.delete(flag_id)
        if not success:
            raise NotFoundError("Feature flag", str(flag_id))
        
        return success
    
    def toggle_feature_flag(
        self,
        flag_key: str,
        enabled: bool
    ) -> FeatureFlagResponse:
        """Toggle feature flag on/off"""
        flag = self.repository.get_by_key(flag_key)
        if not flag:
            raise NotFoundError("Feature flag", flag_key)
        
        update_data = FeatureFlagUpdate(is_enabled=enabled)
        updated_flag = self.repository.update(flag.id, update_data)
        
        return FeatureFlagResponse.from_orm(updated_flag)
    
    def update_rollout_percentage(
        self,
        flag_key: str,
        percentage: int
    ) -> FeatureFlagResponse:
        """Update rollout percentage for gradual rollout"""
        if percentage < 0 or percentage > 100:
            raise ValidationError("Rollout percentage must be between 0 and 100")
        
        flag = self.repository.get_by_key(flag_key)
        if not flag:
            raise NotFoundError("Feature flag", flag_key)
        
        update_data = FeatureFlagUpdate(rollout_percentage=percentage)
        updated_flag = self.repository.update(flag.id, update_data)
        
        return FeatureFlagResponse.from_orm(updated_flag)
    
    def is_feature_enabled(
        self,
        flag_key: str,
        user_id: Optional[int] = None,
        environment: Optional[EnvironmentType] = None
    ) -> bool:
        """Simple boolean check if feature is enabled for user"""
        evaluation = self.evaluate_feature_flag(flag_key, user_id, environment)
        return evaluation.user_qualified
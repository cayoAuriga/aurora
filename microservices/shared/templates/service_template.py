"""
Template for creating new microservices
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from shared.base_app import BaseService, create_service
from shared.config import BaseServiceConfig, get_config
from shared.database import get_db_dependency
from shared.errors import NotFoundError, ValidationError
from shared.aurora_logging import get_logger

# Service configuration
config = get_config("{{SERVICE_NAME}}")
logger = get_logger("{{SERVICE_NAME}}")

# Create service instance
service = create_service(
    service_name="{{SERVICE_NAME}}",
    config=config,
    title="{{SERVICE_TITLE}}",
    description="{{SERVICE_DESCRIPTION}}"
)

# Database dependency
get_db = get_db_dependency("{{SERVICE_NAME}}")

# Router for API endpoints
router = APIRouter()


# Example endpoints
@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "{{SERVICE_TITLE}} is running"}


@router.get("/items/")
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List items with pagination"""
    # Implement your logic here
    return {"items": [], "total": 0}


@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Get item by ID"""
    # Implement your logic here
    # Example error handling:
    # if not item:
    #     raise NotFoundError("Item", str(item_id))
    return {"id": item_id, "name": "Example Item"}


@router.post("/items/")
async def create_item(
    # item: ItemCreateSchema,
    db: Session = Depends(get_db)
):
    """Create new item"""
    # Implement your logic here
    return {"id": 1, "message": "Item created"}


@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    # item: ItemUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update item"""
    # Implement your logic here
    return {"id": item_id, "message": "Item updated"}


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Delete item"""
    # Implement your logic here
    return {"message": "Item deleted"}


# Add router to service
service.add_router(router, prefix="/api/v1", tags=["{{SERVICE_NAME}}"])

# Export the FastAPI app
app = service.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.service_port,
        reload=config.debug
    )
"""
Service discovery endpoints for Configuration Service
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from shared.service_discovery import get_service_registry, get_discovery_client
from shared.health_checks import create_standard_health_checks

router = APIRouter(prefix="/discovery", tags=["service-discovery"])


@router.get("/services")
async def get_all_services():
    """Get all registered services"""
    registry = get_service_registry()
    services = await registry.get_all_services()
    
    return {
        "services": [service.to_dict() for service in services],
        "total_count": len(services)
    }


@router.get("/services/healthy")
async def get_healthy_services(
    timeout_seconds: int = Query(30, description="Timeout for considering service healthy")
):
    """Get all healthy services"""
    registry = get_service_registry()
    services = await registry.get_healthy_services(timeout_seconds)
    
    return {
        "services": [service.to_dict() for service in services],
        "total_count": len(services),
        "timeout_seconds": timeout_seconds
    }


@router.get("/services/{service_name}")
async def get_service_info(service_name: str):
    """Get information about a specific service"""
    registry = get_service_registry()
    service = await registry.get_service(service_name)
    
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    return service.to_dict()


@router.post("/services/{service_name}/heartbeat")
async def send_heartbeat(service_name: str):
    """Send heartbeat for a service"""
    registry = get_service_registry()
    success = await registry.update_heartbeat(service_name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    return {"success": True, "message": f"Heartbeat updated for {service_name}"}


@router.delete("/services/{service_name}")
async def deregister_service(service_name: str):
    """Deregister a service"""
    registry = get_service_registry()
    success = await registry.deregister_service(service_name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    return {"success": True, "message": f"Service {service_name} deregistered"}


@router.post("/cleanup")
async def cleanup_stale_services(
    timeout_seconds: int = Query(60, description="Timeout for considering service stale")
):
    """Clean up stale services"""
    registry = get_service_registry()
    cleaned_count = await registry.cleanup_stale_services(timeout_seconds)
    
    return {
        "success": True,
        "cleaned_services": cleaned_count,
        "message": f"Cleaned up {cleaned_count} stale services"
    }


@router.get("/health-check/{service_name}")
async def health_check_service(service_name: str):
    """Perform health check on a specific service"""
    discovery_client = get_discovery_client()
    is_healthy = await discovery_client.health_check_service(service_name)
    
    return {
        "service_name": service_name,
        "healthy": is_healthy,
        "timestamp": __import__('time').time()
    }


@router.get("/health-check-all")
async def health_check_all_services():
    """Perform health check on all registered services"""
    discovery_client = get_discovery_client()
    results = await discovery_client.health_check_all_services()
    
    healthy_count = sum(1 for is_healthy in results.values() if is_healthy)
    total_count = len(results)
    
    return {
        "results": results,
        "summary": {
            "total_services": total_count,
            "healthy_services": healthy_count,
            "unhealthy_services": total_count - healthy_count
        },
        "timestamp": __import__('time').time()
    }
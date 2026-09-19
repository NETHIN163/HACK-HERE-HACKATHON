from fastapi import APIRouter, HTTPException, status
from app.models.road import Road
from app.services.traffic_service import traffic_service

router = APIRouter(tags=["roads"])


@router.get("/api/roads/{road_id}", response_model=Road)
def get_road_by_id(road_id: str):
    """Returns requested road details or 404 HTTP error if unknown."""
    road = traffic_service.get_road(road_id)
    if not road:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found.",
        )
    return road

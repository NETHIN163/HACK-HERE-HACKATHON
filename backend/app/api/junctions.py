from fastapi import APIRouter, HTTPException, status
from app.models.junction import Junction
from app.services.traffic_service import traffic_service

router = APIRouter(tags=["junctions"])


@router.get("/api/junctions/{junction_id}", response_model=Junction)
def get_junction_by_id(junction_id: str):
    """Returns requested junction details or 404 HTTP error if unknown."""
    junc = traffic_service.get_junction(junction_id)
    if not junc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Junction '{junction_id}' not found.",
        )
    return junc

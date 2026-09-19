from pydantic import BaseModel, ConfigDict, Field


class Junction(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    junction_id: str = Field(..., description="Unique identifier for the junction")
    signal_phase: str = Field("NS_GREEN", description="Current signal phase (e.g. NS_GREEN, EW_GREEN, ALL_RED)")
    green_duration: float = Field(30.0, description="Active green signal duration in seconds", ge=0.0)
    red_duration: float = Field(30.0, description="Active red signal duration in seconds", ge=0.0)
    queue_length: int = Field(0, description="Total queued vehicles at all approaches of junction", ge=0)
    vehicle_density: float = Field(0.0, description="Aggregate vehicle density at junction area (0.0 to 1.0)", ge=0.0)
    pedestrian_count: int = Field(0, description="Number of waiting pedestrians", ge=0)
    emergency_reserved: bool = Field(False, description="Flag indicating if junction is reserved for emergency corridor")
    crossing_active: bool = Field(False, description="Flag indicating active pedestrian crossing signal")
    crossing_remaining_seconds: float = Field(0.0, description="Remaining seconds for active pedestrian clearance", ge=0.0)


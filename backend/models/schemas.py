from pydantic import BaseModel
from typing import Optional


class Scene(BaseModel):
    scene_number: int
    int_ext: str
    location_description: str
    time_of_day: str
    terrain_tags: list[str]
    characters_present: list[str] = []


class CandidateLocation(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    terrain_score: float = 0.0
    description_score: float = 0.0
    int_ext_score: float = 0.0
    time_score: float = 0.0
    distance_score: float = 0.0
    total_score: float = 0.0
    place_id: str = ""


class SceneLocation(BaseModel):
    scene: Scene
    candidates: list[CandidateLocation]
    best_location: Optional[CandidateLocation] = None


class TravelLeg(BaseModel):
    from_location: str
    to_location: str
    from_lat: float
    from_lng: float
    to_lat: float
    to_lng: float
    distance_km: float
    duration_minutes: float


class ShootOrderItem(BaseModel):
    order: int
    scene_number: int
    location: CandidateLocation
    travel_to_next: Optional[TravelLeg] = None


class LogisticsEstimate(BaseModel):
    total_travel_hours: float
    total_distance_km: float
    transport_rate: float
    estimated_cost: float
    currency: str = "NPR"


class ProjectReport(BaseModel):
    project_name: str
    base_region: str
    total_scenes: int
    total_locations: int
    scenes_locations: list[SceneLocation]
    shoot_order: list[ShootOrderItem]
    logistics: LogisticsEstimate
    warnings: list[str] = []

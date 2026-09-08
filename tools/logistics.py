import httpx
import math

from backend.models.schemas import (
    CandidateLocation,
    LogisticsEstimate,
    ShootOrderItem,
    TravelLeg,
)

OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving"


async def get_travel_info(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> tuple[float, float]:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{OSRM_ROUTE_URL}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}",
                params={"overview": "false"},
                timeout=10,
            )
            data = resp.json()
            if data.get("routes"):
                route = data["routes"][0]
                distance_km = route["distance"] / 1000.0
                duration_min = route["duration"] / 60.0
                return distance_km, duration_min
        except Exception as e:
            print(f"OSRM API error: {e}")

    R = 6371
    dlat = math.radians(dest_lat - origin_lat)
    dlon = math.radians(dest_lng - origin_lng)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(origin_lat)) * math.cos(math.radians(dest_lat)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = R * c
    duration_min = (distance_km / 60.0) * 60

    return round(distance_km, 2), round(duration_min, 1)


async def calculate_pairwise_travel(
    shoot_order: list[ShootOrderItem],
) -> list[ShootOrderItem]:
    for i in range(len(shoot_order) - 1):
        curr = shoot_order[i]
        next_item = shoot_order[i + 1]
        dist, dur = await get_travel_info(
            curr.location.lat,
            curr.location.lng,
            next_item.location.lat,
            next_item.location.lng,
        )
        curr.travel_to_next = TravelLeg(
            from_location=curr.location.name,
            to_location=next_item.location.name,
            from_lat=curr.location.lat,
            from_lng=curr.location.lng,
            to_lat=next_item.location.lat,
            to_lng=next_item.location.lng,
            distance_km=round(dist, 2),
            duration_minutes=round(dur, 1),
        )
    return shoot_order


def nearest_neighbor_order(items: list[ShootOrderItem]) -> list[ShootOrderItem]:
    if len(items) <= 1:
        return items

    remaining = list(items)
    ordered = [remaining.pop(0)]

    while remaining:
        current = ordered[-1]
        best_idx = 0
        best_dist = float("inf")
        for i, item in enumerate(remaining):
            dist = (current.location.lat - item.location.lat) ** 2 + (
                current.location.lng - item.location.lng
            ) ** 2
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        ordered.append(remaining.pop(best_idx))

    for i, item in enumerate(ordered):
        item.order = i + 1

    return ordered


def estimate_logistics(
    shoot_order: list[ShootOrderItem],
    transport_rate: float = 2500.0,
    currency: str = "NPR",
) -> LogisticsEstimate:
    total_km = 0.0
    total_minutes = 0.0
    for item in shoot_order:
        if item.travel_to_next:
            total_km += item.travel_to_next.distance_km
            total_minutes += item.travel_to_next.duration_minutes

    total_hours = round(total_minutes / 60.0, 2)
    total_km = round(total_km, 2)
    estimated_cost = round(total_hours * transport_rate, 2)

    return LogisticsEstimate(
        total_travel_hours=total_hours,
        total_distance_km=total_km,
        transport_rate=transport_rate,
        estimated_cost=estimated_cost,
        currency=currency,
    )

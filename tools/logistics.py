import httpx

from backend.models.schemas import (
    CandidateLocation,
    LogisticsEstimate,
    ShootOrderItem,
    TravelLeg,
)

DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


async def get_travel_info(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    api_key: str,
) -> tuple[float, float]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            DIRECTIONS_URL,
            params={
                "origin": f"{origin_lat},{origin_lng}",
                "destination": f"{dest_lat},{dest_lng}",
                "key": api_key,
                "mode": "driving",
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("routes"):
            leg = data["routes"][0]["legs"][0]
            distance_km = leg["distance"]["value"] / 1000.0
            duration_min = leg["duration"]["value"] / 60.0
            return distance_km, duration_min
    return 0.0, 0.0


async def calculate_pairwise_travel(
    shoot_order: list[ShootOrderItem],
    api_key: str,
) -> list[ShootOrderItem]:
    for i in range(len(shoot_order) - 1):
        curr = shoot_order[i]
        next_item = shoot_order[i + 1]
        dist, dur = await get_travel_info(
            curr.location.lat,
            curr.location.lng,
            next_item.location.lat,
            next_item.location.lng,
            api_key,
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

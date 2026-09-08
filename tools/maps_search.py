import os
import httpx

from backend.models.schemas import CandidateLocation

PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


async def geocode_region(region: str, api_key: str) -> tuple[float, float]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GEOCODE_URL,
            params={"address": region, "key": api_key},
            timeout=10,
        )
        data = resp.json()
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    return 27.7172, 85.3240  # default: Kathmandu


async def search_locations(
    query: str,
    region_lat: float,
    region_lng: float,
    api_key: str,
    radius: int = 50000,
    keyword: str = "",
) -> list[CandidateLocation]:
    candidates = []
    async with httpx.AsyncClient() as client:
        params = {
            "query": query,
            "key": api_key,
            "location": f"{region_lat},{region_lng}",
            "radius": radius,
        }
        if keyword:
            params["keyword"] = keyword

        resp = await client.get(PLACES_TEXT_SEARCH_URL, params=params, timeout=10)
        data = resp.json()

        for result in data.get("results", [])[:5]:
            loc = result["geometry"]["location"]
            candidates.append(
                CandidateLocation(
                    name=result.get("name", "Unknown"),
                    address=result.get("formatted_address", ""),
                    lat=loc["lat"],
                    lng=loc["lng"],
                    place_id=result.get("place_id", ""),
                )
            )
    return candidates


async def find_candidates_for_scene(
    location_description: str,
    terrain_tags: list[str],
    int_ext: str,
    region_lat: float,
    region_lng: float,
    api_key: str,
) -> list[CandidateLocation]:
    query = f"{location_description}"
    if terrain_tags:
        query += f" {', '.join(terrain_tags[:3])}"

    all_candidates = await search_locations(query, region_lat, region_lng, api_key)

    if not all_candidates and terrain_tags:
        fallback_query = " ".join(terrain_tags[:2])
        all_candidates = await search_locations(fallback_query, region_lat, region_lng, api_key)

    return all_candidates[:3]

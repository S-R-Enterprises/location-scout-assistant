import httpx
import urllib.parse

from backend.models.schemas import CandidateLocation

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"


async def geocode_region(region: str) -> tuple[float, float]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            NOMINATIM_SEARCH_URL,
            params={"q": region, "format": "json", "limit": 1},
            headers={"User-Agent": "LocationScoutAssistant/1.0"},
            timeout=10,
        )
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    return 27.7172, 85.3240


async def search_locations(
    query: str,
    region_lat: float,
    region_lng: float,
    radius: int = 50000,
) -> list[CandidateLocation]:
    candidates = []

    overpass_query = f"""
    [out:json][timeout:10];
    (
      node["name"](around:{radius},{region_lat},{region_lng});
      way["name"](around:{radius},{region_lat},{region_lng});
    );
    out center body;
    """

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                OVERPASS_API_URL,
                data={"data": overpass_query},
                timeout=15,
            )
            data = resp.json()

            for element in data.get("elements", [])[:10]:
                tags = element.get("tags", {})
                name = tags.get("name", tags.get("amenity", "Unknown location"))

                if element.get("type") == "node":
                    lat = element["lat"]
                    lon = element["lon"]
                elif "center" in element:
                    lat = element["center"]["lat"]
                    lon = element["center"]["lon"]
                else:
                    continue

                address_parts = []
                for key in ["addr:street", "addr:housenumber", "addr:city", "addr:state"]:
                    if key in tags:
                        address_parts.append(tags[key])
                address = ", ".join(address_parts) if address_parts else f"{lat}, {lon}"

                candidates.append(
                    CandidateLocation(
                        name=name,
                        address=address,
                        lat=lat,
                        lng=lon,
                        place_id=str(element.get("id", "")),
                    )
                )
        except Exception as e:
            print(f"Overpass API error: {e}")

    if not candidates:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                NOMINATIM_SEARCH_URL,
                params={
                    "q": query,
                    "format": "json",
                    "limit": 5,
                    "viewbox": f"{region_lng - 0.5},{region_lat + 0.5},{region_lng + 0.5},{region_lat - 0.5}",
                    "bounded": 1,
                },
                headers={"User-Agent": "LocationScoutAssistant/1.0"},
                timeout=10,
            )
            data = resp.json()
            for result in data[:5]:
                candidates.append(
                    CandidateLocation(
                        name=result.get("display_name", "Unknown").split(",")[0],
                        address=result.get("display_name", ""),
                        lat=float(result["lat"]),
                        lng=float(result["lon"]),
                        place_id=str(result.get("osm_id", "")),
                    )
                )

    return candidates[:5]


async def find_candidates_for_scene(
    location_description: str,
    terrain_tags: list[str],
    int_ext: str,
    region_lat: float,
    region_lng: float,
) -> list[CandidateLocation]:
    query = f"{location_description}"
    if terrain_tags:
        query += f" {', '.join(terrain_tags[:3])}"

    all_candidates = await search_locations(query, region_lat, region_lng)

    if not all_candidates and terrain_tags:
        fallback_query = " ".join(terrain_tags[:2])
        all_candidates = await search_locations(fallback_query, region_lat, region_lng)

    if not all_candidates:
        amenity_type = "tourism"
        if terrain_tags:
            if "urban" in terrain_tags or "industrial" in terrain_tags:
                amenity_type = "amenity"
            elif "nature" in terrain_tags or "water" in terrain_tags:
                amenity_type = "natural"

        overpass_query = f"""
        [out:json][timeout:10];
        node["{amenity_type}"](around:50000,{region_lat},{region_lng});
        out body;
        """

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    OVERPASS_API_URL,
                    data={"data": overpass_query},
                    timeout=15,
                )
                data = resp.json()
                for element in data.get("elements", [])[:5]:
                    tags = element.get("tags", {})
                    name = tags.get("name", tags.get(amenity_type, "Unknown"))
                    candidates = all_candidates
                    candidates.append(
                        CandidateLocation(
                            name=name,
                            address=f"{element['lat']}, {element['lon']}",
                            lat=element["lat"],
                            lng=element["lon"],
                            place_id=str(element.get("id", "")),
                        )
                    )
                    all_candidates = candidates
            except Exception:
                pass

    return all_candidates[:3]

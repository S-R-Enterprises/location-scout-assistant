from backend.models.schemas import (
    CandidateLocation,
    ProjectReport,
    SceneLocation,
    ShootOrderItem,
)
from tools.script_parser import extract_scenes, extract_text_from_pdf
from tools.maps_search import find_candidates_for_scene, geocode_region
from tools.location_ranker import rank_locations
from tools.logistics import (
    calculate_pairwise_travel,
    estimate_logistics,
    nearest_neighbor_order,
)


async def run_pipeline(
    pdf_bytes: bytes | None,
    text_input: str | None,
    base_region: str,
    project_name: str,
) -> ProjectReport:
    if pdf_bytes:
        raw_text = extract_text_from_pdf(pdf_bytes)
    else:
        raw_text = text_input or ""

    scenes = await extract_scenes(raw_text)
    if not scenes:
        raise ValueError("No scenes could be extracted from the screenplay.")

    region_lat, region_lng = await geocode_region(base_region)

    scenes_locations: list[SceneLocation] = []
    all_locations_count = 0

    for scene in scenes:
        candidates = await find_candidates_for_scene(
            scene.location_description,
            scene.terrain_tags,
            scene.int_ext,
            region_lat,
            region_lng,
        )
        ranked = rank_locations(scene, candidates, region_lat, region_lng)
        best = ranked[0] if ranked else None
        all_locations_count += len(ranked)
        scenes_locations.append(
            SceneLocation(scene=scene, candidates=ranked, best_location=best)
        )

    shoot_items = []
    for sl in scenes_locations:
        if sl.best_location:
            shoot_items.append(
                ShootOrderItem(
                    order=sl.scene.scene_number,
                    scene_number=sl.scene.scene_number,
                    location=sl.best_location,
                )
            )

    shoot_order = nearest_neighbor_order(shoot_items)
    shoot_order = await calculate_pairwise_travel(shoot_order)
    logistics = estimate_logistics(shoot_order)

    warnings = []
    warnings.append("Weather data not included in MVP.")
    warnings.append("Permit/legal information not verified.")
    warnings.append("Cost estimate is approximate — verify with local rates.")
    warnings.append("Using free OpenStreetMap data — results may vary from Google Maps.")

    return ProjectReport(
        project_name=project_name,
        base_region=base_region,
        total_scenes=len(scenes),
        total_locations=all_locations_count,
        scenes_locations=scenes_locations,
        shoot_order=shoot_order,
        logistics=logistics,
        warnings=warnings,
    )

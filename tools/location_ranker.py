from backend.models.schemas import Scene, CandidateLocation


def _terrain_match_score(scene: Scene, candidate: CandidateLocation) -> float:
    if not scene.terrain_tags:
        return 0.5
    name_lower = candidate.name.lower()
    addr_lower = candidate.address.lower()
    combined = f"{name_lower} {addr_lower}"
    matches = sum(1 for tag in scene.terrain_tags if tag.lower() in combined)
    return min(matches / max(len(scene.terrain_tags), 1), 1.0)


def _description_match_score(scene: Scene, candidate: CandidateLocation) -> float:
    desc_words = set(scene.location_description.lower().split())
    combined = f"{candidate.name.lower()} {candidate.address.lower()}"
    matches = sum(1 for w in desc_words if len(w) > 2 and w in combined)
    return min(matches / max(len(desc_words), 1), 1.0)


def _int_ext_score(scene: Scene, candidate: CandidateLocation) -> float:
    name_lower = candidate.name.lower()
    addr_lower = candidate.address.lower()
    combined = f"{name_lower} {addr_lower}"
    if scene.int_ext == "INT":
        indoor_keywords = ["hotel", "museum", "indoor", "hall", "room", "office", "cafe", "restaurant", "mall", "theater"]
        outdoor_keywords = ["park", "garden", "street", "road", "field", "mountain", "river", "forest"]
        score = 0.5
        for kw in indoor_keywords:
            if kw in combined:
                score = 1.0
                break
        for kw in outdoor_keywords:
            if kw in combined:
                score = max(score, 0.3)
        return score
    else:
        outdoor_keywords = ["park", "garden", "street", "road", "field", "mountain", "river", "forest", "square", "bridge"]
        indoor_keywords = ["hotel", "museum", "indoor", "hall", "room", "office"]
        score = 0.5
        for kw in outdoor_keywords:
            if kw in combined:
                score = 1.0
                break
        for kw in indoor_keywords:
            if kw in combined:
                score = max(score, 0.3)
        return score


def _time_score(scene: Scene, candidate: CandidateLocation) -> float:
    if scene.time_of_day in ["DAY", "MORNING", "AFTERNOON"]:
        return 0.8
    elif scene.time_of_day in ["NIGHT"]:
        return 0.7
    return 0.6


def rank_locations(
    scene: Scene,
    candidates: list[CandidateLocation],
    base_lat: float = 27.7172,
    base_lng: float = 85.3240,
) -> list[CandidateLocation]:
    for c in candidates:
        c.terrain_score = _terrain_match_score(scene, c)
        c.description_score = _description_match_score(scene, c)
        c.int_ext_score = _int_ext_score(scene, c)
        c.time_score = _time_score(scene, c)

        dist_sq = (c.lat - base_lat) ** 2 + (c.lng - base_lng) ** 2
        c.distance_score = max(1.0 - dist_sq * 10, 0.0)

        c.total_score = (
            c.terrain_score * 0.40
            + c.description_score * 0.30
            + c.int_ext_score * 0.15
            + c.time_score * 0.10
            + c.distance_score * 0.05
        )

    candidates.sort(key=lambda x: x.total_score, reverse=True)
    return candidates

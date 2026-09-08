import re
import io
from typing import Optional

from backend.models.schemas import Scene

SLUGLINE_PATTERN = re.compile(
    r"^(?:\d+\.?\s*)?(INT\.?|EXT\.?|INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?)\s*"
    r"[.\-\s]*(?:DAY|NIGHT|DAWN|DUSK|CONTINUOUS|MORNING|AFTERNOON|EVENING)?",
    re.MULTILINE | re.IGNORECASE,
)

LOCATION_KEYWORDS = {
    "urban": ["street", "city", "downtown", "building", "office", "apartment", "house", "room", "cafe", "restaurant", "bar", "hotel", "mall", "shop", "store", "market"],
    "industrial": ["factory", "warehouse", "plant", "mill", "dock", "port", "construction", "workshop", "garage"],
    "nature": ["forest", "park", "garden", "field", "meadow", "hill", "mountain", "river", "lake", "beach", "coast", "desert", "canyon", "valley"],
    "residential": ["home", "house", "apartment", "neighborhood", "suburb", "village", "town"],
    "indoor": ["room", "hall", "office", "kitchen", "bedroom", "bathroom", "lobby", "theater", "cinema", "museum", "church", "temmos"],
    "exterior": ["outside", "yard", "garden", "street", "road", "highway", "bridge", "rooftop", "balcony", "patio"],
    "water": ["ocean", "sea", "river", "lake", "pool", "harbor", "dock", "pier", "beach", "waterfall"],
    "night": ["nightclub", "bar", "alley", "dark", "shadow", "moonlight", "streetlight"],
}


def detect_terrain_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags = []
    for tag, keywords in LOCATION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags if tags else ["general"]


def regex_fallback_parse(text: str) -> list[Scene]:
    scenes = []
    lines = text.split("\n")
    current_scene_num = 0

    for line in lines:
        line = line.strip()
        match = SLUGLINE_PATTERN.match(line)
        if match:
            current_scene_num += 1
            int_ext_raw = match.group(1).upper().replace(".", "")
            if "/" in int_ext_raw:
                int_ext_raw = "INT/EXT"

            time_of_day = "DAY"
            upper_line = line.upper()
            for tod in ["NIGHT", "DAWN", "DUSK", "CONTINUOUS", "MORNING", "AFTERNOON", "EVENING"]:
                if tod in upper_line:
                    time_of_day = tod
                    break

            location_part = re.sub(
                r"^(?:\d+\.?\s*)?(INT\.?|EXT\.?|INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?)\s*[.\-\s]*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            location_part = re.sub(
                r"\s*(DAY|NIGHT|DAWN|DUSK|CONTINUOUS|MORNING|AFTERNOON|EVENING)\s*$",
                "",
                location_part,
                flags=re.IGNORECASE,
            ).strip()
            location_part = re.sub(r"^\s*[-–—.\s]+\s*", "", location_part).strip()

            if not location_part:
                location_part = "Unknown location"

            terrain_tags = detect_terrain_tags(location_part)

            scenes.append(
                Scene(
                    scene_number=current_scene_num,
                    int_ext=int_ext_raw,
                    location_description=location_part,
                    time_of_day=time_of_day,
                    terrain_tags=terrain_tags,
                    characters_present=[],
                )
            )
    return scenes


async def extract_scenes(text: str) -> list[Scene]:
    return regex_fallback_parse(text)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception:
        return pdf_bytes.decode("utf-8", errors="ignore")

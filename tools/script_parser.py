import json
import re
from typing import Optional

from google import genai
from google.genai import types

from backend.models.schemas import Scene

SYSTEM_PROMPT = """You are a screenplay parser. Extract all scenes from the provided screenplay text.
For each scene, return a JSON array of objects with these fields:
- scene_number: integer
- int_ext: "INT" or "EXT"
- location_description: string describing the location
- time_of_day: "DAY", "NIGHT", "DAWN", "DUSK", or "CONTINUOUS"
- terrain_tags: array of relevant terrain/setting tags (e.g. "urban", "industrial", "forest", "indoor", "residential")
- characters_present: array of character names mentioned in the scene

Return ONLY the JSON array, no other text. If you cannot parse a scene, skip it.
Use regex fallback for INT./EXT. sluglines if needed."""

SLUGLINE_PATTERN = re.compile(
    r"^(?:\d+\.?\s*)?(INT\.?|EXT\.?|INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?)\s*"
    r"[.\-\s]*(?:DAY|NIGHT|DAWN|DUSK|CONTINUOUS|MORNING|AFTERNOON|EVENING)?",
    re.MULTILINE | re.IGNORECASE,
)


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
            else:
                int_ext_raw = int_ext_raw.replace("EXT", "EXT").replace("INT", "INT")

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

            scenes.append(
                Scene(
                    scene_number=current_scene_num,
                    int_ext=int_ext_raw,
                    location_description=location_part,
                    time_of_day=time_of_day,
                    terrain_tags=[],
                    characters_present=[],
                )
            )
    return scenes


async def extract_scenes_gemini(text: str, api_key: str) -> list[Scene]:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\n\nScreenplay:\n{text[:15000]}",
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=8192,
            ),
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        scenes_data = json.loads(raw)
        return [Scene(**s) for s in scenes_data]
    except Exception as e:
        print(f"Gemini parsing failed, using regex fallback: {e}")
        return regex_fallback_parse(text)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
        import io
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception:
        return pdf_bytes.decode("utf-8", errors="ignore")

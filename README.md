# Location Scout Assistant

AI-powered screenplay location scouting and shoot scheduling tool.

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set your API keys
cp ../.env.example ../.env
# Edit .env with your keys

# Run the server
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. API Keys

You need a Google Cloud API key with these APIs enabled:
- Google Maps Places API
- Google Maps Directions API
- Google Maps Geocoding API
- Google Generative Language API (Gemini)

Set `GOOGLE_MAPS_API_KEY` and `GEMINI_API_KEY` in `.env`.

## How It Works

1. Upload a screenplay PDF or paste text
2. Gemini extracts structured scene data
3. Google Places finds candidate locations per scene
4. Locations are ranked against scene requirements
5. Nearest-neighbor routing optimizes shoot order
6. Travel time and rough logistics cost are calculated

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, Tailwind CSS, Leaflet maps
- **AI**: Google Gemini via google-genai SDK
- **Maps**: Google Places, Directions, Geocoding APIs

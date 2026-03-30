# London Schools Explorer 🏛

A public-facing school finder for London, built on Ofsted inspection data with
composite scoring, filtering, and borough breakdowns.

---

## Stack

| Layer    | Tech                          | Deploy to         |
|----------|-------------------------------|-------------------|
| Frontend | React (CDN) + vanilla HTML/CSS | Vercel / Netlify  |
| API      | FastAPI + Python              | Render / Railway  |
| Data     | JSON (pre-processed from CSV) | Bundled with API  |

---

## Project Structure

```
london-schools/
├── api/
│   ├── main.py           ← FastAPI app
│   └── requirements.txt
├── data/
│   └── schools.json      ← Pre-processed from ofsted.csv (451 schools)
├── frontend/
│   └── index.html        ← Full React app (single file, no build step)
├── scripts/
│   └── process_data.py   ← Re-generate schools.json from source CSVs
└── README.md
```

---

## Quick Start (local)

### 1. Start the API

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 2. Open the frontend

```bash
# Either open directly in browser:
open frontend/index.html

# Or serve with Python:
cd frontend && python3 -m http.server 3000
```

The frontend tries to connect to `http://localhost:8000` and falls back to
bundled demo data if the API is unavailable.

---

## API Endpoints

| Endpoint              | Description                            |
|-----------------------|----------------------------------------|
| `GET /schools`        | List/search/filter schools             |
| `GET /schools/{urn}`  | Get single school by URN               |
| `GET /filters`        | Available filter values (phases, LAs)  |
| `GET /stats`          | Aggregate statistics                   |

### Query Parameters for `/schools`

| Param            | Type    | Example                       |
|------------------|---------|-------------------------------|
| `q`              | string  | `q=Highgate`                  |
| `phase`          | string  | `phase=Secondary`             |
| `local_authority`| string  | `local_authority=Islington`   |
| `score_band`     | string  | `score_band=Outstanding`      |
| `min_score`      | float   | `min_score=80`                |
| `has_sixth_form` | bool    | `has_sixth_form=true`         |
| `sort_by`        | string  | `sort_by=ofsted_score`        |
| `sort_dir`       | string  | `sort_dir=desc`               |
| `limit`          | int     | `limit=50`                    |
| `offset`         | int     | `offset=0`                    |

---

## Scoring Model

Scores are derived from `scoring.py`:

| Dimension           | Weight | Source                  |
|---------------------|--------|-------------------------|
| Ofsted Quality      | 40%    | `Quality of education`  |
| IMD Deprivation     | 25%    | `imd_lookup.csv`        |
| Crime               | 20%    | `crime_cache.csv`       |
| Distance            | 15%    | User-supplied postcode  |

Current deployment uses Ofsted scores only (IMD/crime/distance require
the enrichment pipeline from `enrich.py` and `geocode.py`).

**Score bands:**
- 85–100 → Outstanding
- 70–84  → Good
- 45–69  → Requires improvement
- 0–44   → Inadequate

---

## Deployment

### Frontend → Vercel (free)

```bash
# Vercel can serve a plain HTML file directly
npm i -g vercel
cd frontend
vercel
```

Or drag-and-drop `frontend/` to https://vercel.com/new.

### API → Render (free tier)

1. Push repo to GitHub
2. New Web Service on Render → connect repo
3. Root directory: `api`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Update the API URL in the frontend

In `frontend/index.html`, change:
```js
const API_BASE = 'http://localhost:8000';
```
to your Render URL:
```js
const API_BASE = 'https://london-schools-api.onrender.com';
```

---

## Adding the Map

Install Leaflet and geocode schools by postcode:

```bash
# In frontend, add to <head>:
# <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
# <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
```

Add a geocoding step to `scripts/process_data.py` using `geopy` to add
`lat`/`lng` fields to each school record, then render a Leaflet map.

---

## Re-processing Data

To regenerate `data/schools.json` from source CSVs:

```bash
python3 scripts/process_data.py
```

Source files needed in `data/`:
- `ofsted.csv` — Ofsted inspection data
- `imd_lookup.csv` — IMD deprivation rankings
- `lsoa_2011_to_2021_lookup.csv` — LSOA geography lookup
- `crime_cache.csv` — Police API crime data (optional)

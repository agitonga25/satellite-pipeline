# Satellite Cloud Cover Analysis — Ghana 2023

> **Scientific Python Project** | Python 3.10+ | Project-Based Learning, MSc DSAIS, Cranfield University

## Learning Context

This project was completed as part of a **Project-Based Learning (PBL)** module — my first experience with the PBL methodology. Rather than following a prescribed set of instructions, the task required independently scoping the problem, identifying appropriate data sources, designing the pipeline architecture, and interpreting results to arrive at a meaningful conclusion. The core module  was co-developed in a group; pipeline extensions, EDA, analysis were individual work.

The end-to-end nature of the work — from discovering the STAC API and understanding its response structure, to handling real-world data quality issues (null values from Sentinel-1a) and communicating findings — reflects the core philosophy of PBL: learning by doing on a problem with no single right answer.

## Overview

A data pipeline for extracting and analysing cloud cover data from Landsat and Sentinel satellite imagery over Ghana. The pipeline queries the [Element 84 Earth Search STAC API](https://earth-search.aws.element84.com/v1) via HTTP GET requests, flattens the nested JSON responses, and produces a clean tabular dataset for temporal analysis — to identify the optimal times for satellite imaging over Ghana.

**Key finding:** December is the best month for satellite imaging over Ghana (avg. cloud cover ~14%). Cloud cover exceeds 50% for most of the year, peaking in June–August (~80–85%).

## Pipeline Architecture

```
  STAC API GET Request
  earth-search.aws.element84.com/v1/search
        │
        ▼
  Raw JSON Response
  (nested FeatureCollection)
        │
        ▼
  Items.flatten_data()
  pd.json_normalize → tabular DataFrame
        │
        ▼
  Monthly loop (relativedelta)
  → concatenate into final_df (4,442 rows)
        │
        ▼
  Filter: select desired columns,
  drop duplicates on geometry.coordinates
        │
        ▼
  EDA: null analysis, platform counts,
  monthly resample, correlation
        │
        ▼
  Conclusion: best imaging windows
```

## API Details

| Parameter | Value |
|-----------|-------|
| Endpoint | `https://earth-search.aws.element84.com/v1/search` |
| Auth | None (public API) |
| Bounding box | Ghana: `-3.244, 4.710, 1.060, 11.098` |
| Date range | 2022-12-31 to 2024-01-02 (monthly windows; edges overlap adjacent years to guarantee full coverage of 2023)|
| Limit per call | 350 |
| Total records fetched | 4,442 |

## Fields Extracted

| API Field | Description |
|-----------|-------------|
| `properties.eo:cloud_cover` | Cloud cover percentage (0–100) |
| `properties.datetime` | Image acquisition datetime (UTC) |
| `geometry.coordinates` | Scene bounding polygon |
| `properties.platform` | Satellite platform name |
| `id` | Unique scene identifier |
| `collection` | Dataset collection name |
| `bbox` | Scene bounding box |

## Platforms in Dataset

| Platform | Images | Notes |
|----------|--------|-------|
| sentinel-2a | 2,216 | Primary analysis platform |
| sentinel-2b | 1,721 | Primary analysis platform |
| landsat-9 | 138 | |
| landsat-8 | 135 | |
| landsat-7 | 108 | |
| sentinel-1a | 124 | ⚠️ All cloud cover values are NaN — excluded from analysis |

## Project Structure

```
satellite_pipeline/
├── data/
│   ├── ghana_cloud_cover_dummy.csv       # Synthetic dummy data (safe to commit)
│   └── sample_api_response_dummy.json    # Sample raw API response structure
│   # real extracted data → gitignored, never commit
├── src/
│   ├── __init__.py
│   └── SP_Ghana_flattened.py             # Items class: get_data() + flatten_data()
├── notebooks/
│   └── 01_cloud_cover_analysis.ipynb     # Full analysis: EDA, plots, conclusions
├── results/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
git clone <repo-url>
cd satellite_pipeline
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```python
import SP_Ghana_flattened as sgf
import pandas as pd

bbox = "-3.24437008301, 4.71046214438, 1.0601216976, 11.0983409693"
fields = [
    'properties.eo:cloud_cover',
    'properties.datetime',
    'geometry.coordinates',
    'properties.platform',
    'id'
]
datetime = "2023-01-01T00:00:00Z/2023-12-31T23:59:59Z"

items = sgf.Items()
json_data = items.get_data(bbox, fields, datetime, limit=350)
df = items.flatten_data(json_data)
print(df.head())
```

## Requirements

```
requests>=2.31
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
geopandas>=0.14
python-dateutil>=2.8
```

## Key Results

| Month | Images | Avg Cloud Cover |
|-------|--------|----------------|
| Jan 2023 | 340 | 41% |
| Jun 2023 | 340 | 85% ← worst |
| Dec 2023 | 460 | 14% ← best |

**Recommendation:** Use satellite imagery over Ghana in **November–January** when cloud cover drops below 50%. Avoid June–August (>79% cloud cover).

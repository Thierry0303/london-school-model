"""
London School Model
High-level pipeline for matching and ranking London schools
for a given postcode and preferences.
"""

from typing import Optional, Dict

import pandas as pd

from .loader import load_schools
from .geocode import postcode_to_latlon
from .filters import filter_by_phase, filter_by_distance
from .enrich import enrich
from .scoring import score_schools, DEFAULT_WEIGHTS
from .probability import add_probability_column


def match_schools(
    postcode: str,
    phase: Optional[str] = None,
    max_distance_km: Optional[float] = None,
    weights: Optional[Dict[str, float]] = None,
    schools_path: str = "data/london_schools.csv",
    imd_path: str = "data/imd_lookup.csv",
    crime_path: str = "data/crime_cache.csv",
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    """
    End-to-end pipeline:

    1. Geocode user postcode
    2. Load London schools dataset
    3. Filter by phase (primary/secondary)
    4. Filter by distance (optional)
    5. Enrich with IMD, crime, Ofsted badge
    6. Score schools with weighted model
    7. Add offer probability
    8. Return ranked shortlist

    Args:
        postcode: User's home postcode
        phase: 'primary', 'secondary', or None
        max_distance_km: Optional max distance filter
        weights: Optional override for scoring weights
        schools_path: Path to london_schools.csv
        imd_path: Path to imd_lookup.csv
        crime_path: Path to crime_cache.csv
        top_n: If provided, return only the top N schools

    Returns:
        Ranked pandas DataFrame of schools.
    """
    # 1. Geocode user postcode
    user_lat, user_lon = postcode_to_latlon(postcode)
    if user_lat is None or user_lon is None:
        raise ValueError(f"Could not geocode postcode: {postcode}")

    # 2. Load schools
    df = load_schools(schools_path)

    # 3. Filter by phase
    df = filter_by_phase(df, phase=phase)

    # 4. Filter by distance (and compute Distance_km)
    df = filter_by_distance(df, user_lat=user_lat, user_lon=user_lon, max_km=max_distance_km)

    if df.empty:
        return df

    # 5. Enrich with IMD, crime, Ofsted badge
    df = enrich(df, imd_path=imd_path, crime_path=crime_path)

    # 6. Score schools
    df = score_schools(df, weights=weights or DEFAULT_WEIGHTS)

    # 7. Add offer probability
    df = add_probability_column(df)

    # 8. Optionally limit to top N
    if top_n is not None:
        df = df.head(top_n).reset_index(drop=True)

    return df


__all__ = [
    "match_schools",
    "load_schools",
    "postcode_to_latlon",
    "filter_by_phase",
    "filter_by_distance",
    "enrich",
    "score_schools",
    "add_probability_column",
    "DEFAULT_WEIGHTS",
]

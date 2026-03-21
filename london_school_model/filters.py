from typing import Optional
import pandas as pd

from .utils import haversine
from .loader import PRIMARY_PHASES, SECONDARY_PHASES


# ---------------------------------------------------------
# Phase filtering
# ---------------------------------------------------------

def filter_by_phase(df: pd.DataFrame, phase: Optional[str] = None) -> pd.DataFrame:
    """
    Filter schools by phase: 'primary', 'secondary', or None (no filter).

    Args:
        df: DataFrame of schools
        phase: 'primary', 'secondary', or None

    Returns:
        Filtered DataFrame
    """
    if phase is None:
        return df

    phase = phase.lower().strip()

    if phase == "primary":
        allowed = PRIMARY_PHASES
    elif phase == "secondary":
        allowed = SECONDARY_PHASES
    else:
        raise ValueError("phase must be 'primary', 'secondary', or None")

    return df[df["Phase"].isin(allowed)].copy()


# ---------------------------------------------------------
# Distance filtering
# ---------------------------------------------------------

def filter_by_distance(
    df: pd.DataFrame,
    user_lat: float,
    user_lon: float,
    max_km: Optional[float] = None
) -> pd.DataFrame:
    """
    Add a Distance_km column and optionally filter by max distance.

    Args:
        df: DataFrame of schools
        user_lat: latitude of user postcode
        user_lon: longitude of user postcode
        max_km: maximum distance in km (optional)

    Returns:
        DataFrame with Distance_km column, optionally filtered
    """
    df = df.copy()

    df["Distance_km"] = df.apply(
        lambda row: haversine(
            user_lat,
            user_lon,
            row["Latitude"],
            row["Longitude"]
        ),
        axis=1
    )

    if max_km is not None:
        df = df[df["Distance_km"] <= max_km].copy()

    return df

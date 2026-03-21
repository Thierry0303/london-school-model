import math
import pandas as pd

# ---------------------------------------------------------
# Haversine distance
# ---------------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    """
    Compute the great-circle distance between two points on Earth (in km).

    Returns:
        float: distance in kilometres
    """
    if any(v is None for v in [lat1, lon1, lat2, lon2]):
        return None

    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ---------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------

def minmax_normalise(series: pd.Series):
    """
    Normalise a pandas Series to the range [0, 1].

    If all values are identical, returns 0 for all rows.
    """
    if series.nunique() <= 1:
        return pd.Series([0] * len(series), index=series.index)

    min_val = series.min()
    max_val = series.max()

    return (series - min_val) / (max_val - min_val)


def invert(series: pd.Series):
    """
    Invert a normalised score: 1 becomes 0, 0 becomes 1.
    Useful when lower values are better (e.g., distance).
    """
    return 1 - series


# ---------------------------------------------------------
# Safe numeric conversion
# ---------------------------------------------------------

def to_float(value):
    """
    Convert a value to float safely.
    Returns None if conversion fails.
    """
    try:
        return float(value)
    except Exception:
        return None

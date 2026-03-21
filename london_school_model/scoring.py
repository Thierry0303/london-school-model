import pandas as pd
from .utils import minmax_normalise, invert


# ---------------------------------------------------------
# Default weights
# ---------------------------------------------------------

DEFAULT_WEIGHTS = {
    "distance": 0.35,
    "oversub": 0.25,
    "ofsted": 0.20,
    "imd": 0.10,
    "crime": 0.10,
}


# ---------------------------------------------------------
# Ofsted → numeric score
# ---------------------------------------------------------

OFSTED_MAP = {
    "Outstanding": 1.0,
    "Good": 0.75,
    "Requires Improvement": 0.25,
    "Inadequate": 0.0,
    "Unknown": 0.5,  # neutral fallback
}


def ofsted_to_score(badge: str) -> float:
    return OFSTED_MAP.get(badge, 0.5)


# ---------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------

def score_schools(df: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    """
    Compute a weighted score for each school.

    Inputs expected in df:
    - Distance_km
    - Oversub Ratio
    - Ofsted Badge
    - IMD Decile
    - Crime Score

    Returns:
        DataFrame with new columns:
        - Distance_score
        - Oversub_score
        - Ofsted_score
        - IMD_score
        - Crime_score
        - Final_score
    """
    df = df.copy()
    weights = weights or DEFAULT_WEIGHTS

    # -----------------------------
    # Distance (lower is better)
    # -----------------------------
    df["Distance_score"] = invert(minmax_normalise(df["Distance_km"]))

    # -----------------------------
    # Oversubscription (lower is better)
    # -----------------------------
    df["Oversub_score"] = invert(minmax_normalise(df["Oversub Ratio"]))

    # -----------------------------
    # Ofsted (higher is better)
    # -----------------------------
    df["Ofsted_score"] = df["Ofsted Badge"].apply(ofsted_to_score)

    # -----------------------------
    # IMD (higher decile = less deprived = better)
    # -----------------------------
    df["IMD_score"] = minmax_normalise(df["IMD Decile"].fillna(df["IMD Decile"].median()))

    # -----------------------------
    # Crime (lower is better)
    # -----------------------------
    df["Crime_score"] = invert(minmax_normalise(df["Crime Score"].fillna(df["Crime Score"].median())))

    # -----------------------------
    # Final weighted score
    # -----------------------------
    df["Final_score"] = (
        df["Distance_score"] * weights["distance"]
        + df["Oversub_score"] * weights["oversub"]
        + df["Ofsted_score"] * weights["ofsted"]
        + df["IMD_score"] * weights["imd"]
        + df["Crime_score"] * weights["crime"]
    )

    return df.sort_values("Final_score", ascending=False).reset_index(drop=True)
"Fail"

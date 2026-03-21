import pandas as pd


# ---------------------------------------------------------
# Load IMD lookup
# ---------------------------------------------------------

def load_imd(path: str = "data/imd_lookup.csv") -> pd.DataFrame:
    """
    Load IMD lookup table.

    Expected columns:
    - Postcode (no spaces, uppercase)
    - IMD Score
    - IMD Decile (1 = most deprived, 10 = least deprived)
    """
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    required = ["Postcode", "IMD Score", "IMD Decile"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required IMD columns: {missing}")

    df["Postcode"] = df["Postcode"].astype(str).str.upper().str.replace(" ", "")
    return df


# ---------------------------------------------------------
# Load crime cache
# ---------------------------------------------------------

def load_crime(path: str = "data/crime_cache.csv") -> pd.DataFrame:
    """
    Load crime lookup table.

    Expected columns:
    - Postcode (no spaces, uppercase)
    - Crime Score (higher = more crime)
    """
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    required = ["Postcode", "Crime Score"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required crime columns: {missing}")

    df["Postcode"] = df["Postcode"].astype(str).str.upper().str.replace(" ", "")
    return df


# ---------------------------------------------------------
# Ofsted badge helper
# ---------------------------------------------------------

def ofsted_badge(rating: str) -> str:
    """
    Convert Ofsted rating into a badge string.
    """
    if not isinstance(rating, str):
        return "Unknown"

    rating = rating.strip().lower()

    if rating in {"outstanding"}:
        return "Outstanding"
    if rating in {"good"}:
        return "Good"
    if rating in {"requires improvement", "ri"}:
        return "Requires Improvement"
    if rating in {"inadequate"}:
        return "Inadequate"

    return "Unknown"


# ---------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------

def enrich(df: pd.DataFrame,
           imd_path: str = "data/imd_lookup.csv",
           crime_path: str = "data/crime_cache.csv") -> pd.DataFrame:
    """
    Enrich the schools DataFrame with:
    - IMD Score
    - IMD Decile
    - Crime Score
    - Ofsted Badge

    Returns:
        DataFrame with new columns added.
    """
    df = df.copy()

    # Load lookup tables
    imd = load_imd(imd_path)
    crime = load_crime(crime_path)

    # Normalise postcode for merging
    df["Postcode_clean"] = df["Postcode"].astype(str).str.upper().str.replace(" ", "")

    # Merge IMD
    df = df.merge(imd, how="left", left_on="Postcode_clean", right_on="Postcode")
    df = df.drop(columns=["Postcode_y"], errors="ignore")
    df = df.rename(columns={"Postcode_x": "Postcode"})

    # Merge crime
    df = df.merge(crime, how="left", left_on="Postcode_clean", right_on="Postcode")
    df = df.drop(columns=["Postcode"], errors="ignore")

    # Ofsted badge
    df["Ofsted Badge"] = df["Ofsted Rating"].apply(ofsted_badge)

    return df

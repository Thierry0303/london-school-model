import pandas as pd

# Define which phases count as primary or secondary
PRIMARY_PHASES = {
    "Primary",
    "Middle deemed primary",
    "All-through"
}

SECONDARY_PHASES = {
    "Secondary",
    "Middle deemed secondary",
    "All-through",
    "Not applicable"
}

def load_schools(path: str = "data/london_schools.csv") -> pd.DataFrame:
    """
    Load and clean the London-wide schools dataset.

    Expected columns:
    - URN
    - School Name
    - Phase
    - Local Authority
    - Postcode
    - Latitude
    - Longitude
    - PAN 2025
    - 1st Pref Apps 2025
    - Ofsted Rating
    """

    df = pd.read_csv(path)

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]

    required = [
        "URN",
        "School Name",
        "Phase",
        "Local Authority",
        "Postcode",
        "Latitude",
        "Longitude",
        "PAN 2025",
        "1st Pref Apps 2025",
        "Ofsted Rating",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in london_schools.csv: {missing}")

    # Clean postcode
    df["Postcode"] = (
        df["Postcode"]
        .astype(str)
        .str.upper()
        .str.replace(" ", "")
    )

    # Convert numeric fields
    df["PAN 2025"] = pd.to_numeric(df["PAN 2025"], errors="coerce").fillna(0).astype(int)
    df["1st Pref Apps 2025"] = pd.to_numeric(df["1st Pref Apps 2025"], errors="coerce").fillna(0).astype(int)

    # Avoid division by zero
    df["PAN 2025"] = df["PAN 2025"].replace(0, 1)

    # Oversubscription ratio
    df["Oversub Ratio"] = (
        df["1st Pref Apps 2025"] / df["PAN 2025"]
    ).replace([float("inf")], 0)

    return df

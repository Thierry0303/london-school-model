import numpy as np
import pandas as pd


def oversub_to_probability(oversub_ratio: float,
                           midpoint: float = 1.0,
                           steepness: float = 4.0) -> float:
    """
    Convert oversubscription ratio into a probability of receiving an offer.

    Args:
        oversub_ratio: 1st pref apps / PAN
        midpoint: ratio where probability = 0.5
        steepness: controls how sharply probability drops

    Returns:
        float in [0, 1]
    """
    if oversub_ratio is None or np.isnan(oversub_ratio):
        return 0.5  # neutral fallback

    # Logistic curve: high oversub → low probability
    return float(1 / (1 + np.exp(steepness * (oversub_ratio - midpoint))))


def add_probability_column(df: pd.DataFrame,
                           midpoint: float = 1.0,
                           steepness: float = 4.0) -> pd.DataFrame:
    """
    Add a 'Offer_Probability' column to the DataFrame.

    Args:
        df: DataFrame with 'Oversub Ratio'
        midpoint: logistic midpoint
        steepness: logistic steepness

    Returns:
        DataFrame with Offer_Probability column
    """
    df = df.copy()
    df["Offer_Probability"] = df["Oversub Ratio"].apply(
        lambda r: oversub_to_probability(r, midpoint, steepness)
    )
    return df

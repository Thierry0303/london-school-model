"""London School Model - Data loader module"""
import pandas as pd

def load_schools(filepath):
    """Load schools data from CSV file"""
    return pd.read_csv(filepath)

def load_imd_data(filepath):
    """Load IMD (Index of Multiple Deprivation) data from CSV"""
    return pd.read_csv(filepath)

def load_crime_data(filepath):
    """Load crime statistics data from cache"""
    return pd.read_csv(filepath)
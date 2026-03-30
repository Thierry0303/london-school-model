"""
scripts/process_data.py
Regenerate data/schools.json from source CSVs.
Run from the project root: python3 scripts/process_data.py
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_PATH = DATA_DIR / "schools.json"

QUALITY_MAP = {1: 'Outstanding', 2: 'Good', 3: 'Requires improvement', 4: 'Inadequate'}
OFSTED_SCORES = {1: 100, 2: 80, 3: 40, 4: 0}


def load_ofsted():
    path = DATA_DIR / "ofsted.csv"
    df = pd.read_csv(path, encoding='latin1')
    # Filter London only
    df = df[df['Ofsted region'] == 'London'].copy()
    print(f"  Loaded {len(df)} London schools from Ofsted data")
    return df


def load_imd():
    path = DATA_DIR / "imd_lookup.csv"
    if not path.exists():
        print("  imd_lookup.csv not found, skipping IMD enrichment")
        return None
    return pd.read_csv(path)


def process(df, imd_df=None):
    cols = {
        'URN': 'urn',
        'School name': 'name',
        'Local authority': 'local_authority',
        'Postcode': 'postcode',
        'Ofsted phase': 'phase',
        'Type of education': 'school_type',
        'Admissions policy': 'admissions',
        'Sixth form': 'sixth_form',
        'Total number of pupils': 'pupils',
        'Statutory lowest age': 'age_from',
        'Statutory highest age': 'age_to',
        'Quality of education': 'quality_raw',
        'Behaviour and attitudes': 'behaviour_raw',
        'Personal development': 'personal_dev_raw',
        'Effectiveness of leadership and management': 'leadership_raw',
        'Safeguarding is effective': 'safeguarding',
        'Inspection start date': 'inspection_date',
        'The income deprivation affecting children index (IDACI) quintile': 'idaci_quintile',
        'Web link': 'ofsted_url',
        'Designated religious character': 'religious_character',
        'Multi-academy trust name': 'mat_name',
        'Parliamentary constituency': 'constituency',
    }

    df = df.rename(columns={k: v for k, v in cols.items() if k in df.columns})

    df['quality_label'] = df['quality_raw'].map(QUALITY_MAP)
    df['ofsted_score'] = df['quality_raw'].map(OFSTED_SCORES)
    df['score_band'] = df['quality_label'].fillna('Unknown')

    return df


def clean_val(val):
    if val is None:
        return None
    if isinstance(val, float) and np.isnan(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        if np.isnan(val):
            return None
        iv = int(val)
        return iv if val == iv else float(val)
    return val


def to_records(df):
    keep = [
        'urn', 'name', 'local_authority', 'postcode', 'phase', 'school_type',
        'admissions', 'sixth_form', 'pupils', 'age_from', 'age_to',
        'quality_raw', 'behaviour_raw', 'personal_dev_raw', 'leadership_raw',
        'safeguarding', 'inspection_date', 'idaci_quintile', 'ofsted_url',
        'religious_character', 'mat_name', 'constituency',
        'quality_label', 'ofsted_score', 'score_band',
    ]
    cols = [c for c in keep if c in df.columns]
    records = []
    for _, row in df.iterrows():
        r = {c: clean_val(row.get(c)) for c in cols}
        records.append(r)
    return records


def main():
    print("Processing London Schools data...")
    df = load_ofsted()
    imd_df = load_imd()
    df = process(df, imd_df)
    records = to_records(df)

    with open(OUT_PATH, 'w') as f:
        json.dump(records, f, indent=2)

    print(f"\n✅ Wrote {len(records)} schools to {OUT_PATH}")
    print(f"   Score bands: { {r['score_band']: sum(1 for x in records if x['score_band']==r['score_band']) for r in records} }")


if __name__ == '__main__':
    main()

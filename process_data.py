"""
scripts/process_data.py
Rebuild schools.json from GIAS + Ofsted + IMD sources.

Source files expected in data/:
  - catholic_schools_with_coords.csv  (GIAS full register — all England schools with coords)
  - ofsted.csv                         (Ofsted inspection export)
  - imd_lookup.csv                     (IMD deprivation by LSOA)

Run from project root:
  python3 scripts/process_data.py
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_PATH = DATA_DIR / "schools.json"

QUALITY_MAP = {1: 'Outstanding', 2: 'Good', 3: 'Requires improvement', 4: 'Inadequate'}
OFSTED_SCORES = {1: 100, 2: 80, 3: 40, 4: 0}


def load_gias():
    path = DATA_DIR / "catholic_schools_with_coords.csv"
    gias = pd.read_csv(path, low_memory=False)
    london = gias[
        (gias['GOR (name)'] == 'London') &
        (gias['EstablishmentStatus (name)'] == 'Open')
    ].copy()
    print(f"  GIAS open London schools: {len(london)}")
    return london


def load_ofsted():
    path = DATA_DIR / "ofsted.csv"
    df = pd.read_csv(path, encoding='latin1')
    df = df[df['Ofsted region'] == 'London'].copy()
    print(f"  Ofsted London records: {len(df)}")
    return df


def load_imd():
    path = DATA_DIR / "imd_lookup.csv"
    imd = pd.read_csv(path)
    imd = imd.rename(columns={
        'LSOA code (2021)': 'lsoa_code',
        'Index of Multiple Deprivation (IMD) Rank (where 1 is most deprived)': 'imd_rank',
        'Index of Multiple Deprivation (IMD) Decile (where 1 is most deprived 10% of LSOAs)': 'imd_decile',
    })[['lsoa_code', 'imd_rank', 'imd_decile']]
    max_rank = imd['imd_rank'].max()
    imd['imd_score'] = ((imd['imd_rank'] / max_rank) * 100).round(1)
    print(f"  IMD records: {len(imd)}")
    return imd


def build(gias_df, ofsted_df, imd_df):
    # GIAS base columns
    gias_cols = {
        'URN': 'urn', 'EstablishmentName': 'name',
        'LA (name)': 'local_authority', 'Postcode': 'postcode',
        'PhaseOfEducation (name)': 'phase',
        'TypeOfEstablishment (name)': 'school_type',
        'StatutoryLowAge': 'age_from', 'StatutoryHighAge': 'age_to',
        'OfficialSixthForm (name)': 'sixth_form',
        'Gender (name)': 'gender',
        'AdmissionsPolicy (name)': 'admissions',
        'NumberOfPupils': 'pupils', 'SchoolCapacity': 'capacity',
        'NumberOfBoys': 'num_boys', 'NumberOfGirls': 'num_girls',
        'PercentageFSM': 'pct_fsm',
        'ReligiousCharacter (name)': 'religious_character',
        'Diocese (name)': 'diocese',
        'Trusts (name)': 'trust_name',
        'SchoolWebsite': 'website',
        'TelephoneNum': 'telephone',
        'HeadFirstName': 'head_first', 'HeadLastName': 'head_last',
        'Street': 'street', 'Town': 'town',
        'Latitude': 'lat', 'Longitude': 'lng',
        'LSOA (code)': 'lsoa_code',
        'ParliamentaryConstituency (name)': 'constituency',
    }
    base = gias_df.rename(columns={k: v for k, v in gias_cols.items() if k in gias_df.columns})
    base = base[[v for v in gias_cols.values() if v in base.columns]].copy()

    # Ofsted columns
    ofsted_cols = {
        'URN': 'urn',
        'Quality of education': 'quality_raw',
        'Behaviour and attitudes': 'behaviour_raw',
        'Personal development': 'personal_dev_raw',
        'Effectiveness of leadership and management': 'leadership_raw',
        'Safeguarding is effective': 'safeguarding',
        'Inspection start date': 'inspection_date',
        'Web link': 'ofsted_url',
        'The income deprivation affecting children index (IDACI) quintile': 'idaci_quintile',
        'Multi-academy trust name': 'mat_name',
        'Total number of pupils': 'ofsted_pupils',
    }
    ofsted = ofsted_df.rename(columns={k: v for k, v in ofsted_cols.items() if k in ofsted_df.columns})
    ofsted = ofsted[[v for v in ofsted_cols.values() if v in ofsted.columns]].copy()
    ofsted['quality_raw'] = ofsted['quality_raw'].apply(lambda x: x if x in [1, 2, 3, 4] else None)
    ofsted['quality_label'] = ofsted['quality_raw'].map(QUALITY_MAP)
    ofsted['ofsted_score'] = ofsted['quality_raw'].map(OFSTED_SCORES)

    # Join
    base = base.merge(ofsted, on='urn', how='left')
    base = base.merge(imd_df, on='lsoa_code', how='left')

    # Derived fields
    base['score_band'] = base['quality_label'].apply(lambda x: x if pd.notna(x) else 'Not yet rated')
    base['head_name'] = (
        base.get('head_first', pd.Series([''] * len(base))).fillna('') + ' ' +
        base.get('head_last', pd.Series([''] * len(base))).fillna('')
    ).str.strip().apply(lambda x: x or None)
    base = base.drop(columns=[c for c in ['head_first', 'head_last'] if c in base.columns])

    return base


def clean(val):
    if val is None: return None
    if isinstance(val, float) and np.isnan(val): return None
    if isinstance(val, (np.integer,)): return int(val)
    if isinstance(val, (np.floating,)):
        if np.isnan(val): return None
        iv = int(val)
        return iv if val == iv else round(float(val), 6)
    if isinstance(val, str): return val.strip() or None
    return val


def main():
    print("Building schools.json...")
    gias = load_gias()
    ofsted = load_ofsted()
    imd = load_imd()
    df = build(gias, ofsted, imd)

    records = [{col: clean(row.get(col)) for col in df.columns} for _, row in df.iterrows()]

    with open(OUT_PATH, 'w') as f:
        json.dump(records, f, indent=2)

    from collections import Counter
    bands = Counter(r['score_band'] for r in records)
    print(f"\n✅ Written {len(records)} schools to {OUT_PATH}")
    print(f"   Bands: {dict(bands)}")
    print(f"   With IMD: {sum(1 for r in records if r.get('imd_score') is not None)}")
    print(f"   With coords: {sum(1 for r in records if r.get('lat') is not None)}")


if __name__ == '__main__':
    main()

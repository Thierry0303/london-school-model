# London School Model


A Python package for analyzing and modeling London schools data.

## Directory Structure

```
london-school-model/
├── data/
│   ├── london_schools.csv
│   ├── imd_lookup.csv
│   └── crime_cache.csv
├── london_school_model/
│   ├── __init__.py
│   ├── loader.py
│   ├── geocode.py
│   ├── enrich.py
│   ├── scoring.py
│   ├── probability.py
│   ├── filters.py
│   └── utils.py
├── notebooks/
│   └── build_dataset.ipynb
├── tests/
│   └── test_scoring.py
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Import the package and start using it:

```python
from london_school_model import loader, scoring
```

## Testing

Run tests with:

```bash
python -m pytest tests/
```

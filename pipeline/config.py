"""
Pipeline configuration: data source registry, province mappings, output paths.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAKE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lake")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Province name normalization mapping
# StatCan uses full names; our dashboards use these canonical forms
PROVINCE_CANONICAL = {
    "Newfoundland and Labrador": "Newfoundland & Labrador",
    "Prince Edward Island": "Prince Edward Island",
    "Nova Scotia": "Nova Scotia",
    "New Brunswick": "New Brunswick",
    "Quebec": "Quebec",
    "Ontario": "Ontario",
    "Manitoba": "Manitoba",
    "Saskatchewan": "Saskatchewan",
    "Alberta": "Alberta",
    "British Columbia": "British Columbia",
    "Yukon": "Yukon",
    "Northwest Territories": "Northwest Territories",
    "Nunavut": "Nunavut",
}

PROVINCES = [
    "British Columbia",
    "Alberta",
    "Saskatchewan",
    "Manitoba",
    "Ontario",
    "Quebec",
    "New Brunswick",
    "Nova Scotia",
    "Prince Edward Island",
    "Newfoundland & Labrador",
]

TERRITORIES = [
    "Yukon",
    "Northwest Territories",
    "Nunavut",
]

# Canonical ordering: Canada first, then provinces (west to east), then territories
PROVINCES_ORDERED = ["Canada"] + PROVINCES + TERRITORIES

# Legacy: fiscal data files historically used "Federal" for the national entity.
# We now normalize to "Canada" everywhere.
FISCAL_ENTITY_NAME = "Canada"

# StatCan bulk CSV download URL pattern
STATCAN_URL = "https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"

# Data source registry
# Each entry: table_id -> { description, outputs (list of output JSON filenames) }
SOURCES = {
    # Economy
    "36-10-0222": {
        "description": "GDP per capita by province",
        "outputs": ["economy-gdp-per-capita.json"],
    },
    "14-10-0064": {
        "description": "Median weekly wages by province",
        "outputs": ["economy-median-weekly-wages.json"],
    },
    "14-10-0288": {
        "description": "Employment by sector (public/private)",
        "outputs": ["economy-employment.json"],
    },
    # Crime
    "35-10-0026": {
        "description": "Crime Severity Index (total, violent, non-violent)",
        "outputs": [
            "crime-severity-index.json",
            "crime-breakdown.json",
        ],
    },
    "35-10-0068": {
        "description": "Homicide rate per 100K",
        "outputs": ["crime-homicide-rate.json"],
    },
    # Demographics
    "17-10-0005": {
        "description": "Population estimates by province",
        "outputs": [
            "demographics-population.json",
            "demographics-population-growth.json",
        ],
    },
    "17-10-0014": {
        "description": "International immigration by province",
        "outputs": ["demographics-international-immigration.json"],
    },
    "17-10-0045": {
        "description": "Interprovincial migration",
        "outputs": ["demographics-interprovincial-migration.json"],
    },
    # Housing
    "18-10-0205": {
        "description": "New Housing Price Index",
        "outputs": ["housing-new-price-index.json"],
    },
    "34-10-0135": {
        "description": "Housing starts by province (CMHC)",
        "outputs": ["housing-starts.json"],
    },
    # NOTE: 34-10-0127 (rental vacancy) has CMA-level data only, not provincial.
    # housing-rental-vacancy-rate.json is maintained manually.
    # We still download it for reference but don't auto-transform it.
    "34-10-0127": {
        "description": "Rental vacancy rate by CMA (CMHC) — reference only",
        "outputs": [],
    },
    # Fiscal
    "36-10-0450": {
        "description": "Provincial/territorial government revenue and spending",
        "outputs": [
            "fiscal-government-revenue.json",
            "fiscal-government-spending.json",
        ],
    },
}

# Manual data sources (not downloadable from StatCan)
MANUAL_SOURCES = {
    "fiscal-deficit": {
        "description": "Federal/provincial deficit - Dept of Finance Fiscal Reference Tables",
        "outputs": ["fiscal-deficit.json", "fiscal-net-debt.json"],
        "note": "Manual entry from Department of Finance Fiscal Reference Tables 2025",
    },
}

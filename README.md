# Transportation ROI Analysis: OKI Region

## Overview
A fiscal productivity analysis of the 8-county Ohio-Kentucky-Indiana (OKI) metropolitan region, measuring whether federal transportation investment is allocated proportionally to property tax revenue generation. Key finding: urban tracts generate ~17x more property tax revenue per acre than sprawl areas, yet suburban areas receive the highest per-acre federal investment.

## Key Data Science Skills
*   **Fiscal Impact Modeling:** Estimating per-acre property tax productivity at the census tract level.
*   **Federal Award Attribution:** Mapping USASpending.gov awards to census geographies.
*   **Geospatial Analysis:** Joining tract-level fiscal data with Overture Maps infrastructure layers.
*   **Comparative Density Analysis:** Classifying tracts by density class to expose cross-subsidy patterns.

## Tech Stack
*   **R (sf, leaflet, tidyverse):** Spatial analysis and interactive mapping.
*   **Python:** Federal award fetching, Overture Maps querying, census data extraction.
*   **Quarto:** Report generation.

## Data Sources
*   **USASpending.gov:** Federal transportation awards by geography.
*   **Overture Maps Foundation:** Road network and infrastructure layers.
*   **US Census Bureau:** ACS 5-Year Estimates, tract boundaries.

## Key Findings
*   Urban tracts: highest revenue per acre, lowest federal investment per acre.
*   Suburban tracts: highest federal investment per acre, lowest revenue per acre.
*   Pattern consistent with a cross-subsidy from urban to low-density areas.

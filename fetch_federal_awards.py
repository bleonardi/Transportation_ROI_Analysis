import requests
import json
import pandas as pd
import time

# OKI 8-county region FIPS mapping
OKI_COUNTIES = [
    {"state": "OH", "county": "061", "name": "Hamilton"},
    {"state": "OH", "county": "017", "name": "Butler"},
    {"state": "OH", "county": "025", "name": "Clermont"},
    {"state": "OH", "county": "165", "name": "Warren"},
    {"state": "KY", "county": "015", "name": "Boone"},
    {"state": "KY", "county": "117", "name": "Kenton"},
    {"state": "KY", "county": "037", "name": "Campbell"},
    {"state": "IN", "county": "029", "name": "Dearborn"}
]

AWARD_TYPE_GROUPS = {
    "grants": ["02", "03", "04", "05"],
    "contracts": ["A", "B", "C", "D"]
}

API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def fetch_awards(state, county, name, type_codes):
    print(f"Fetching {type_codes} awards for {name} County, {state}...")
    
    payload = {
        "filters": {
            "place_of_performance_locations": [
                {
                    "country": "USA",
                    "state": state,
                    "county": county
                }
            ],
            "time_period": [
                {
                    "start_date": "2019-10-01",
                    "end_date": "2024-09-30"
                }
            ],
            "agencies": [
                {
                    "type": "funding",
                    "tier": "toptier",
                    "name": "Department of Transportation"
                }
            ],
            "award_type_codes": type_codes
        },
        "fields": [
            "Award ID",
            "Recipient Name",
            "Start Date",
            "End Date",
            "Award Amount",
            "Description",
            "Place of Performance City Name",
            "Place of Performance County Name",
            "Award Type"
        ],
        "limit": 100,
        "page": 1
    }
    
    all_awards = []
    page = 1
    
    while True:
        payload["page"] = page
        response = requests.post(API_URL, json=payload)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        results = data.get("results", [])
        all_awards.extend(results)
        
        if not data.get("page_metadata", {}).get("has_next_page"):
            break
            
        page += 1
        time.sleep(0.5)
        
    return all_awards

if __name__ == "__main__":
    combined_awards = []
    for county in OKI_COUNTIES:
        for group_name, codes in AWARD_TYPE_GROUPS.items():
            awards = fetch_awards(county["state"], county["county"], county["name"], codes)
            combined_awards.extend(awards)
        
    df = pd.DataFrame(combined_awards)
    if not df.empty:
        output_path = "Transportation_ROI_Analysis/data/oki_federal_awards.csv"
        df.to_csv(output_path, index=False)
        print(f"\nSaved {len(df)} awards to {output_path}")
    else:
        print("\nNo awards found.")

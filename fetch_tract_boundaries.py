import requests
import json
import os

OKI_COUNTIES = [
    {"state": "39", "counties": "('061','017','025','165')", "name": "OH"},
    {"state": "21", "counties": "('015','117','037')", "name": "KY"},
    {"state": "18", "counties": "('029')", "name": "IN"}
]

BASE_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/8/query"

def fetch_tracts():
    all_features = []
    for region in OKI_COUNTIES:
        print(f"Fetching tracts for {region['name']}...")
        params = {
            "where": f"STATE = '{region['state']}' AND COUNTY IN {region['counties']}",
            "outFields": "GEOID",
            "f": "geojson",
            "outSR": "4326"
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            all_features.extend(data.get("features", []))
        else:
            print(f"Error fetching {region['name']}: {response.status_code}")
            
    combined = {
        "type": "FeatureCollection",
        "features": all_features
    }
    
    output_path = "Transportation_ROI_Analysis/data/oki_tracts.geojson"
    with open(output_path, "w") as f:
        json.dump(combined, f)
    print(f"Saved {len(all_features)} tracts to {output_path}")

if __name__ == "__main__":
    fetch_tracts()

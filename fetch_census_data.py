import requests
import pandas as pd

# OKI 8-county region
OKI_COUNTIES = [
    {"state": "39", "county": "061", "name": "Hamilton"},
    {"state": "39", "county": "017", "name": "Butler"},
    {"state": "39", "county": "025", "name": "Clermont"},
    {"state": "39", "county": "165", "name": "Warren"},
    {"state": "21", "county": "015", "name": "Boone"},
    {"state": "21", "county": "117", "name": "Kenton"},
    {"state": "21", "county": "037", "name": "Campbell"},
    {"state": "18", "county": "029", "name": "Dearborn"}
]

# Variables:
# B01003_001E: Total Population
# B25001_001E: Total Housing Units
# B25077_001E: Median Home Value
VARS = "B01003_001E,B25001_001E,B25077_001E"

def fetch_census_data():
    all_data = []
    for region in OKI_COUNTIES:
        print(f"Fetching Census data for {region['name']}...")
        url = f"https://api.census.gov/data/2022/acs/acs5?get=NAME,{VARS}&for=tract:*&in=state:{region['state']}&in=county:{region['county']}"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                # First row is header
                df = pd.DataFrame(data[1:], columns=data[0])
                all_data.append(df)
            except Exception as e:
                print(f"Error parsing JSON for {region['name']}: {e}")
                print(f"Response text: {response.text[:200]}")
        else:
            print(f"Error fetching {region['name']}: {response.status_code}")
            print(f"Response text: {response.text[:200]}")
            
    if all_data:
        combined = pd.concat(all_data)
        # Create GEOID
        combined['GEOID'] = combined['state'] + combined['county'] + combined['tract']
        combined = combined.rename(columns={
            "B01003_001E": "Population",
            "B25001_001E": "Housing_Units",
            "B25077_001E": "Median_Home_Value"
        })
        # Clean numeric
        for col in ["Population", "Housing_Units", "Median_Home_Value"]:
            combined[col] = pd.to_numeric(combined[col], errors='coerce')
            
        output_path = "Transportation_ROI_Analysis/data/oki_census_data.csv"
        combined.to_csv(output_path, index=False)
        print(f"Saved {len(combined)} tracts to {output_path}")

if __name__ == "__main__":
    fetch_census_data()

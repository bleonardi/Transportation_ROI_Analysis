import duckdb
import pandas as pd
import json
import os

# OKI Bbox
BBOX = {
    "xmin": -85.2,
    "xmax": -84.0,
    "ymin": 38.8,
    "ymax": 39.6
}

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

# 1. Load Tracts into DuckDB
print("Loading Tract boundaries...")
con.execute(f"CREATE TABLE tracts AS SELECT GEOID, geom FROM ST_Read('Transportation_ROI_Analysis/data/oki_tracts.geojson')")

# 2. Process Awards
awards_df = pd.read_csv("Transportation_ROI_Analysis/data/oki_awards_with_locations.csv")
high_conf = awards_df[awards_df['Confidence'].isin(['High', 'Medium'])].copy()

results = []

print(f"Mapping {len(high_conf)} awards using local cache (names + routes)...")

# Load cached segments into a table
con.execute("CREATE TABLE segments AS SELECT * FROM read_parquet('Transportation_ROI_Analysis/data/oki_transportation_segments.parquet')")

for idx, row in high_conf.iterrows():
    award_id = row['Award ID']
    amount = row['Award Amount']
    route = row['Primary_Route']
    detail = row['Location_Detail']
    
    if not isinstance(route, str):
        continue
        
    filters = []
    
    # 1. Try matching by route ref
    import re
    route_match = re.search(r'([A-Z]+)-(\d+)', route)
    if route_match:
        prefix, num = route_match.groups()
        if prefix == "I":
            filters.append(f"len(list_filter(routes, x -> x.ref = '{num}' AND x.network = 'US:I')) > 0")
        elif prefix == "US":
            filters.append(f"len(list_filter(routes, x -> x.ref = '{num}' AND x.network = 'US:US')) > 0")
        elif prefix in ["SR", "KY"]:
            filters.append(f"len(list_filter(routes, x -> x.ref = '{num}')) > 0")
    
    # 2. Try matching by name variants
    variants = [route, route.replace("-", " "), route.replace("-", "")]
    # Clean up variants for SQL
    variants = [v.replace("'", "''") for v in variants if isinstance(v, str)]
    
    if detail and isinstance(detail, str):
        variants.append(detail.replace("'", "''"))
    
    if variants:
        name_filters = " OR ".join([f"name ILIKE '%{v}%'" for v in variants])
        filters.append(f"({name_filters})")
    
    if not filters:
        continue
        
    combined_filter = " OR ".join(filters)
    # print(f"DEBUG: {route} -> {combined_filter}")
    
    query = f"""
    WITH matched_segments AS (
        SELECT geometry
        FROM segments
        WHERE {combined_filter}
    ),
    intersected AS (
        SELECT t.GEOID, ST_Length(ST_Intersection(s.geometry, ST_SetCRS(t.geom, 'OGC:CRS84'))) as overlap_len
        FROM matched_segments s, tracts t
        WHERE ST_Intersects(s.geometry, ST_SetCRS(t.geom, 'OGC:CRS84'))
    )
    SELECT GEOID, SUM(overlap_len) as total_len
    FROM intersected
    GROUP BY GEOID
    """
    
    try:
        mapping = con.execute(query).df()
        if not mapping.empty:
            total_len = mapping['total_len'].sum()
            mapping['assigned_amount'] = (mapping['total_len'] / total_len) * amount
            mapping['Award ID'] = award_id
            results.append(mapping[['Award ID', 'GEOID', 'assigned_amount']])
            # print(f"Matched {route} to {len(mapping)} tracts.")
        else:
            pass
    except Exception as e:
        # print(f"Error matching {route}: {e}")
        pass

if results:
    final_mapping = pd.concat(results)
    final_mapping.to_csv("Transportation_ROI_Analysis/data/award_tract_mapping.csv", index=False)
    print(f"\nSaved mapping for {len(final_mapping['Award ID'].unique())} awards.")
else:
    print("\nNo awards could be mapped to segments.")

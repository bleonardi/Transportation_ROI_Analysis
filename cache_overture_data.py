import duckdb
import os

BBOX = {
    "xmin": -85.2,
    "xmax": -84.0,
    "ymin": 38.8,
    "ymax": 39.6
}

RELEASE_PATH = "s3://overturemaps-us-west-2/release/2026-05-20.0"

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("SET s3_region='us-west-2';")

output_path = "Transportation_ROI_Analysis/data/oki_transportation_segments.parquet"

if not os.path.exists(output_path):
    print("Caching Overture Transportation segments for OKI region...")
    query = f"""
    COPY (
        SELECT 
            names.primary as name,
            routes,
            subtype,
            class,
            geometry
        FROM read_parquet('{RELEASE_PATH}/theme=transportation/type=segment/*.parquet')
        WHERE bbox.xmin > {BBOX['xmin']} AND bbox.xmax < {BBOX['xmax']}
          AND bbox.ymin > {BBOX['ymin']} AND bbox.ymax < {BBOX['ymax']}
    ) TO '{output_path}' (FORMAT 'PARQUET')
    """
    con.execute(query)
    print(f"Cached segments to {output_path}")
else:
    print(f"Cache already exists at {output_path}")

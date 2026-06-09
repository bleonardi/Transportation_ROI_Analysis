import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")
con.execute("CREATE TABLE segments AS SELECT * FROM read_parquet('Transportation_ROI_Analysis/data/oki_transportation_segments.parquet')")
con.execute("CREATE TABLE tracts AS SELECT GEOID, geom FROM ST_Read('Transportation_ROI_Analysis/data/oki_tracts.geojson')")

query = """
    WITH matched_segments AS (
        SELECT geometry
        FROM segments
        WHERE len(list_filter(routes, x -> x.ref = '75' AND x.network = 'US:I')) > 0
    ),
    intersected AS (
        SELECT t.GEOID, ST_Length(ST_Intersection(s.geometry, ST_Transform(t.geom, 'OGC:CRS84'))) as overlap_len
        FROM matched_segments s, tracts t
        WHERE ST_Intersects(s.geometry, ST_Transform(t.geom, 'OGC:CRS84'))
    )
    SELECT GEOID, SUM(overlap_len) as total_len
    FROM intersected
    GROUP BY GEOID
"""

df = con.execute(query).df()
print(df)

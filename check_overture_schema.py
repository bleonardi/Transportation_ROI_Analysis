import duckdb
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("SET s3_region='us-west-2';")
url = "s3://overturemaps-us-west-2/release/2026-05-20.0/theme=transportation/type=segment/*.parquet"
schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{url}') LIMIT 0").df()
print(schema[['column_name', 'column_type']])

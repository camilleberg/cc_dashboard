# this is to load all the parquet files and put them into one

# https://github.com/observablehq/framework/pull/1386#issue-2311499272
duckdb :memory: <<EOF
COPY (
    SELECT *
    FROM './src/data/input/cd119_geographies/*.parquet') 
    to '/dev/stdout' (format parquet, codec zstd)
EOF
duckdb :memory: <<EOF
copy (select * from range(10) tbl(i)) to '/dev/stdout' (format parquet, codec zstd)
EOF
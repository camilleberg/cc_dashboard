DIR="$(cd "$(dirname "$0")" && pwd)"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# run the sibling loaders; their stdout goes to temp files
sh "$DIR/../age/cc_data_age_table.parquet.sh"        > "$TMP/cc_data_all.parquet"

duckdb :memory: <<EOF
COPY (
  SELECT a.*,
         h.* EXCLUDE (ccn20, cd119, State),
         e.* EXCLUDE (ccn20, cd119, State),
         l.* EXCLUDE (ccn20, cd119, State)
  FROM '$TMP/age.parquet' a
  JOIN '$TMP/housing.parquet' h USING (ccn20)
  JOIN '$TMP/emp.parquet' e USING (ccn20)
  JOIN '$TMP/lang.parquet' l USING (ccn20)
) TO '/dev/stdout' (FORMAT parquet, CODEC zstd)
EOF
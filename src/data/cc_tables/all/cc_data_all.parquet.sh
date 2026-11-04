DIR="$(cd "$(dirname "$0")" && pwd)"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# run the sibling loaders; their stdout goes to temp files
sh "$DIR/../age/cc_data_age_table.parquet.sh"        > "$TMP/age.parquet"
sh "$DIR/../housing/cc_data_housing_table.parquet.sh" > "$TMP/housing.parquet"
sh "$DIR/../emp/cc_data_employment_table.parquet.sh"  > "$TMP/emp.parquet"
sh "$DIR/../lang/cc_data_lang_table.parquet.sh"       > "$TMP/lang.parquet"
sh "$DIR/../../ccn20_geo.parquet.sh"       > "$TMP/geo.parquet"

duckdb :memory: <<EOF
COPY (
  SELECT a.*,
         h.* EXCLUDE (ccn20, cd119, State),
         e.* EXCLUDE (ccn20, cd119, State),
         l.* EXCLUDE (ccn20, cd119, State),
         g.* EXCLUDE (ccn20, cd119, State)
  FROM '$TMP/age.parquet' a
  JOIN '$TMP/housing.parquet' h USING (ccn20)
  JOIN '$TMP/emp.parquet' e USING (ccn20)
  JOIN '$TMP/lang.parquet' l USING (ccn20)
  JOIN '$TMP/geo.parquet' g USING (ccn20)
) TO '/dev/stdout' (FORMAT parquet, CODEC zstd)
EOF
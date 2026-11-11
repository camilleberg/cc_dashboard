DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
  SELECT
    ccn20,
    cd119,
    State,
    tot_pop,
    ageGroup_under18,
    ageGroup_18_65,
    ageGroup_over65,
    ageGroup_under18 / NULLIF(tot_pop, 0)::DOUBLE AS age_prop_under18,
    ageGroup_18_65   / NULLIF(tot_pop, 0)::DOUBLE AS age_prop_18_65,
    ageGroup_over65  / NULLIF(tot_pop, 0)::DOUBLE AS age_prop_over65
  FROM '$DIR/../../cc_data_updated.parquet'
) TO '/dev/stdout' (FORMAT parquet, CODEC zstd)
EOF
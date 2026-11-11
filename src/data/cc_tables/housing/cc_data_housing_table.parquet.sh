# this is toload the vars for age 

DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
SELECT
    ccn20,
    cd119,
    State,
    tot_housing,
    tot_hholds,
    tot_owned_hholds,
    tot_vacant_units,
    tot_rented_hholds,
  
    tot_hholds 
        / NULLIF(tot_housing, 0)::DOUBLE
        AS housing_occupancy_rate,

    tot_owned_hholds
        / NULLIF(tot_hholds, 0)::DOUBLE
        AS housing_ownership_rate,

    --adding in extra  rates
    1 - housing_occupancy_rate AS housing_vacancy_rate, 
    1 - housing_ownership_rate AS housing_rental_rate,

    FROM './src/data/cc_data_updated.parquet'
) TO '/dev/stdout' (format parquet, codec zstd)
EOF
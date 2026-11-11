# this is toload the vars for age 

DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
SELECT
    cd119,

    SUM(tot_housing) AS tot_housing,
    SUM(tot_hholds) AS tot_hholds,
    SUM(tot_owned_hholds) AS tot_owned_hholds,
    SUM(tot_vacant_units) AS tot_vacant_units,
    SUM(tot_rented_hholds) AS tot_rented_hholds,

    SUM(tot_hholds)
        / NULLIF(SUM(tot_housing), 0)::DOUBLE
        AS housing_occupancy_rate,

    SUM(tot_owned_hholds)
        / NULLIF(SUM(tot_hholds), 0)::DOUBLE
        AS housing_ownership_rate,

    1 - housing_occupancy_rate AS housing_vacancy_rate, 
    1 - housing_ownership_rate AS housing_rental_rate

FROM './src/data/cc_data_updated.parquet'
GROUP BY cd119
) TO '/dev/stdout' (format parquet, codec zstd)
EOF
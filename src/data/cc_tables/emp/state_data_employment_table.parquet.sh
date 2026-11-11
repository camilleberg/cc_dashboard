# this is toload the vars for age 

DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
    SELECT
    State,

    SUM(tot_emp) AS tot_emp,
    SUM(tot_unemp) AS tot_unemp,
    SUM(tot_civilian_lf) AS tot_civilian_lf,
    SUM(tot_working_age_pop) AS tot_working_age_pop,

    SUM(tot_unemp)
        / NULLIF(SUM(tot_civilian_lf), 0)::DOUBLE
        AS unemp_rate3,

    SUM(tot_emp)
        / NULLIF(SUM(tot_civilian_lf), 0)::DOUBLE
        AS emp_rate3,

    SUM(tot_civilian_lf)
        / NULLIF(SUM(tot_working_age_pop), 0)::DOUBLE
        AS lfp_rate,

    SUM(tot_emp)
        / NULLIF(SUM(tot_working_age_pop), 0)::DOUBLE
        AS emp_to_pop,

    FROM './src/data/cc_data_updated.parquet'
    GROUP BY State
) TO '/dev/stdout' (format parquet, codec zstd)
EOF
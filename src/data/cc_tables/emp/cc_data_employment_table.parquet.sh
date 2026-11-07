# this is toload the vars for age 

DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
SELECT
    ccn20,
    cd119,
    State,
    tot_emp, 
    tot_unemp, 
    tot_civilian_lf, 
    tot_working_age_pop,
  
    tot_unemp 
        / NULLIF(tot_civilian_lf, 0)::DOUBLE
        AS unemp_rate3,

    tot_emp 
        / NULLIF(tot_civilian_lf, 0)::DOUBLE
        AS emp_rate3,

    tot_civilian_lf
        / NULLIF(tot_working_age_pop, 0)::DOUBLE
        AS lfp_rate,

    tot_emp 
        / NULLIF(tot_working_age_pop, 0)::DOUBLE
        AS emp_to_pop,   

    FROM './src/data/cc_data_updated.parquet'
) TO '/dev/stdout' (format parquet, codec zstd)
EOF
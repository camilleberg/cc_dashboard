# this is toload the vars for age 

DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
    SELECT
    cd119,

        SUM(tot_pop_5yrs) AS tot_pop_5yrs,
        SUM(tot_english_only) AS tot_english_only, 
        SUM(tot_non_english) AS tot_non_english, 
        SUM(tot_spanish) AS tot_spanish,
    
        SUM(tot_english_only) 
            / NULLIF(SUM(tot_pop_5yrs), 0)::DOUBLE
            AS prop_english_only,

        1 - prop_english_only AS prop_non_english,

        SUM(tot_spanish)
            / NULLIF(SUM(tot_pop_5yrs), 0)::DOUBLE
            AS prop_span,

        SUM(tot_spanish)
            / NULLIF(SUM(tot_non_english), 0)::DOUBLE
            AS prop_span_nonEnglish,  

FROM './src/data/cc_data_updated.parquet'
GROUP BY cd119
) TO '/dev/stdout' (format parquet, codec zstd)
EOF
# this is toload the vars for age 

DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
    SELECT
        ccn20,
        cd119,
        State,
        tot_pop_5yrs, 
        tot_english_only, 
        tot_non_english, 
        tot_spanish,
    
        tot_english_only 
            / NULLIF(tot_pop_5yrs, 0)::DOUBLE
            AS prop_english_only,

        1 - prop_english_only AS prop_non_english,

        tot_spanish
            / NULLIF(tot_pop_5yrs, 0)::DOUBLE
            AS prop_span,

        tot_spanish
            / NULLIF(tot_non_english, 0)::DOUBLE
            AS prop_span_nonEnglish,

    FROM './src/data/cc_data_updated.parquet'
) TO '/dev/stdout' (format parquet, codec zstd)
EOF
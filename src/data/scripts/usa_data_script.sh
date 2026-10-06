DIR="$(cd "$(dirname "$0")" && pwd)"

duckdb :memory: <<EOF
COPY (
    SELECT
        -- age
        SUM(tot_pop)           AS tot_pop,
        SUM(ageGroup_under18)  AS ageGroup_under18,
        SUM(ageGroup_18_65)    AS ageGroup_18_65,
        SUM(ageGroup_over65)   AS ageGroup_over65,
        SUM(ageGroup_under18) / NULLIF(SUM(tot_pop), 0)::DOUBLE AS age_prop_under18,
        SUM(ageGroup_18_65)   / NULLIF(SUM(tot_pop), 0)::DOUBLE AS age_prop_18_65,
        SUM(ageGroup_over65)  / NULLIF(SUM(tot_pop), 0)::DOUBLE AS age_prop_over65,

        -- housing
        SUM(tot_housing)       AS tot_housing,
        SUM(tot_hholds)        AS tot_hholds,
        SUM(tot_owned_hholds)  AS tot_owned_hholds,
        SUM(tot_vacant_units)  AS tot_vacant_units,
        SUM(tot_rented_hholds) AS tot_rented_hholds,

        SUM(tot_hholds)       / NULLIF(SUM(tot_housing), 0)::DOUBLE AS housing_occupancy_rate,
        SUM(tot_owned_hholds) / NULLIF(SUM(tot_hholds), 0)::DOUBLE  AS housing_ownership_rate,
        1 - housing_occupancy_rate AS housing_vacancy_rate,
        1 - housing_ownership_rate AS housing_rental_rate,

        -- language
        SUM(tot_pop_5yrs)     AS tot_pop_5yrs,
        SUM(tot_english_only) AS tot_english_only,
        SUM(tot_non_english)  AS tot_non_english,
        SUM(tot_spanish)      AS tot_spanish,

        SUM(tot_english_only) / NULLIF(SUM(tot_pop_5yrs), 0)::DOUBLE AS prop_english_only,
        1 - prop_english_only AS prop_non_english,
        SUM(tot_spanish)      / NULLIF(SUM(tot_pop_5yrs), 0)::DOUBLE AS prop_span,
        SUM(tot_spanish)      / NULLIF(SUM(tot_non_english), 0)::DOUBLE AS prop_span_nonEnglish,

        -- employment
        SUM(tot_emp)             AS tot_emp,
        SUM(tot_unemp)           AS tot_unemp,
        SUM(tot_civilian_lf)     AS tot_civilian_lf,
        SUM(tot_working_age_pop) AS tot_working_age_pop,

        SUM(tot_unemp)       / NULLIF(SUM(tot_civilian_lf), 0)::DOUBLE     AS unemp_rate3,
        SUM(tot_emp)         / NULLIF(SUM(tot_civilian_lf), 0)::DOUBLE     AS emp_rate3,
        SUM(tot_civilian_lf) / NULLIF(SUM(tot_working_age_pop), 0)::DOUBLE AS lfp_rate,
        SUM(tot_emp)         / NULLIF(SUM(tot_working_age_pop), 0)::DOUBLE AS emp_to_pop
    FROM read_parquet('$DIR/../cc_data_updated.parquet')
) TO '$DIR/../usa_data_updated.parquet' (FORMAT parquet, CODEC zstd);
EOF
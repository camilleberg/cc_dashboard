---
title: check
sql:
  ccn20_geo: data/ccn20_geo.parquet
  cd119_geos: ./data/cd119_geos.parquet
  cc_data_updated: ./data/cc_data_updated.parquet
  ccn20_to_cd119: ./data/ccn20_to_cd119.parquet
  usa_data_updated: ./data/usa_data_updated.parquet
  cc_data_age_table: ./data/cc_tables/age/cc_data_age_table.parquet
  dc_data_age_table: ./data/cc_tables/age/dc_data_age_table.parquet
  state_data_age_table: ./data/cc_tables/age/state_data_age_table.parquet 
  cc_data_housing_table: ./data/cc_tables/housing/cc_data_housing_table.parquet 
  dc_data_housing_table: ./data/cc_tables/housing/dc_data_housing_table.parquet 
  state_data_housing_table: ./data/cc_tables/housing/state_data_housing_table.parquet 
head: '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tarekraafat/autocomplete.js@10/dist/css/autoComplete.min.css">'
---

This is to check sql 

```sql
SELECT * FROM state_data_age_table 

```
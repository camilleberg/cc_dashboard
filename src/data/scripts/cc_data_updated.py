import sys
from pathlib import Path

import pandas as pd
from dbfread import DBF

import json
import pandas as pd


# Resolve relative to this file so it works regardless of cwd
def load_dbf(path):
    return pd.DataFrame(iter(DBF(str(path.resolve()))))

def clean(df):
    df.rename(columns={'GEOID': 'ccn20', 'STAB': 'state'}, inplace=True)
    return df

def clean_age(df):
    df.rename(columns={'D001': 'tot_pop', 
                       'D019': 'ageGroup_under18', 
                       'D024': 'ageGroup_over65'}, inplace=True)
    df['ageGroup_18_65'] = df['tot_pop'] - df['ageGroup_under18'] - df['ageGroup_over65']
    
    return df

def clean_housing(df):
    df.rename(columns={'H001': 'tot_housing', 
                       'H002': 'occupied_housing_units', 
                       'H003': 'vacant_housing_units'}, inplace=True)
    return df

def clean_households(df):
    df.rename(columns={'S001': 'tot_hholds',
                       'H046': 'hholds_ownership_own', 
                       'H047': 'tot_rented'}, inplace=True)
    return df

def write_parquet(df, path):
    df.to_parquet(path, index=False)

def load_metadata(path):
    return pd.read_excel(path.resolve())

def write_metadata(metadata, path):
    metadata.to_json(path, orient="records")


if __name__ == "__main__":
    DBF_PATH = Path(__file__).parent / "../../../src/data/input/ACS5Y2024_501_Itemset1_CD119.dbf"
    df = load_dbf(DBF_PATH)
    df = clean(df)
    df = clean_age(df)
    df = clean_housing(df)
    df = clean_households(df)

    PARQUET_PATH = Path(__file__).parent / "../../../src/data/cc_data_updated.parquet"
    write_parquet(df, PARQUET_PATH)
    
    XLSX_PATH = Path(__file__).parent / "../../../src/data/input/Metadata 2024.xlsx"
    metadata = load_metadata(XLSX_PATH)
    
    METADATA_JSON_PATH = Path(__file__).parent / "../../../src/data/cc_data_updated_metadata.json"
    write_metadata(metadata, METADATA_JSON_PATH)
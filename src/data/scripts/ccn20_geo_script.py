#!/usr/bin/env python3
import sys
import os
import tempfile
import gdown
import pandas as pd
import shapely
import json
import zstandard as zstd
import numpy as np
import os
from pathlib import Path

FILE_ID = "1o-LGPQr-ML6xSp4hmTGGuGZO2pyWBLk5"

def log(msg):
    # stderr only — never contaminate stdout
    print(msg, file=sys.stderr)

def load_file():
    fd, tmp_path = tempfile.mkstemp(suffix=".parquet")
    os.close(fd)

    try:
        log(f"Downloading file_id={FILE_ID} to temp path")
        result = gdown.download(id=FILE_ID, output=tmp_path, quiet=True)

        if result is None:
            log("gdown.download returned None — download failed")
            sys.exit(1)

        with open(tmp_path, "rb") as f:
            header = f.read(4)

        if header != b"PAR1":
            log("Downloaded file does not look like valid Parquet (bad magic bytes)")
            sys.exit(1)

        log("Transforming geometry column")
        df = pd.read_parquet(tmp_path)
        df = df[["CCN20", "DC", "State", "geometry"]].copy()
        # rounding to 1 m (grid_size=0.00001)
        df["geometry"] = shapely.set_precision(shapely.from_wkb(df["geometry"]), grid_size=0.00001)
        # converting it to geojson
        df["geometry"] = shapely.to_geojson(df["geometry"])
        
        # returns df data 
        log("Finished processing file.")
        return df

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    

def split_file(df):
    # Split into a dictionary of DataFrames
   return {value: group for value, group in df.groupby('State')}

def save_state_parquets(state_dfs, DATA_DIR):
    for state, df in state_dfs.items():
        df.to_parquet(f"{DATA_DIR}/{state}.parquet", index=False)
    log(f"Saved parquet files to {DATA_DIR}")
        

if __name__ == "__main__":
    DATA_DIR = "./src/data/input/ccn20_geos"
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    df = load_file()
    state_dfs = split_file(df)
    save_state_parquets(state_dfs, DATA_DIR)
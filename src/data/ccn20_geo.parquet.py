#!/usr/bin/env python3
import sys
import os
import tempfile
import gdown
import pandas as pd
import shapely

FILE_ID = "1o-LGPQr-ML6xSp4hmTGGuGZO2pyWBLk5"

def log(msg):
    # stderr only — never contaminate stdout
    print(msg, file=sys.stderr)

def main():
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
        df["geometry"] = shapely.to_geojson(shapely.from_wkb(df["geometry"]))

        out_buf = df.to_parquet(index=False)
        sys.stdout.buffer.write(out_buf)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    main()
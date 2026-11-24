# Downloads Census Designated Place (CDP) files for each state, extracts them,
# keeps STATE and BASENAME, and writes one combined parquet file.
#
# Parallel download pattern from:
# https://medium.com/data-science/use-python-to-download-multiple-files-or-urls-in-parallel-1759da9d6535
#
# Requires: pip install requests pandas pyarrow

import shutil
import time
import zipfile
from multiprocessing.pool import ThreadPool
from pathlib import Path

import pandas as pd
import requests


# ---------- building URLs and paths ----------

url = 'https://tigerweb.geo.census.gov/tigerwebmain/Files/tab20/tigerweb_tab20_zcta5_2020_us.html'


def download_html(url):
    table = pd.read_html(url)[0]
    table.columns = [c.lower() for c in table.columns]
    table = table[['zcta5']]
    return table



def save_to_parquet(df, export_dir):
    df = df.copy()
    df["zcta5"] = df["zcta5"].astype(str).zfill(5)
    df.to_parquet(Path(export_dir) / "zcta5.parquet", index=False)

if __name__ == '__main__':
    # Dedicated temp folder: this gets deleted at the end, so never point it at a
    # folder that holds other data.
    EXPORT_DIR = "./src/data/input/"
    Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)

    # download
    print("Downloading HTML table for zcst...")
    df = download_html(url)
    print("Download complete. Saving to parquet...")
    save_to_parquet(df, EXPORT_DIR)
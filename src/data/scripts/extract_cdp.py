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
fips_to_abbr = {
    '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA',
    '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
    '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN',
    '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
    '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
    '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
    '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND',
    '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
    '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
    '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
    '56': 'WY', '60': 'AS', '66': 'GU', '69': 'MP', '72': 'PR',
    '78': 'VI'
}

FIPS = list(fips_to_abbr)
ABBRS = [abbr.lower() for abbr in fips_to_abbr.values()]   # ['al', 'ak', 'az', ...]


# ---------- building URLs and paths ----------

def make_urls(abr):
    # NOTE: this ends in .html. Open one in a browser to confirm it downloads a zip
    # and isn't a web page; if it's a page, find the real zip link.
    return ('https://tigerweb.geo.census.gov/tigerwebmain/Files/acs26/'
            f'tigerweb_acs26_cdp_2025_acs25_{abr}.html')


def download_html(url):
    table = pd.read_html(url)[0]
    table.columns = [c.lower() for c in table.columns]
    table = table[['basename', 'state']]
    return table

def download_all_htmls(ABBRS):
    tables = []
    for abr in ABBRS:
        url = make_urls(abr)
        table = download_html(url)
        tables.append(table)
        print(f"Downloaded {len(table)} rows for {abr.upper()}")
    return pd.concat(tables, ignore_index=True)

def save_to_parquet(df, export_dir):
    df = df.copy()
    df["state"] = df["state"].astype(str)
    df["state"] = df["state"].apply(lambda x: fips_to_abbr.get(x.zfill(2), x))
    df['state_no'] = df['state'].map({v: k for k, v in fips_to_abbr.items()})
    df["basename"] = df["basename"].astype(str)
    df['label'] = df['basename'] + ', ' + df['state']
    df.to_parquet(Path(export_dir) / "acs2025_cdp.parquet", index=False)

if __name__ == '__main__':
    # Dedicated temp folder: this gets deleted at the end, so never point it at a
    # folder that holds other data.
    EXPORT_DIR = "./src/data/input/cdp_lists"
    Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)

    # download
    print("Downloading HTML tables for all states...")
    combined_df = download_all_htmls(ABBRS)
    print("Download complete. Saving to parquet...")
    save_to_parquet(combined_df, EXPORT_DIR)
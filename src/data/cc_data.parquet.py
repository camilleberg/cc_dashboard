#!/usr/bin/env python3
"""
Data loader that takes the Excel file of data and transforms it into a parquet.

Later this may be modified to pull from the API.
"""

import pandas as pd
from pathlib import Path
import sys


def log(msg):
    # stderr only — never contaminate stdout
    print(msg, file=sys.stderr)


def excel_to_parquet(file_path, sheet_name, output_path):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df.rename(
        columns={'Dist Code': 'DC', 'State Postal Abbreviation': 'State'},
        inplace=True,
    )

    # CCN20 in the topojson properties is a zero-padded 7-char string (e.g. "0101001"),
    # but pandas/Excel reads it as an int64 (e.g. 101001) with the leading zero stripped.
    # If left as int64, filterBy joins against the geo file will silently match zero rows
    # since 101001 != "0101001". Cast here once so every consumer downstream (DuckDB,
    # vgplot, the dropdown menu) sees the same string format as the geo file.
    if 'CCN20' in df.columns:
        if df['CCN20'].isna().any():
            log("WARNING: CCN20 has null values — these will zero-pad to '0000nan'")
        df['CCN20'] = df['CCN20'].astype(str).str.zfill(7)
    else:
        log("WARNING: CCN20 column not found — skipping zero-pad fix; "
            "downstream joins against the geo file may silently return zero rows")

    # DC has the same issue (topojson gives "0101", 4-char zero-padded string)
    if 'DC' in df.columns:
        if df['DC'].isna().any():
            log("WARNING: DC has null values — these will zero-pad to '000nan'")
        df['DC'] = df['DC'].astype(str).str.zfill(4)
    else:
        log("WARNING: DC column not found — skipping zero-pad fix; "
            "downstream joins against the geo file may silently return zero rows")

    df.to_parquet(output_path, index=False)
    log(f"Data saved successfully to {output_path}")


if __name__ == '__main__':
    SCRIPT_DIR = Path(__file__).parent
    excel_to_parquet(
        SCRIPT_DIR / 'input' / 'cc20_us_02052025_website.xlsx',
        'CD119_CCN20_Itemset1',
        SCRIPT_DIR / 'cc_data.parquet',
    )
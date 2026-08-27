# this is a data loader that takes the excel file of data and transforms it into a parquet

# later maybe it can be modified to pull from the API

import pandas as pd
from pathlib import Path
import sys


def log(msg):
    # stderr only — never contaminate stdout
    print(msg, file=sys.stderr)

def excel_to_parquet(file_path, sheet_name, output_path):
    df = pd.read_excel(file_path, sheet_name)
    df.rename(columns={'Dist Code': 'DC', 'State Postal Abbreviation': 'State'}, inplace=True)

    # CCN20 in the topojson properties is a zero-padded 7-char string (e.g. "0101001"),
    # but pandas/Excel reads it as an int64 (e.g. 101001) with the leading zero stripped.
    # If left as int64, filterBy joins against the geo file will silently match zero rows
    # since 101001 != "0101001". Cast here once so every consumer downstream (DuckDB,
    # vgplot, the dropdown menu) sees the same string format as the geo file.
    if 'CCN20' in df.columns:
        df['CCN20'] = df['CCN20'].astype(str).str.zfill(7)

    # DC has the same issue (topojson gives "0101", 4-char zero-padded string)
    if 'DC' in df.columns:
        df['DC'] = df['DC'].astype(str).str.zfill(4)

    df.to_parquet(output_path, index = False)
    log("Data saved successfully")
    
    sys.stdout.buffer.write(df)
    log("Data exported")
    
    

if __name__ == '__main__':
    SCRIPT_DIR = Path(__file__).parent
    excel_to_parquet(SCRIPT_DIR / 'input' / 'cc20_us_02052025_website.xlsx', 'CD119_CCN20_Itemset1', 
                     SCRIPT_DIR / 'cc_data.parquet')

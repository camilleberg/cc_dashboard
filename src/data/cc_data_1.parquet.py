import pandas as pd
from pathlib import Path
import sys
import openpyxl
import pyarrow

def excel_to_parquet(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name)
    df.rename(columns={'Dist Code': 'DC', 'State Postal Abbreviation': 'State'}, inplace=True)

    if 'CCN20' in df.columns:
        df['CCN20'] = df['CCN20'].astype(str).str.zfill(7)

    if 'DC' in df.columns:
        df['DC'] = df['DC'].astype(str).str.zfill(4)

    print("Data successfully cleaned", file=sys.stderr)  # <-- stderr, not stdout
    return df

def write_parquet(df):
    df.to_parquet(sys.stdout.buffer, engine='pyarrow')
    sys.stdout.buffer.flush()

if __name__ == '__main__':
    SCRIPT_DIR = Path(__file__).parent
    try:
        df = excel_to_parquet(SCRIPT_DIR / 'input' / 'cc20_us_02052025_website.xlsx', 'CD119_CCN20_Itemset1')
        write_parquet(df)
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        raise


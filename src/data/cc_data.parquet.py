# this is a data loader that takes the excel fiel of data and transforms it into a parquet
# later maybe it cna be modified to pull from the API

import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def excel_to_parquet(file_path, output_path):
    df = pd.read_excel(file_path)
    df.rename(columns={'Dist Code': 'DC', 'State Postal Abbreviation': 'State'}, inplace=True)
    df.to_parquet(output_path)
    print("Data saved successfully to {}".format(output_path))

if __name__ == '__main__':
    excel_to_parquet(SCRIPT_DIR / 'input' / 'cc20_us_02052025_website.xlsx', SCRIPT_DIR / 'cc_data.parquet')

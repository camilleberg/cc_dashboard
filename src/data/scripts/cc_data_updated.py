import sys
from pathlib import Path

import pandas as pd
from dbfread import DBF

import json
import pandas as pd

# Resolve relative to this file so it works regardless of cwd
DBF_PATH = Path(__file__).parent / "../../../src/data/input/ACS5Y2024_501_Itemset1_CD119.dbf"

df = pd.DataFrame(iter(DBF(str(DBF_PATH.resolve()))))

PARQUET_PATH = Path(__file__).parent / "../../../src/data/cc_data_updated.parquet"

df.to_parquet(PARQUET_PATH, index=False)

## writing metadata to json 

XLSX_PATH = Path(__file__).parent / "../../../src/data/Metadata 2024.xlsx"
metadata = pd.read_excel(XLSX_PATH.resolve())  # uses openpyxl under the hood
metadata_json_path = Path(__file__).parent / "../../../src/data/cc_data_updated_metadata.json"
metadata.to_json(metadata_json_path, orient="records")
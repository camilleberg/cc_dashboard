# this is to take the ccn20 data and map to cd119 

import pandas as pd
import json 

from pathlib import Path

CC_DATA_PATH = Path(__file__).parent / "../../../src/data/cc_data.parquet"
cc_data = pd.read_parquet(CC_DATA_PATH)

rel_columns = cc_data[['CCN20', 'DC']]
rel_columns.rename(columns = {'CCN20': 'ccn20', 'DC': 'cd119'}, inplace=True)

ccn20_to_cd119 = {row.ccn20: row.cd119 for row in rel_columns.itertuples()}

JSON_PATH = Path(__file__).parent / "../../../src/data/input/ccn20_to_cd119.json"

with open(JSON_PATH, "w") as file:
    json.dump(ccn20_to_cd119, file, indent=4)

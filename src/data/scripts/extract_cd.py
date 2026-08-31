# this fucniton gets the cd geos and downloads them 

# source for code
# https://medium.com/data-science/use-python-to-download-multiple-files-or-urls-in-parallel-1759da9d6535


import requests 
import time 
from multiprocessing import cpu_count 
from multiprocessing.pool import ThreadPool
from pathlib import Path
import os
import zipfile
import geopandas as gpd
import re
import fiona
import fiona.errors
import shutil

# function to make urls

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

def make_urls(idx):
    idx_str = str(idx).zfill(2)
    return 'https://www2.census.gov/geo/tiger/TIGER2024/CD/tl_2024_' + idx_str + '_cd119.zip'


# function to make destination folder names

def make_fns(idx, DATA_DIR):
    idx_str = str(idx).zfill(2)
    return DATA_DIR + f'/tl_2024_{idx_str}_cd119.zip'

def make_input(DATA_DIR):
    urls = [make_urls(idx) for idx in range(1, 78)]
    fns = [make_fns(idx, DATA_DIR) for idx in range(1, 78)]
    
    inputs = zip(urls, fns)
    
    return inputs, fns

def download_url(args): 
  t0 = time.time() 
  url, fn = args[0], args[1] 
  try: 
    r = requests.get(url) 
    with open(fn, 'wb') as f: 
      f.write(r.content) 
      return(url, time.time() - t0) 
  except Exception as e: 
    print('Exception in download_url():', e)

def download_parallel(args):
    cpus = cpu_count()
    with ThreadPool(cpus - 1) as pool:
        for result in pool.imap_unordered(download_url, args):
            if result:
                print('url:', result[0], 'time (s):', result[1])
    print("Files downloaded succesfully")


def make_extracted(idx, DATA_DIR):
    idx_str = str(idx).zfill(2)
    EXTRACT_DIR = DATA_DIR + f'/extracted/tl_2024_{idx_str}_cd119'
    Path(EXTRACT_DIR).mkdir(parents=True, exist_ok=True)
    return EXTRACT_DIR

def make_shpfile_name(extracted_fn):
    shpfile_name = extracted_fn + r'/' + extracted_fn[extracted_fn.rindex("/")+1:] + '.shp'
    return shpfile_name

def make_inputs_extracted(DATA_DIR):
    extracted_fns =  [make_extracted(idx, DATA_DIR) for idx in range(1, 78)]
    shpfile_names = [make_shpfile_name(extracted_fn) for extracted_fn in extracted_fns]
    return extracted_fns, shpfile_names

def extract_files(extracted_path, fn):
        with zipfile.ZipFile(fn, 'r') as zip_ref:
                zip_ref.extractall(extracted_path)

def extract_inputs(extracted_fns, fns):
    failed = []
    for i, extracted_path in enumerate(extracted_fns):
        fn = fns[i]
        try:
            extract_files(extracted_path, fn)
        except FileNotFoundError:
            print('Missing zip, skipping:', fn)
            failed.append(fn)
        except zipfile.BadZipFile:
            print('Corrupt/invalid zip, skipping:', fn)
            failed.append(fn)
    return failed
    
def convert_to_geo_and_clean(shpfile_name, EXPORT_DIR):
    shp_file = gpd.read_file(shpfile_name)
    shp_file  = shp_file.to_crs(epsg=4326)
    
    shp_file['State'] = shp_file['STATEFP'].map(fips_to_abbr)
    shp_file.rename(columns={'GEOID': 'DC'}, inplace=True)
    shp_file_clean = shp_file[['DC', 'State', 'geometry']]
    
    idx = re.findall(r"_(.*?)_", shpfile_name)[3]
    shpfile_save_path = EXPORT_DIR + r'/cd119_' + idx + r'.parquet'
    
    shp_file_clean.to_parquet(shpfile_save_path)
    print(f"File has been sucessfully exported to parquet at {shpfile_save_path}")



def convert_all_geos(shpfile_names, EXPORT_DIR):
    failed = []
    for shpfile_name in shpfile_names:
        try:
            convert_to_geo_and_clean(shpfile_name, EXPORT_DIR)
        except (fiona.errors.DriverError, FileNotFoundError):
            print('Missing/unreadable shpfile, skipping:', shpfile_name)
            failed.append(shpfile_name)
        except zipfile.BadZipFile:
            print('Corrupt/invalid shpfile, skipping:', shpfile_name)
            failed.append(shpfile_name)
    return failed

def delete_extra_files(extracted_path):
    shutil.rmtree(extracted_path)
    print("Extra files deleted successfully from {}".format(extracted_path))

if __name__ == '__main__':
    DATA_DIR = "./src/data/cd_119_geos"
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # downlaoding data
    inputs, fns = make_input(DATA_DIR)
    inputs = list(inputs)
    download_parallel(inputs)
    
    # extracting them 
    extracted_fns, shpfile_names = make_inputs_extracted(DATA_DIR)
    extract_inputs(extracted_fns, fns)
    
    # extracting and cleaning
    EXPORT_DIR =  f"./src/data/cd119_geographies"
    Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)
    
    # cleaning and saving
    convert_all_geos(shpfile_names, EXPORT_DIR)
    
    # deleting
    delete_extra_files(DATA_DIR)
    
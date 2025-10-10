
'''
---------------------------------------------------------------
Imports
---------------------------------------------------------------
'''

import os
import logging
import zipfile
from io import BytesIO
from typing import Optional, List

import pandas as pd
import requests
import glob
import shutil


'''
---------------------------------------------------------------
Basic Setup
---------------------------------------------------------------
'''
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "Rawdata")
os.makedirs(RAW_DIR, exist_ok=True)

ERCOT_RTM_2024_URL = (
    "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065471230"
)



'''
---------------------------------------------------------------
Function 1 — Fetch ERCOT Real-Time Market Prices (Price_t)
---------------------------------------------------------------
'''

'''
ERCOT MIS download link for 2024 Real-Time Market
Load Zone & Hub Settlement Point Prices (RTMLZHBSPP_2024.zip)
'''
ERCOT_RTM_2024_URL = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1065471230"


'''
main function
'''
def fetch_ercot_lmp_2024(url: str = ERCOT_RTM_2024_URL, output_dir: str = RAW_DIR) -> None:

    ''' Download the ERCOT 2024 Real-Time Market ZIP file and extract its contents.'''

    logging.info(f"Downloading ERCOT ZIP from {url}")

    response = requests.get(url, timeout=180)
    response.raise_for_status()

    zip_bytes = BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes) as zf:
        zf.extractall(output_dir)
        file_list = zf.namelist()
        logging.info(f"Extracted {len(file_list)} file(s) to {output_dir}")
        for f in file_list:
            logging.info(f"  - {f}")

        '''rename the extracted Excel file to "price.xlsx"'''

        excel_files = [f for f in file_list if f.lower().endswith(".xlsx")]
        if not excel_files:
            logging.warning("No Excel file found to rename.")

        old_path = os.path.join(output_dir, excel_files[0])
        new_path = os.path.join(output_dir, "price.xlsx")

        try:
            os.replace(old_path, new_path)
            logging.info(f"Renamed {excel_files[0]} → price.xlsx")
        except Exception as e:
            logging.error(f"Failed to rename {excel_files[0]}: {e}")


def extract_load_zip_2024(load_zip_path: str = os.path.join(RAW_DIR, "load", "load.zip")) -> None:
    '''
    Extracts the main load.zip (which contains 366 sub-zip files),
    extracts each sub-zip into a dedicated folder "load_raw_data",
    and deletes only the 366 sub-zip files.
    The main load.zip is preserved for reproducibility.
    '''
    # Define paths
    load_dir = os.path.dirname(load_zip_path)
    raw_data_dir = os.path.join(load_dir, "load_raw_data")
    os.makedirs(raw_data_dir, exist_ok=True)

    # Step 1 — Extract the main load.zip (contains 366 smaller zips)
    logging.info(f"Extracting main ZIP: {load_zip_path}")
    with zipfile.ZipFile(load_zip_path, "r") as zf:
        zf.extractall(load_dir)
        logging.info(f"Extracted {len(zf.namelist())} sub-zips into {load_dir}")

    # Step 2 — Find all sub-zip files
    sub_zips = glob.glob(os.path.join(load_dir, "*.zip"))
    total = len(sub_zips)
    logging.info(f"Found {total} sub-zip files. Extracting them into {raw_data_dir}...")

    # Step 3 — Extract each sub-zip into load_raw_data/
    for idx, sub_zip in enumerate(sub_zips, start=1):
        try:
            with zipfile.ZipFile(sub_zip, "r") as sub_zf:
                sub_zf.extractall(raw_data_dir)
            os.remove(sub_zip)
            logging.info(f"[{idx}/{total}] Extracted and removed: {os.path.basename(sub_zip)}")
        except zipfile.BadZipFile:
            logging.warning(f"⚠️ Skipped invalid ZIP: {sub_zip}")

    # Step 4 — Final message
    logging.info("✅ All sub-zips extracted to 'load_raw_data' and removed successfully.")

'''
---------------------------------------------------------------
Main Execution
---------------------------------------------------------------
'''
if __name__ == "__main__":
    fetch_ercot_lmp_2024()
    extract_load_zip_2024()

'''
---------------------------------------------------------------
Imports
---------------------------------------------------------------
'''

import os
import logging
import zipfile
from io import BytesIO
import time
import pandas as pd
import requests
import glob
from datetime import date
import shutil
from dotenv import load_dotenv

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
PRICE_DIR = os.path.join(RAW_DIR, "price")
CDD_HDD_DIR = os.path.join(RAW_DIR, "CDD_HDD")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PRICE_DIR, exist_ok=True)
os.makedirs(CDD_HDD_DIR, exist_ok=True)

load_dotenv()
token = os.getenv("NOAA_TOKEN")
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

def fetch_ercot_lmp_2024(url: str = ERCOT_RTM_2024_URL, output_dir: str = PRICE_DIR) -> None:

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

    '''rename the extracted Excel file to "Price.xlsx"'''
    excel_files = [f for f in file_list if f.lower().endswith(".xlsx")]
    if not excel_files:
        logging.warning("No Excel file found in the downloaded ZIP.")
        return

    old_path = os.path.join(output_dir, excel_files[0])
    new_path = os.path.join(output_dir, "Price.xlsx")

    try:
        os.replace(old_path, new_path)
        logging.info(f"Renamed {excel_files[0]} → Price.xlsx in {output_dir}")
    except Exception as e:
        logging.error(f"Failed to rename {excel_files[0]}: {e}")

'''
---------------------------------------------------------------
Function 2 — Extract ERCOT System Load daily archives (Load_t)
---------------------------------------------------------------
'''

def extract_load_zip_2024(load_zip_path: str = os.path.join(RAW_DIR, "load", "load.zip")) -> None:
    '''
    Extracts the main load.zip (which contains 366 sub-zip files),
    extracts each sub-zip into a dedicated folder "load_raw_data",
    and deletes only the 366 sub-zip files.
    The main load.zip is preserved for reproducibility.
    '''

    '''Define paths'''
    load_dir = os.path.dirname(load_zip_path)
    raw_data_dir = os.path.join(load_dir, "load_raw_data")
    os.makedirs(raw_data_dir, exist_ok=True)

    '''Extract the main load.zip (contains 366 smaller zips)'''
    logging.info(f"Extracting main ZIP: {load_zip_path}")
    with zipfile.ZipFile(load_zip_path, "r") as zf:
        zf.extractall(load_dir)
        logging.info(f"Extracted {len(zf.namelist())} sub-zips into {load_dir}")

    '''Find all sub-zip files except the original load.zip'''
    sub_zips = [
        f for f in glob.glob(os.path.join(load_dir, "*.zip"))
        if os.path.abspath(f) != os.path.abspath(load_zip_path)
    ]
    total = len(sub_zips)
    logging.info(f"Found {total} sub-zip files. Extracting them into {raw_data_dir}...")

    '''Extract each sub-zip into load_raw_data/'''
    for idx, sub_zip in enumerate(sub_zips, start=1):
        try:
            with zipfile.ZipFile(sub_zip, "r") as sub_zf:
                sub_zf.extractall(raw_data_dir)
            os.remove(sub_zip)
            logging.info(f"[{idx}/{total}] Extracted and removed: {os.path.basename(sub_zip)}")
        except zipfile.BadZipFile:
            logging.warning(f"⚠️ Skipped invalid ZIP: {sub_zip}")

    logging.info("✅ All sub-zips extracted to 'load_raw_data' and removed successfully.")
    logging.info(f"✅ Main ZIP preserved at {load_zip_path}")

'''
---------------------------------------------------------------
Function 3 — Fetch NOAA raw (TMIN/TMAX/TAVG) for CDD/HDD
---------------------------------------------------------------
'''

def fetch_noaa_weather_2024(
    out_dir: str = CDD_HDD_DIR,
    year: int = 2024,
    datatypes = ("TMIN", "TMAX", "TAVG"),
    zones: dict | None = None,
    token_env_var: str = "NOAA_TOKEN",
    page_limit: int = 1000,
    request_timeout: int = 60,
    sleep_between_pages: float = 0.15,
    max_retries: int = 5,
    backoff_base: float = 0.8,
    save_per_station: bool = False,
) -> None:
    '''
    Fetch RAW NOAA GHCND daily observations for 2024 by ERCOT-like zones,
    using one representative station per zone, and saves a tidy long table:

        CDD_HDD/noaa_raw.csv
        columns: [date, zone, station_id, datatype, value]

    Notes:
        • Requires an environment variable "NOAA_TOKEN" loaded from .env.
        • Month-split + pagination + retry to avoid overloading.
    '''

    '''Step 0 — Default zone→station mapping'''
    if zones is None:
        zones = {
            "HOUSTON": "GHCND:USW00012960",   # IAH
            "NORTH":   "GHCND:USW00003927",   # DFW
            "SOUTH":   "GHCND:USW00012921",   # SAT
            "WEST":    "GHCND:USW00023023",   # MAF
        }

    '''Step 1 — Setup and token validation'''
    os.makedirs(out_dir, exist_ok=True)
    if save_per_station:
        os.makedirs(os.path.join(out_dir, "stations"), exist_ok=True)

    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    token = os.getenv(token_env_var)
    if not token:
        raise ValueError(f"Missing NOAA token. Please define {token_env_var} in your .env file.")
    headers = {"token": token}

    '''Step 2 — Helpers'''
    def _month_start_end(y: int, m: int) -> tuple[date, date]:
        '''Return inclusive start and end dates for month m of year y.'''
        if m == 12:
            return date(y, 12, 1), date(y, 12, 31)
        from datetime import timedelta
        first = date(y, m, 1)
        next_first = date(y, m + 1, 1)
        last = next_first - timedelta(days=1)
        return first, last

    def _robust_get(params: dict) -> requests.Response:
        attempt = 0
        while True:
            attempt += 1
            resp = requests.get(base_url, headers=headers, params=params, timeout=request_timeout)
            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt <= max_retries:
                    wait = (backoff_base ** attempt) + 0.5 * attempt
                    logging.warning(
                        f"NOAA {resp.status_code} for {params.get('stationid')} {params.get('datatypeid')} "
                        f"@offset={params.get('offset')} retry {attempt}/{max_retries} after {wait:.2f}s"
                    )
                    time.sleep(wait)
                    continue
            resp.raise_for_status()
            return resp

    def _fetch_month_station_datatype(station_id: str, dtid: str, start_iso: str, end_iso: str) -> list[dict]:
        '''
        Fetch one month for a given station + datatype with pagination.
        Returns a list of raw rows (dicts) for that month.
        '''
        rows_all = []
        offset = 1
        total = None
        while True:
            params = {
                "datasetid": "GHCND",
                "stationid": station_id,
                "datatypeid": dtid,
                "startdate": start_iso,
                "enddate": end_iso,
                "units": "standard",
                "limit": page_limit,
                "offset": offset,
            }
            resp = _robust_get(params)
            js = resp.json()

            if total is None:
                try:
                    total = js["metadata"]["resultset"]["count"]
                    logging.info(f"{dtid} {station_id} {start_iso}→{end_iso}: ~{total} rows")
                except Exception:
                    total = None

            part = js.get("results", [])
            if not part:
                break

            rows_all.extend(part)
            offset += page_limit

            if total:
                done = min(len(rows_all), total)
                pct = 100.0 * done / total
                logging.info(f"{dtid} {station_id} {start_iso[:7]}: {done}/{total} ({pct:.1f}%)")

            time.sleep(sleep_between_pages)

            if total and len(rows_all) >= total:
                break

        return rows_all

    '''Step 3 — Iterate zones × stations × datatypes × months'''
    long_records = []
    if save_per_station:
        station_buffers: dict[str, list[dict]] = {sid: [] for sid in zones.values()}

    for zone, station_id in zones.items():
        for dtid in datatypes:
            for m in range(1, 13):
                m_start, m_end = _month_start_end(year, m)
                start_iso, end_iso = m_start.isoformat(), m_end.isoformat()
                logging.info(f"Fetching {zone} {station_id} {dtid} for {start_iso} → {end_iso}")
                rows = _fetch_month_station_datatype(station_id, dtid, start_iso, end_iso)

                for r in rows:
                    long_records.append({
                        "date": pd.to_datetime(r.get("date")).date() if r.get("date") else None,
                        "zone": zone,
                        "station_id": station_id,
                        "datatype": r.get("datatype"),
                        "value": r.get("value"),
                    })
                    if save_per_station:
                        station_buffers[station_id].append({
                            "date": pd.to_datetime(r.get("date")).date() if r.get("date") else None,
                            "datatype": r.get("datatype"),
                            "value": r.get("value"),
                        })

    '''Step 4 — Save the table'''
    df_long = pd.DataFrame(long_records)
    out_long = os.path.join(out_dir, f"noaa_raw.csv")
    df_long.to_csv(out_long, index=False)
    logging.info(f"Saved RAW NOAA file → {out_long} (rows={len(df_long)})")


'''
---------------------------------------------------------------
Function 4 — Fetch ERCOT RenewableShare (Fuel Mix archive)
---------------------------------------------------------------
'''

def fetch_ercot_renewableshare_2024_from_archive(
    url: str = "https://www.ercot.com/files/docs/2021/03/10/FuelMixReport_PreviousYears.zip",
    output_dir: str = os.path.join(RAW_DIR, "RenewableShare"),
    keep_filename: str = "IntGenbyFuel2024.xlsx",
) -> None:
    '''
    Download ERCOT Fuel Mix "Previous Years" ZIP, extract to Rawdata/RenewableShare,
    keep ONLY the 2024 annual workbook (IntGenbyFuel2024.xlsx), and delete everything else
    (including the source ZIP and other years' files/folders).

    Steps:
        1) Download ZIP to memory and also persist a temp copy for reproducibility logs.
        2) Extract all contents into output_dir (may include nested folders).
        3) Locate IntGenbyFuel2024.xlsx anywhere under output_dir, move it to output_dir root.
        4) Remove the temp ZIP file and all other files/folders except IntGenbyFuel2024.xlsx.
    '''

    '''Step 1 — Prepare directory and download ZIP'''
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Downloading ERCOT Fuel Mix archive from {url}")

    response = requests.get(url, timeout=240)
    response.raise_for_status()

    zip_bytes = BytesIO(response.content)
    temp_zip_path = os.path.join(output_dir, "FuelMixReport_PreviousYears.zip")
    with open(temp_zip_path, "wb") as f:
        f.write(response.content)
    logging.info(f"Saved temporary ZIP → {temp_zip_path}")

    '''Step 2 — Extract all files'''
    with zipfile.ZipFile(zip_bytes) as zf:
        zf.extractall(output_dir)
        names = zf.namelist()
        logging.info(f"Extracted {len(names)} item(s) into {output_dir}")
        for n in names[:10]:
            logging.info(f"  - {n}")
        if len(names) > 10:
            logging.info(f"  ... and {len(names) - 10} more")

    '''Step 3 — Find the target Excel (case-insensitive), move to output_dir root'''
    target_found_path = None
    keep_lower = keep_filename.lower()

    for root, dirs, files in os.walk(output_dir):
        for fn in files:
            if fn.lower() == keep_lower:
                candidate = os.path.join(root, fn)
                target_found_path = candidate
                break
        if target_found_path:
            break

    if not target_found_path:
        raise FileNotFoundError(
            f"Could not locate {keep_filename} after extraction under {output_dir}"
        )

    final_keep_path = os.path.join(output_dir, keep_filename)
    if os.path.abspath(target_found_path) != os.path.abspath(final_keep_path):
        if os.path.exists(final_keep_path):
            os.remove(final_keep_path)
        shutil.move(target_found_path, final_keep_path)
    logging.info(f"Kept workbook → {final_keep_path}")

    '''Step 4 — Delete everything else (including the temp ZIP)'''
    removed_count = 0
    for entry in os.listdir(output_dir):
        path = os.path.join(output_dir, entry)
        if entry == keep_filename:
            continue
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
                removed_count += 1
            elif os.path.isdir(path):
                shutil.rmtree(path)
                removed_count += 1
        except Exception as e:
            logging.warning(f"Failed to remove {path}: {e}")

    logging.info(f"Removed {removed_count} other item(s); only {keep_filename} remains.")
    logging.info("✅ ERCOT Fuel Mix previous-years archive processed successfully.")



'''
---------------------------------------------------------------
Main Execution
---------------------------------------------------------------
'''
if __name__ == "__main__":
    fetch_ercot_lmp_2024()
    extract_load_zip_2024()
    fetch_noaa_weather_2024()
    fetch_ercot_renewableshare_2024_from_archive()
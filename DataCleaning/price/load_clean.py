import os, glob
import pandas as pd
from typing import List

RAW_DIR = "DataScraping/Rawdata/load/load_raw_data"
OUT_PATH = "DataCleaning/price/Load_Clean.csv"

def _norm_cols(df: pd.DataFrame) -> dict:
    return {c.lower().strip(): c for c in df.columns}

def _pick_first(d: dict, keys: List[str]):
    for k in keys:
        if k in d:
            return d[k]
    return None

def _numeric_zone_cols(df: pd.DataFrame, ignore: List[str]) -> List[str]:
    cand = []
    for c in df.columns:
        if c in ignore: 
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            cand.append(c)
    return cand

def load_and_clean() -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSVs under {RAW_DIR}")

    dfs = []
    for f in files:
        df = pd.read_csv(f)
        norm = _norm_cols(df)

        date_col = _pick_first(norm, ["operday","date","delivery date","operating day"])   # date/hour columns
        hour_col = _pick_first(norm, ["hourending","delivery hour","hour"])

        if not date_col:
            raise KeyError(f"No date column found in {f}. Have: {list(df.columns)}")

        load_col = _pick_first(norm, ["total","system load","load (mw)","load","actual load (mw)"])

        tmp = df.copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col])

        if load_col:
            tmp.rename(columns={date_col: "date", load_col: "Load"}, inplace=True)
            keep = ["date"]
            if hour_col:
                tmp.rename(columns={hour_col: "hour"}, inplace=True)
                keep.append("hour")
            keep.append("Load")
            tmp = tmp[keep]
        else:
            ignore = {date_col}  # sum all numeric zone columns except none
            if hour_col: 
                ignore.add(hour_col)
            ignore |= set([_pick_first(norm, ["dstflag"]), _pick_first(norm, ["timezone"])]) - {None}
            zone_cols = _numeric_zone_cols(df, ignore=list(ignore))
            if not zone_cols:
                raise KeyError(f"No load or zone numeric columns found in {f}. Have: {list(df.columns)}")
            tmp = tmp[[date_col] + ([hour_col] if hour_col else []) + zone_cols].copy()
            tmp.rename(columns={date_col: "date"}, inplace=True)
            if hour_col:
                tmp.rename(columns={hour_col: "hour"}, inplace=True)
            tmp["Load"] = tmp[zone_cols].sum(axis=1)

        dfs.append(tmp[["date","Load"]])

    big = pd.concat(dfs, ignore_index=True)

    daily = (big.groupby("date", as_index=False)["Load"] # daily average in MW
                 .mean()
                 .rename(columns={"Load": "Load_t"})
                 .sort_values("date"))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    daily.to_csv(OUT_PATH, index=False)
    print(f"Successfuly Saved: {OUT_PATH} (rows={len(daily)})")
    return daily

if __name__ == "__main__":
    load_and_clean()

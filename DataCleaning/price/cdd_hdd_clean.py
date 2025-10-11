import os, glob
import pandas as pd
import numpy as np

RAW_DIR = "DataScraping/Rawdata/CDD_HDD"
OUT_PATH = "DataCleaning/price/CDD_HDD_Clean.csv"

def read_all():
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSVs found under {RAW_DIR}")
    parts = []
    for f in files:
        df = pd.read_csv(f)
        cols = {c.lower().strip(): c for c in df.columns}   #lower
        need = ["date","datatype","value"]
        if not all(k in cols for k in need):
            raise KeyError(f"{f} missing one of {need}. Have: {list(df.columns)}")

        dcol = cols["date"]; tcol = cols["datatype"]; vcol = cols["value"]
        tmp = df[[dcol, tcol, vcol]].copy()
        tmp.columns = ["date","datatype","value"]
        tmp["date"] = pd.to_datetime(tmp["date"])
        parts.append(tmp)
    return pd.concat(parts, ignore_index=True)

def maybe_fix_units(wide):
    for c in ["TMAX","TMIN","TAVG"]:  #unit
        if c in wide.columns:
            s = wide[c].dropna()
            if len(s) and s.abs().median() > 200:
                wide[c] = wide[c] / 10.0
    return wide

def main():
    longdf = read_all()

    wide = (longdf   # index=date, columns=datatype, values=mean(value)
            .pivot_table(index="date", columns="datatype", values="value", aggfunc="mean")
            .reset_index())

    wide = maybe_fix_units(wide)  # fix probable mistake

    if not {"CDD","HDD"}.issubset(set(wide.columns)):
        if "TAVG" not in wide.columns:
            if {"TMAX","TMIN"}.issubset(set(wide.columns)):
                wide["TAVG"] = (wide["TMAX"] + wide["TMIN"]) / 2.0
            else:
                raise KeyError("No CDD/HDD and also missing TMAX/TMIN to compute TAVG.")
        wide["CDD"] = (wide["TAVG"] - 65).clip(lower=0)
        wide["HDD"] = (65 - wide["TAVG"]).clip(lower=0)

    out = (wide[["date","CDD","HDD"]]
           .rename(columns={"CDD":"CDD_t","HDD":"HDD_t"})
           .sort_values("date"))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"Successfuly saved {OUT_PATH} (rows={len(out)})")

if __name__ == "__main__":
    main()

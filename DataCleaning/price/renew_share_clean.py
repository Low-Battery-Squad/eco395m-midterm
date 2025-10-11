import os
import re
import pandas as pd
import numpy as np

XLSX = "DataScraping/Rawdata/RenewableShare/IntGenbyFuel2024.xlsx"
OUT  = "DataCleaning/price/RenewableShare_Clean.csv"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def find_header_row(df: pd.DataFrame):
    """
    Return index of the header row that contains DATE/Fuel/Total (case-insensitive).
    """
    wanted = {"date","fuel","total"}
    for i, row in df.iterrows():
        labels = set(str(x).strip().lower() for x in row.tolist())
        if {"date","fuel"}.issubset(labels) and "total" in labels:
            return i
    for i, row in df.iterrows():  # Find Date
        labels = set(str(x).strip().lower() for x in row.tolist())
        if "date" in labels:
            return i
    return None

def parse_month(xl: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    df = xl.parse(sheet, header=None)
    df = df.dropna(how="all").dropna(axis=1, how="all")  # remove empty cols/rows
    if df.empty:
        return pd.DataFrame(columns=["date","fuel","total"])

    hdr = find_header_row(df)
    if hdr is None:
        return pd.DataFrame(columns=["date","fuel","total"])

    head = df.iloc[hdr].astype(str).str.strip()
    body = df.iloc[hdr+1:].copy()
    body.columns = head

    cols = {c.lower().strip(): c for c in body.columns}  # Unify neme of cols
    date_col  = cols.get("date")
    fuel_col  = cols.get("fuel")
    total_col = cols.get("total")
    if not (date_col and fuel_col and total_col):
        return pd.DataFrame(columns=["date","fuel","total"])

    out = body[[date_col, fuel_col, total_col]].copy()
    out.rename(columns={date_col:"date", fuel_col:"fuel", total_col:"total"}, inplace=True)  # Stadardize

    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date  # Date
    out = out.dropna(subset=["date"])

    out["total"] = pd.to_numeric(out["total"], errors="coerce")
    out = out.dropna(subset=["total"])

    out["fuel"] = out["fuel"].astype(str).str.strip().str.lower()

    return out[["date","fuel","total"]]

def main():
    if not os.path.exists(XLSX):
        raise FileNotFoundError(f"Not found: {XLSX}")

    xl = pd.ExcelFile(XLSX)
    parts = []
    for s in xl.sheet_names:
        if s in MONTHS:
            part = parse_month(xl, s)
            if not part.empty:
                parts.append(part)

    if not parts:
        raise RuntimeError("No usable monthly sheets parsed (Jan..Dec).")

    df = pd.concat(parts, ignore_index=True)

    daily_total = df.groupby("date", as_index=False)["total"].sum().rename(columns={"total":"total_gen"})  #putem together
    wind_total  = (df[df["fuel"].str.contains("wind")]
                   .groupby("date", as_index=False)["total"].sum()
                   .rename(columns={"total":"wind"}))
    solar_total = (df[df["fuel"].str.contains("solar")]
                   .groupby("date", as_index=False)["total"].sum()
                   .rename(columns={"total":"solar"}))

    merged = daily_total.merge(wind_total, on="date", how="left").merge(solar_total, on="date", how="left")
    merged[["wind","solar"]] = merged[["wind","solar"]].fillna(0.0)
    merged["RenewableShare_t"] = np.where(merged["total_gen"]>0,
                                          (merged["wind"] + merged["solar"]) / merged["total_gen"],
                                          np.nan)
    result = merged[["date","RenewableShare_t"]].sort_values("date")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result.to_csv(OUT, index=False)
    print(f"Success")

if __name__ == "__main__":
    main()

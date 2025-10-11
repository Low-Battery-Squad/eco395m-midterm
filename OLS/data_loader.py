# data_loader.py  — portable + drop negative price rows
from pathlib import Path
import sys
import re
import pandas as pd

BASE_DIR    = Path(__file__).resolve().parent
# default to ../DataCleaning/ALL_IN_ONE.csv; override via CLI arg
DEFAULT_RAW = BASE_DIR.parent / "DataCleaning" / "ALL_IN_ONE.csv"
OUT_PATH    = BASE_DIR / "preprocessed_data.csv"

def find_price_col(cols):
    """
    Find a column that looks like 'price' (e.g., Price, price_t, PRICE2022).
    Case-insensitive, allows optional suffixes.
    """
    low_map = {c.lower(): c for c in cols}
    pat = re.compile(r"^price(_?\w+)?$", re.I)
    for lc, orig in low_map.items():
        if pat.match(lc):
            return orig
    return None

def load_and_preprocess_data(raw_path: Path = DEFAULT_RAW, out_path: Path = OUT_PATH) -> Path:
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {raw_path}.\n"
            "Place your CSV there or run:  python data_loader.py /full/path/to/your.csv"
        )

    print(f"[info] BASE_DIR  = {BASE_DIR}")
    print(f"[info] RAW_PATH  = {raw_path}")
    print(f"[info] OUT_PATH  = {out_path}")
    print(f"[info] Reading raw CSV: {raw_path}")

    df = pd.read_csv(raw_path)

    # 1) Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # 2) Auto-detect price column
    price_col = find_price_col(df.columns)
    if price_col is None:
        raise KeyError(
            "Could not find a price column. Expected something like 'Price' or 'Price_t'.\n"
            f"Available columns: {list(df.columns)}"
        )

    # 3) Coerce numeric-looking columns (safe)
    for col in df.columns:
        if df[col].dtype == "object":
            coerced = pd.to_numeric(df[col], errors="coerce")
            # keep if coercion produced at least some numbers
            if coerced.notna().sum() > 0:
                df[col] = coerced

    # 4) Drop rows with negative price
    before = len(df)
    df = df[df[price_col] >= 0]
    after_nonneg = len(df)

    # 5) Drop rows that are entirely NaN (optional safety)
    df = df.dropna(how="all")
    after = len(df)

    # 6) Save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[done] Wrote preprocessed data → {out_path} "
          f"(rows={after}, cols={df.shape[1]}; "
          f"dropped {before - after_nonneg} with negative {price_col}, "
          f"{after_nonneg - after} all-NaN rows)")

    return out_path

def main():
    # Allow: python data_loader.py /path/to/raw.csv
    raw = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_RAW
    load_and_preprocess_data(raw, OUT_PATH)

if __name__ == "__main__":
    main()


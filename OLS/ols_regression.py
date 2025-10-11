# ols_regression.py — portable + auto-detect column names + model pickle
from pathlib import Path
import re
import pickle
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ---------- repo-relative paths ----------
BASE_DIR   = Path(__file__).resolve().parent
DATA_PATH  = BASE_DIR / "preprocessed_data.csv"
MODEL_PATH = BASE_DIR / "ols_model.pkl"
COEF_CSV   = BASE_DIR / "ols_coefficients.csv"
RESID_PNG  = BASE_DIR / "ols_residuals_analysis.png"

# keywords to find columns (case-insensitive, allows optional suffixes like _t)
KEYS = {
    "target": ["price", "p"],
    "load": ["load"],
    "cdd": ["cdd", "coolingdegree", "cooling_deg"],
    "hdd": ["hdd", "heatingdegree", "heating_deg"],
    "renew": ["renewableshare", "renew_share", "renew", "rs", "solar_wind_share"],
}

def _find_col(cols, keywords):
    """Return first column whose name matches any keyword (case-insensitive, optional suffixes like _t)."""
    low = {c.lower(): c for c in cols}
    for kw in keywords:
        pat = re.compile(rf"^{re.escape(kw)}(_?\w+)?$", flags=re.I)
        for lc, orig in low.items():
            if pat.match(lc):
                return orig
    return None

def autodetect_columns(df: pd.DataFrame):
    cols = list(df.columns)
    tgt = _find_col(cols, KEYS["target"])
    ld  = _find_col(cols, KEYS["load"])
    cdd = _find_col(cols, KEYS["cdd"])
    hdd = _find_col(cols, KEYS["hdd"])
    rnw = _find_col(cols, KEYS["renew"])

    missing = []
    if tgt is None: missing.append("Price (target)")
    if ld  is None: missing.append("Load")
    if cdd is None: missing.append("CDD")
    if hdd is None: missing.append("HDD")
    if rnw is None: missing.append("RenewableShare")

    if missing:
        raise KeyError(
            "Could not find required columns in preprocessed_data.csv:\n"
            f"  Missing: {missing}\n"
            f"  Available columns: {cols}\n"
            "Tip: rename your headers or extend KEYS in this script."
        )
    return tgt, [ld, cdd, hdd, rnw]

def run_ols_regression(
    data_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
    coef_csv: Path = COEF_CSV,
    resid_png: Path = RESID_PNG,
):
    if not data_path.exists():
        raise FileNotFoundError(f"Missing data at {data_path}. Run data_loader.py first.")

    df = pd.read_csv(data_path)

    # drop obvious non-feature columns if present
    for c in ("date", "Date", "DATE", "timestamp", "time"):
        if c in df.columns:
            # don’t drop yet; just avoid selecting as a regressor
            pass

    target_col, features = autodetect_columns(df)

    d = df[[target_col] + features].dropna().copy()
    y = d[target_col].astype(float)
    X = d[features].astype(float)
    X = sm.add_constant(X, has_constant="add")

    model = sm.OLS(y, X).fit()
    print(model.summary())

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"[done] Saved model → {model_path}")

    coef_df = pd.DataFrame({
        "term": model.params.index,
        "coef": model.params.values,
        "std_err": model.bse.values,
        "t_or_z": model.tvalues.values,
        "p_value": model.pvalues.values,
    }).round(6)
    coef_df.to_csv(coef_csv, index=False)
    print(f"[done] Wrote coefficients → {coef_csv}")

    plt.figure(figsize=(9, 5.5))
    plt.scatter(model.fittedvalues, model.resid, s=12)
    plt.axhline(0, linewidth=1)
    plt.xlabel("Fitted")
    plt.ylabel("Residual")
    plt.title("OLS Residuals vs Fitted")
    plt.tight_layout()
    plt.savefig(resid_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[done] Saved residuals plot → {resid_png}")

    return model

if __name__ == "__main__":
    print(f"[info] BASE_DIR   = {BASE_DIR}")
    print(f"[info] DATA_PATH  = {DATA_PATH}")
    print(f"[info] MODEL_PATH = {MODEL_PATH}")
    run_ols_regression()


# regression_report.py
from pathlib import Path
import pickle
import pandas as pd
import numpy as np

# ---------- Portable, repo-relative paths ----------
BASE_DIR   = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "ols_model.pkl"
DATA_PATH  = BASE_DIR / "preprocessed_data.csv"
REPORT_PATH = BASE_DIR / "ols_regression_report.md"

def generate_regression_report(model_path: Path = MODEL_PATH,
                               data_path: Path = DATA_PATH,
                               report_path: Path = REPORT_PATH) -> Path:
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model at {model_path}. Run `python ols_regression.py` first.")
    if not data_path.exists():
        raise FileNotFoundError(f"Missing data at {data_path}. Run `python data_loader.py` first.")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    df = pd.read_csv(data_path)

    # --- Collect model stats (robust to different statsmodels types) ---
    dep_var   = getattr(model.model, "endog_names", "y")
    nobs      = getattr(model, "nobs", len(getattr(model.model, "endog", [])))
    r2        = getattr(model, "rsquared", None)
    r2_adj    = getattr(model, "rsquared_adj", None)
    aic       = getattr(model, "aic", None)
    bic       = getattr(model, "bic", None)
    fvalue    = getattr(model, "fvalue", None)
    f_pvalue  = getattr(model, "f_pvalue", None)

    # Coeff table
    params = model.params
    conf   = model.conf_int()
    pvals  = model.pvalues
    coef_df = pd.DataFrame({
        "coef": params,
        "std_err": getattr(model, "bse", pd.Series(index=params.index, dtype=float)),
        "t_or_z": getattr(model, "tvalues", pd.Series(index=params.index, dtype=float)),
        "p_value": pvals,
        "ci_low": conf[0],
        "ci_high": conf[1],
    })
    coef_df = coef_df.rename_axis("term").reset_index()
    coef_df = coef_df.round(6)

    # Markdown table for coefficients (first 120 terms to keep file reasonable)
    def to_md_table(df: pd.DataFrame, max_rows: int = 120) -> str:
        show = df.head(max_rows)
        return show.to_markdown(index=False)

    # Build markdown
    lines = []
    lines.append(f"# OLS Regression Report")
    lines.append("")
    lines.append(f"- **Working dir**: `{BASE_DIR}`")
    lines.append(f"- **Model file** : `{model_path.name}`")
    lines.append(f"- **Data file**  : `{data_path.name}`")
    lines.append("")
    lines.append("## Model Summary (key stats)")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| Dependent var | `{dep_var}` |")
    lines.append(f"| N (obs) | {int(nobs) if pd.notna(nobs) else 'NA'} |")
    lines.append(f"| R² | {r2:.6f} |" if r2 is not None else "| R² | NA |")
    lines.append(f"| Adj. R² | {r2_adj:.6f} |" if r2_adj is not None else "| Adj. R² | NA |")
    lines.append(f"| F-stat | {fvalue:.6f} |" if fvalue is not None else "| F-stat | NA |")
    lines.append(f"| Prob(F) | {f_pvalue:.6g} |" if f_pvalue is not None else "| Prob(F) | NA |")
    lines.append(f"| AIC | {aic:.6f} |" if aic is not None else "| AIC | NA |")
    lines.append(f"| BIC | {bic:.6f} |" if bic is not None else "| BIC | NA |")
    lines.append("")
    lines.append("## Coefficients")
    lines.append("")
    lines.append(to_md_table(coef_df))
    lines.append("")
    lines.append("> Note: Values rounded to 6 decimals. Confidence intervals are usually 95% by default in statsmodels.")

    # Save
    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")
    print(f"[done] Wrote report → {report_path}")
    return report_path

def main():
    print(f"[info] BASE_DIR   = {BASE_DIR}")
    print(f"[info] MODEL_PATH = {MODEL_PATH}")
    print(f"[info] DATA_PATH  = {DATA_PATH}")
    print(f"[info] REPORT_OUT = {REPORT_PATH}")
    generate_regression_report()

if __name__ == "__main__":
    main()

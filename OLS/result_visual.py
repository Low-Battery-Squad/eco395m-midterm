# result_visual.py
from pathlib import Path
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Portable, repo-relative paths ----------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "ols_model.pkl"
DATA_PATH = BASE_DIR / "preprocessed_data.csv"
FIG_PATH = BASE_DIR / "ols_fitted_actual.png"

def load_model_and_data(model_path: Path = MODEL_PATH, data_path: Path = DATA_PATH):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Missing model file: {model_path}\n"
            "Run `python ols_regression.py` first to create it."
        )
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    if not data_path.exists():
        raise FileNotFoundError(
            f"Missing data file: {data_path}\n"
            "Run `python data_loader.py` (or your preprocessing step) to create it."
        )
    df = pd.read_csv(data_path)
    return model, df

def build_plot_df(model, df: pd.DataFrame) -> pd.DataFrame:
    # Get actual y from the model/df in a robust way
    target_name = getattr(model.model, "endog_names", None)
    if target_name and target_name in df.columns:
        actual = df[target_name].reset_index(drop=True)
    else:
        # Fall back to endog from the fitted model
        actual = pd.Series(getattr(model.model, "endog", []), name=target_name or "y").reset_index(drop=True)

    fitted = pd.Series(model.fittedvalues, name="fitted").reset_index(drop=True)

    # Align lengths safely
    n = min(len(actual), len(fitted))
    plot_df = pd.DataFrame({
        "obs": range(1, n + 1),
        "actual": actual.iloc[:n].values,
        "fitted": fitted.iloc[:n].values,
    })
    return plot_df

def make_plot(plot_df: pd.DataFrame, fig_path: Path = FIG_PATH):
    # Line plot over observation index; defaults use matplotlib's colors
    plt.figure(figsize=(9, 5.5))
    plt.plot(plot_df["obs"], plot_df["actual"], label="Actual", linewidth=1.6)
    plt.plot(plot_df["obs"], plot_df["fitted"], label="Fitted", linewidth=1.6)
    plt.xlabel("Observation")
    plt.ylabel("Value")
    plt.title("OLS: Actual vs. Fitted")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()

def main():
    print(f"[info] BASE_DIR     = {BASE_DIR}")
    print(f"[info] MODEL_PATH   = {MODEL_PATH}")
    print(f"[info] DATA_PATH    = {DATA_PATH}")
    print(f"[info] Output figure= {FIG_PATH}")

    model, df = load_model_and_data()
    plot_df = build_plot_df(model, df)
    make_plot(plot_df)
    print(f"[done] Saved figure → {FIG_PATH}")

if __name__ == "__main__":
    main()


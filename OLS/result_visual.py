import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from matplotlib import rcParams

# Configure plot settings (avoid Chinese font issues; use English fonts by default)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False  # Fix negative sign display


def load_model_and_data(model_path: str = "/Users/szs/eco395m-midterm/OLS/ols_model.pkl",
                        data_path: str = "/Users/szs/eco395m-midterm/OLS/preprocessed_data.csv"):
    """
    Load the saved OLS model and preprocessed data, then calculate fitted values.

    Args:
        model_path (str): Path to the saved pickle model
        data_path (str): Path to preprocessed data

    Returns:
        tuple: (loaded_model, data_with_fitted)
            - loaded_model: statsmodels OLS model object
            - data_with_fitted: DataFrame with actual values and fitted values
    """
    # Load the saved model
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    # Load preprocessed data
    df = pd.read_csv(data_path)
    # Calculate fitted values (y_hat) using the loaded model
    X_with_const = sm.add_constant(df[["ln_Load", "CDD_t", "HDD_t", "RenewableShare_t"]])
    df["ln_Price_fitted"] = model.predict(X_with_const)
    return model, df


def plot_coefficients(model):
    """
    Plot regression coefficients with 95% confidence intervals.

    Args:
        model: statsmodels OLS model object (with fitted results)
    """
    # Extract coefficients and 95% confidence intervals
    coefs = model.params
    conf_int = model.conf_int()  # Columns: [2.5%, 97.5%]
    # Exclude constant term to focus on independent variables
    coefs = coefs.drop("const")
    conf_int = conf_int.drop("const")

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    x_pos = np.arange(len(coefs))
    # Plot coefficient bars
    ax.bar(x_pos, coefs.values,
           color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
           alpha=0.7)
    # Add error bars for confidence intervals
    ax.errorbar(x_pos, coefs.values,
                yerr=[coefs.values - conf_int[0].values, conf_int[1].values - coefs.values],
                fmt='none', color='black', capsize=5)
    # Add labels and title
    ax.set_xticks(x_pos)
    ax.set_xticklabels(["ln(Load)", "CDD", "HDD", "RenewableShare"], fontsize=12)
    ax.set_ylabel("Regression Coefficient (β)", fontsize=12)
    ax.set_title("OLS Regression Coefficients with 95% Confidence Intervals", fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)  # Horizontal line at y=0 (tests significance)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    # Save plot
    plt.savefig("./ols_coefficients_plot.png", dpi=300, bbox_inches='tight')
    print("Coefficient plot saved to OLS/ols_coefficients_plot.png")


def plot_fitted_vs_actual(df):
    """
    Plot actual values vs. fitted values of ln(Price_t) to evaluate model fit.

    Args:
        df (pd.DataFrame): DataFrame with "date", "ln_Price", and "ln_Price_fitted" columns
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    # Sort data by date to show time trend clearly
    df_sorted = df.sort_values("date")
    # Plot actual and fitted values
    ax.plot(df_sorted["date"], df_sorted["ln_Price"],
            label="Actual ln(Price)", color='#1f77b4', alpha=0.8)
    ax.plot(df_sorted["date"], df_sorted["ln_Price_fitted"],
            label="Fitted ln(Price)", color='#ff7f0e', alpha=0.8, linestyle='--')
    # Add labels and title
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("ln(Price)", fontsize=12)
    ax.set_title("OLS Regression: Actual vs. Fitted Values of ln(Price)", fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    # Rotate date labels to avoid overlap
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    # Save plot
    plt.savefig("./ols_fitted_actual.png", dpi=300, bbox_inches='tight')
    print("Actual vs. Fitted plot saved to OLS/ols_fitted_actual.png")


def plot_residuals(df):
    """
    Plot residual distribution (histogram) and residual time trend to test OLS assumptions.

    Args:
        df (pd.DataFrame): DataFrame with "date", "ln_Price", and "ln_Price_fitted" columns
    """
    # Calculate residuals (actual - fitted)
    df["residuals"] = df["ln_Price"] - df["ln_Price_fitted"]

    # Create subplots for residual analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    # Subplot 1: Residual distribution histogram (tests normality)
    ax1.hist(df["residuals"], bins=30, color='#2ca02c', alpha=0.7, edgecolor='black')
    ax1.set_xlabel("Residuals", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.set_title("Residual Distribution Histogram", fontsize=14, fontweight='bold')
    ax1.grid(alpha=0.3)

    # Subplot 2: Residual time trend (tests for autocorrelation)
    df_sorted = df.sort_values("date")
    ax2.plot(df_sorted["date"], df_sorted["residuals"], color='#d62728', alpha=0.6)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.8)  # Horizontal line at y=0
    ax2.set_xlabel("Date", fontsize=12)
    ax2.set_ylabel("Residuals", fontsize=12)
    ax2.set_title("Residual Time Trend", fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    # Save plot
    plt.savefig("./ols_residuals_analysis.png", dpi=300, bbox_inches='tight')
    print("Residual analysis plots saved to OLS/ols_residuals_analysis.png")


# Execute all visualization functions when running this script
if __name__ == "__main__":
    import statsmodels.api as sm  # Re-import to avoid cross-file dependency issues

    model, df = load_model_and_data()
    plot_coefficients(model)
    plot_fitted_vs_actual(df)
    plot_residuals(df)
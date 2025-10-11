import pandas as pd
import statsmodels.api as sm  # Preferred for comprehensive regression statistics
from statsmodels.stats.stattools import durbin_watson  # Test for residual autocorrelation


def run_ols_regression(data_path: str = "/Users/szs/eco395m-midterm/OLS/preprocessed_data.csv"):
    """
    Execute OLS regression based on the specified model formula:
    ln(Price_t) = β₀ + β₁×ln(Load_t) + β₂×CDD_t + β₃×HDD_t + β₄×RenewableShare_t + ε_t

    Steps:
    1. Load preprocessed data
    2. Define dependent variable (y) and independent variables (X)
    3. Add constant term (β₀) to independent variables
    4. Fit OLS model and output detailed results
    5. Conduct additional diagnostic tests (e.g., Durbin-Watson)
    6. Save key results to CSV for further analysis

    Args:
        data_path (str): Path to preprocessed data

    Returns:
        tuple: (fitted_ols_model, results_dict)
            - fitted_ols_model: statsmodels OLS model object
            - results_dict: Dictionary of key regression statistics
    """
    # Step 1: Load preprocessed data
    df = pd.read_csv(data_path)

    # Step 2: Define variables (match the regression formula)
    y = df["ln_Price"]  # Dependent variable: ln(Price_t)
    X = df[["ln_Load", "CDD_t", "HDD_t", "RenewableShare_t"]]  # Independent variables

    # Step 3: Add constant term (statsmodels does not include intercept by default)
    X_with_const = sm.add_constant(X)
    print("Independent variables (with constant term):", X_with_const.columns.tolist())

    # Step 4: Fit OLS model
    ols_model = sm.OLS(y, X_with_const).fit()

    # Step 5: Print detailed regression results (includes coefficients, p-values, R², etc.)
    print("\n" + "=" * 80)
    print("Detailed OLS Regression Results")
    print("=" * 80)
    print(ols_model.summary())

    # Step 6: Additional diagnostic tests
    # 6.1 Durbin-Watson test (tests for residual autocorrelation; ~2 = no autocorrelation)
    dw_stat = durbin_watson(ols_model.resid)
    print(f"\nDurbin-Watson Statistic: {dw_stat:.4f} (values near 2 indicate no residual autocorrelation)")

    # 6.2 Extract key results for visualization and reporting
    results = {
        "coefficients": ols_model.params,  # Regression coefficients (β₀ to β₄)
        "p_values": ols_model.pvalues,  # P-values for significance testing
        "r_squared": ols_model.rsquared,  # R-squared (goodness of fit)
        "adj_r_squared": ols_model.rsquared_adj,  # Adjusted R-squared (accounts for number of variables)
        "f_statistic": ols_model.fvalue,  # F-statistic for overall model significance
        "f_pvalue": ols_model.f_pvalue,  # P-value for F-statistic
        "residuals": ols_model.resid  # Residuals (for residual analysis)
    }

    # Step 7: Save coefficients and significance to CSV
    results_df = pd.DataFrame({
        "Variable": results["coefficients"].index,
        "Regression_Coefficient(β)": results["coefficients"].values,
        "P_Value": results["p_values"].values,
        "Significance": ["***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else "ns"
                         for p in results["p_values"].values]
    })
    results_df.to_csv("./ols_coefficients.csv", index=False, encoding="utf-8-sig")
    print(f"\nRegression coefficients saved to OLS/ols_coefficients.csv")

    return ols_model, results


# Test: Run regression when executing this script independently
if __name__ == "__main__":
    model, results = run_ols_regression()
    # Save fitted model for later reuse (avoids re-fitting)
    import pickle

    with open("./ols_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("Fitted OLS model saved to OLS/ols_model.pkl")
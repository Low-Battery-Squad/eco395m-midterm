import pandas as pd
import pickle
import statsmodels.api as sm


def generate_regression_report(model_path: str = "/Users/szs/eco395m-midterm/OLS/ols_model.pkl",
                               data_path: str = "/Users/szs/eco395m-midterm/OLS/preprocessed_data.csv",
                               report_path: str = "/Users/szs/eco395m-midterm/OLS/ols_regression_report.md"):
    """
    Generate a structured markdown report for the OLS regression analysis.
    The report includes data overview, model specification, results interpretation, and conclusions.

    Args:
        model_path (str): Path to the saved OLS model (default: "./ols_model.pkl")
        data_path (str): Path to preprocessed data (default: "./preprocessed_data.csv")
        report_path (str): Path to save the markdown report (default: "./ols_regression_report.md")
    """
    # Load fitted model and preprocessed data
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    df = pd.read_csv(data_path)

    # Extract key regression statistics
    coefs = model.params
    p_values = model.pvalues
    r2 = model.rsquared
    adj_r2 = model.rsquared_adj
    f_stat = model.fvalue
    f_pval = model.f_pvalue
    n_obs = model.nobs  # Number of observations

    # Define significance labels for coefficients
    def get_significance(p_val):
        if p_val < 0.01:
            return "***"
        elif p_val < 0.05:
            return "**"
        elif p_val < 0.1:
            return "*"
        else:
            return "ns"

    # Construct markdown report content
    report_content = f"""# OLS Regression Analysis Report
## 1. Background and Model Specification
### 1.1 Data Overview
- Time range: January 1, 2024 to December 30, 2024 (total {n_obs} observations)
- Key variables:
  - Dependent variable: `ln(Price_t)` (Natural logarithm of electricity price)
  - Independent variables:
    - `ln(Load_t)` (Natural logarithm of electricity load)
    - `CDD_t` (Cooling Degree Days, measures summer cooling demand)
    - `HDD_t` (Heating Degree Days, measures winter heating demand)
    - `RenewableShare_t` (Share of renewable energy in total supply)

### 1.2 Regression Model Formula
The OLS regression model used in this analysis is consistent with the requirements:
    Where:
    - β₀: Constant term (intercept)
    - β₁~β₄: Regression coefficients for independent variables
    - ε_t: Random error term (residuals)

    ## 2. Key Regression Results
    ### 2.1 Model Goodness of Fit
    - R-squared: {r2:.4f} → The model explains {r2 * 100:.2f}% of the variance in the dependent variable
    - Adjusted R-squared: {adj_r2:.4f}
    - F-statistic: {f_stat:.4f}, P-value: {f_pval:.6f} → {'Model is overall significant (P<0.05)' if f_pval < 0.05 else 'Model is not overall significant (P≥0.05)'}

    ### 2.2 Regression Coefficients and Significance
    | Variable                | Coefficient(β) | P-Value   | Significance | Interpretation                                                                 |
    |-------------------------|----------------|-----------|--------------|--------------------------------------------------------------------------------|
    | Constant Term (β₀)      | {coefs["const"]:.4f} | {p_values["const"]:.6f} | {get_significance(p_values["const"])} | Baseline value of ln(Price) when all independent variables are 0 |
    | ln(Load_t) (β₁)         | {coefs["ln_Load"]:.4f} | {p_values["ln_Load"]:.6f} | {get_significance(p_values["ln_Load"])} | A 1% increase in load leads to a {coefs["ln_Load"] * 100:.2f}% average change in price (elasticity) |
    | CDD_t (β₂)              | {coefs["CDD_t"]:.4f} | {p_values["CDD_t"]:.6f} | {get_significance(p_values["CDD_t"])} | A 1-unit increase in CDD leads to a {coefs["CDD_t"]:.4f} average change in ln(Price) |
    | HDD_t (β₃)              | {coefs["HDD_t"]:.4f} | {p_values["HDD_t"]:.6f} | {get_significance(p_values["HDD_t"])} | A 1-unit increase in HDD leads to a {coefs["HDD_t"]:.4f} average change in ln(Price) |
    | RenewableShare_t (β₄)   | {coefs["RenewableShare_t"]:.4f} | {p_values["RenewableShare_t"]:.6f} | {get_significance(p_values["RenewableShare_t"])} | A 1-unit increase in renewable share leads to a {coefs["RenewableShare_t"]:.4f} average change in ln(Price) |

    *Significance notes: *** p<0.01, ** p<0.05, * p<0.1, ns = not significant

    """

    # Save report to markdown file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Regression report saved to {report_path}")
    print("\nReport Preview (first 500 characters):")
    print(report_content[:500] + "...")


# Generate report when running this script independently
if __name__ == "__main__":
    generate_regression_report()
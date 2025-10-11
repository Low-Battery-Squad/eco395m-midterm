# OLS Regression Analysis Report
## 1. Background and Model Specification
### 1.1 Data Overview
- Time range: January 1, 2024 to December 30, 2024 (total 364.0 observations)
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
    - R-squared: 0.4282 → The model explains 42.82% of the variance in the dependent variable
    - Adjusted R-squared: 0.4218
    - F-statistic: 67.1980, P-value: 0.000000 → Model is overall significant (P<0.05)

    ### 2.2 Regression Coefficients and Significance
    | Variable                | Coefficient(β) | P-Value   | Significance | Interpretation                                                                 |
    |-------------------------|----------------|-----------|--------------|--------------------------------------------------------------------------------|
    | Constant Term (β₀)      | -17.5899 | 0.001216 | *** | Baseline value of ln(Price) when all independent variables are 0 |
    | ln(Load_t) (β₁)         | 2.0184 | 0.000078 | *** | A 1% increase in load leads to a 201.84% average change in price (elasticity) |
    | CDD_t (β₂)              | -0.0289 | 0.005209 | *** | A 1-unit increase in CDD leads to a -0.0289 average change in ln(Price) |
    | HDD_t (β₃)              | -0.0101 | 0.089519 | * | A 1-unit increase in HDD leads to a -0.0101 average change in ln(Price) |
    | RenewableShare_t (β₄)   | -2.6977 | 0.000000 | *** | A 1-unit increase in renewable share leads to a -2.6977 average change in ln(Price) |

    *Significance notes: *** p<0.01, ** p<0.05, * p<0.1, ns = not significant

    
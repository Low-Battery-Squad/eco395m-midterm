import pandas as pd
import numpy as np


def load_and_preprocess_data(data_path: str = "/Users/szs/eco395m-midterm/DataCleaning/ALL_IN_ONE.csv"):
    """
    Load and preprocess the dataset for OLS regression:
    1. Read the CSV file from the specified path
    2. Remove rows with negative Price_t (and their corresponding data)
    3. Handle missing values (drop rows with missing data)
    4. Apply log transformation to Price_t and Load_t
    5. Return the preprocessed DataFrame
    """
    # Step 1: Load raw data
    df = pd.read_csv(data_path)
    print(f"Original data shape: {df.shape}")

    # Step 2: Drop if the value is invalid
    negative_price_count = (df["Price_t"] < 0).sum()
    print(f"Number of rows with negative Price_t: {negative_price_count}")
    df = df[df["Price_t"] >= 0]
    print(f"Data shape after removing negative Price_t: {df.shape}")

    # Step 3: Drop rows with missing values
    df = df.dropna()
    print(f"Data shape after dropping missing values: {df.shape}")

    # Step 4: Log transformation (now safe without negative values)
    df["ln_Price"] = np.log(df["Price_t"] + 0.001)  # 加0.001避免log(0)
    df["ln_Load"] = np.log(df["Load_t"] + 0.001)

    print("First 5 rows of preprocessed data:")
    print(df[["date", "ln_Price", "ln_Load", "CDD_t", "HDD_t", "RenewableShare_t"]].head())
    print("\nDescriptive statistics of preprocessed variables:")
    print(df[["ln_Price", "ln_Load", "CDD_t", "HDD_t", "RenewableShare_t"]].describe())

    return df


if __name__ == "__main__":
    preprocessed_df = load_and_preprocess_data()
    preprocessed_df.to_csv("./preprocessed_data.csv", index=False)
    print("\nPreprocessed data saved to OLS/preprocessed_data.csv")
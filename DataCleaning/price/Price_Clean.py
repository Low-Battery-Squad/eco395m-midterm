import os
import pandas as pd

RAW_DIR = "DataScraping/Rawdata"
OUT_DIR = "DataCleaning/price"

def clean_price():
    src = os.path.join(RAW_DIR, "price", "Price.xlsx")
    if not os.path.exists(src):
        raise FileNotFoundError(f"Price file not found: {src}")

    xls = pd.ExcelFile(src) #Obtain it in months
    df = pd.concat(pd.read_excel(xls, sheet_name=s) for s in xls.sheet_names)

    df = df[df["Settlement Point Name"] == "HB_BUSAVG"] #keep HB_BUSAVG only

    df["Delivery Date"] = pd.to_datetime(df["Delivery Date"])

    
    hourly = (     # date x hours
        df.groupby(["Delivery Date", "Delivery Hour"])["Settlement Point Price"]
          .mean()
          .reset_index()
    )

    daily = (          #price,daily
        hourly.groupby("Delivery Date")["Settlement Point Price"]
              .mean()
              .reset_index()
              .rename(columns={"Delivery Date": "date",
                               "Settlement Point Price": "Price_t"})
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "Price_Clean.csv")
    daily.to_csv(out_path, index=False)
    print(f"Successfuly Saved: {out_path} (rows={len(daily)})")

if __name__ == "__main__":
    clean_price()

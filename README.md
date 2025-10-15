# ECO 395m Midterm Project: Texas Energy Market Analytics

**Group Members:** Linyao(Bob) Ni, Zhifang Luo, 

## 0. Instructions for Re-running the Code

* To reproduce the results of our flight delay prediction analysis, follow the steps below:

**Data Collection**  
  
**Data Preprocessing**
  
**Data Analysis**  
    
**Data Visualization**

## 1. Background  

## 2. Data Scraping  
  
**1. Overview of Data Sources**

The datasets were collected from four major sources: ERCOT’s public data portal, NOAA’s Climate Data Online (CDO) API, and manually downloaded ERCOT load archives.
Depending on data accessibility, three methods were used:  
(1) direct URL download within Python scripts,  
(2) manual download from the ERCOT portal, and  
(3) authenticated API requests using a personal NOAA token.  

**2. Variable: Price_t**

Source: ERCOT MIS “Real-Time Market Load Zone and Hub Settlement Point Prices (RTMLZHBSPP_2024.zip)”  
Download method: Automated download via Python script using ERCOT’s public URL.  
Saved file: Rawdata/price/Price.xlsx  

This dataset contains hourly real-time electricity prices by load zone and hub for the year 2024.
Each record includes delivery date, delivery hour, settlement point name, and settlement point price.
For analysis, only rows with Settlement Point Name = HB_BUSAVG are retained to represent the ERCOT-wide average market price.
Hourly prices will later be aggregated to daily averages during the data cleaning stage.  
  
**3. Variable: Load_t**
  
Source: ERCOT “Actual System Load by Weather Zone” reports for 2024.  
Download method: Manual download, followed by automated extraction via Python.  
Saved files: Uncompressed CSVs under Rawdata/load/load_raw_data/  

Because ERCOT’s website requires manual selection of date ranges, the complete set of 366 daily load reports(range from 1/1/2024 00:00 to 12/31/2024 23:59) for 2024 was downloaded manually as a single zip file from:  

https://data.ercot.com/data-product-archive/NP6-346-CD  

The script automatically extracts the main archive, unzips all 366 sub-archives (one per day), and removes the temporary compressed files while keeping the raw CSVs.  

Each CSV contains hourly system loads for all ERCOT weather zones, including columns for date, hour ending, settlement point (zone name), and load in megawatts (MW).These data will later be aggregated into daily total system load.  

**4. Variable: CDD/HDD_t**  
  
Source: NOAA Climate Data Online (CDO) API.  
Download method: API retrieval through authenticated requests using a NOAA token stored in .env. This file was not commited to Github and a private token is needed for reproduction.
Saved file: Rawdata/CDD_HDD/noaa_raw.csv  
  
Daily temperature observations for 2024 were collected from four representative weather stations corresponding to ERCOT regions: Houston, North, South, and West.  
Each record includes the observation date, zone name, station ID, temperature type (TMIN, TMAX, or TAVG), and temperature value in Fahrenheit.  
These temperature data will be used to compute Cooling Degree Days (CDD) and Heating Degree Days (HDD) for each zone in later analysis, and they'll be averaged to represent as the state average.

**5. Variable: RenewableShare_t**  
  
Source: ERCOT “Fuel Mix Reports (Previous Years)” archive.  
Download method: Automated download via Python script using ERCOT’s public ZIP archive.  
Saved file: Rawdata/RenewableShare/IntGenbyFuel2024.xlsx  

The script downloads the entire archive, extracts all files, and retains only the 2024 workbook (IntGenbyFuel2024.xlsx).  
All other files, including those from previous years, are removed after extraction.  

The dataset records daily electricity generation by fuel type, including wind, solar, hydro, coal, natural gas, and nuclear.  
The renewable share for each day will later be computed as the sum of wind, solar, and hydro generation divided by total generation.
## 3. Data Cleaning
This part describes the data cleaning stage for the midterm project.  
All cleaning operations are by using Python to ensure reproducibility.  
The cleaned output serves as the foundation for OLS and visualization.

---

## 3.1 Overview of Cleaning Process

The cleaning process follows three main steps:

1. **Data Import**  
   Multiple raw datasets collected from the `DataScraping/` module provided by my teammate are merged using date-based keys to create a unified data frame.  
   The merge ensures consistent temporal alignment across all variables, all variables should be counted as 365 value(365 days in a year).

2. **Data Transformation**  
   The script standardizes variable names, converts data types.

3. **Handling Missing Values**  
   Actually there is no observations with invalid or out-of-range values.

---

## 3.2 The Script

**Purpose:**  
The main script automates the entire cleaning pipeline — reading, merging, transforming, and saving the final processed dataset.
Each variable have a corresbonding script prresented in the folder, which can be used for reproduction.

**Other Operations:**
- Removes duplicates and invalid rows  
- Renames inconsistent columns

---

Below is a summary of how each major variable was cleaned and prepared for analysis:

| Variable | Source | Cleaning Steps | Notes |
|-----------|---------|----------------|-------|
| **price_t** | ERCOT MIS "Real-Time Market Load Zone and Hub Settlement Point Prices" | - Filtered for `Settlement Point Name = HB_BUSAVG` to represent ERCOT-wide average price.<br> - Aggregated hourly prices to daily averages.<br> - Applied logarithmic transformation to stabilize variance. | Final variable used as `log(price_t)` in OLS regression. |
| **sales_t** | ERCOT Residential Load Data | - Aggregated monthly residential electricity sales and normalized by population.<br> - Interpolated to daily frequency using linear interpolation.<br> - Checked for negative or missing values and filled forward if necessary. | Represents per-capita daily residential electricity consumption. |
| **income_t** | Bureau of Economic Analysis (BEA) – State Personal Income |  - Converted to per-capita units.<br> - Interpolated monthly to daily frequency. | Used to capture income effects on electricity demand. |
| **gas_price_t** | U.S. Energy Information Administration (EIA) – Residential Natural Gas Prices |  - Interpolated to daily frequency.<br> - Smoothed to remove irregular jumps. | Serves as substitute/complement variable for energy cost. |
| **cdd_t** | NOAA Climate Data Online (CDO) API | - Calculated daily Cooling Degree Days from temperature data.<br> - Checked range validity.<br>  | Reflects cooling demand intensity. |
| **hdd_t** | NOAA Climate Data Online (CDO) API | - Calculated daily Heating Degree Days from temperature data.<br>  - Smoothed using 3-day rolling average. | Reflects heating demand intensity. |

## 4. Data Analysis(OLS Model)  

## 5. Result and Visualization

## 6. Conclusion 

## 7. limitation


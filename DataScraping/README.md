**Data Scraping Documentation**  

This document describes the data collection process. Each variable represents a key input in the econometric model and corresponds to a distinct dataset retrieved from public sources.  
All raw data are stored in the DataScraping/Rawdata directory. Except for the load-related data, which must be downloaded manually from the ERCOT website,
running the DataScraping.py file will automatically retrieve and organize all other datasets.
  
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
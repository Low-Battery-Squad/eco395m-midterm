# ECO 395m Midterm Project: Texas Energy Market Analytics

**Group Members:** Linyao(Bob) Ni, 

## 0. Instructions for Re-running the Code

* To reproduce the results of our flight delay prediction analysis, follow the steps below:

**Data Collection**  
  
**Data Preprocessing**
  
**Data Analysis**  
    
**Data Visualization**

## 1. Background  

## 2. Data Scraping
This part describes the data cleaning stage for the midterm project.  
All cleaning operations are by using Python to ensure reproducibility.  
The cleaned output serves as the foundation for OLS and visualization.

---

## 1. Overview of Cleaning Process

The cleaning process follows three main steps:

1. **Data Import**  
   Multiple raw datasets collected from the `DataScraping/` module provided by my teammate are merged using date-based keys to create a unified data frame.  
   The merge ensures consistent temporal alignment across all variables, all variables should be counted as 365 value(365 days in a year).

2. **Data Transformation**  
   The script standardizes variable names, converts data types.

3. **Handling Missing Values**  
   Actually there is no observations with invalid or out-of-range values.

---

## 2. The Script

**Purpose:**  
The main script automates the entire cleaning pipeline — reading, merging, transforming, and saving the final processed dataset.
Each variable have a corresbonding script prresented in the folder, which can be used for reproduction.

**Other Operations:**
- Removes duplicates and invalid rows  
- Renames inconsistent columns  
## 3. Data Cleaning

## 4. Data Analysis(OLS Model)  

## 5. Result and Visualization

## 6. Conclusion 

## 7. limitation


# Amazon Borders FBA Report Generator

## Table of Contents

- [Amazon Borders FBA Report Generator](#amazon-borders-fba-report-generator)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Initial Setup](#initial-setup)
    - [Install Git](#install-git)
    - [Install Python](#install-python)
    - [Install ngrok](#install-ngrok)
    - [Set Up Python Path](#set-up-python-path)
    - [Install the Application](#install-the-application)
  - [Generating the Report](#generating-the-report)
    - [Export Files from Amazon](#export-files-from-amazon)
      - [Handling Weekly Shipment Reports](#handling-weekly-shipment-reports)
    - [Run the Script](#run-the-script)
    - [Understand the Output](#understand-the-output)
    - [Import CSV to Google Docs](#import-csv-to-google-docs)
    - [Close the Server](#close-the-server)
  - [Folder Cleaning Function](#folder-cleaning-function)
  - [Configuration File Usage](#configuration-file-usage)
    - [How to Use the Configuration File](#how-to-use-the-configuration-file)
    - [Handling Errors Related to Column Names](#handling-errors-related-to-column-names)
  - [Key Features \& Logic](#key-features--logic)
    - [FBA/Merchant Classification](#fbamerchant-classification)
    - [SKU Mapping and Border Identification](#sku-mapping-and-border-identification)
    - [Sales Forecasting \& Shipment Recommendation](#sales-forecasting--shipment-recommendation)
  - [Troubleshooting](#troubleshooting)

## Introduction

This tool is designed for OntWall to simplify the generation of a weekly report. This report is used to prepare orders for sending products to Amazon FBA. It integrates data from multiple Amazon reports, classifies listings, calculates sales forecasts, recommends shipment quantities, and identifies potential new border listings. This README file provides step-by-step instructions on how to set up and use the tool.

## Initial Setup

### Install Git

1. Download and install Git from the [official Git website](https://git-scm.com/downloads).
2. For detailed installation instructions, refer to this [Git Installation Guide](https://github.com/git-guides/install-git).

### Install Python

1. Download and install Python from the [official Python website](https://www.python.org/downloads/).
2. For detailed installation instructions, refer to this [Python Installation Guide](https://www.geeksforgeeks.org/installation-of-python/).

### Install ngrok

1. Install ngrok from the file `Setup/ngrok.exe` provided with this tool.
2. Alternatively, you can download ngrok from the [official ngrok website](https://ngrok.com/download).

### Set Up Python Path

If you've installed Python but it's not recognized by your system:

1. Restart your computer.
2. If the issue persists, follow these instructions to [Add Python to the Windows PATH](https://geek-university.com/add-python-to-the-windows-path/).

### Install the Application

1. Ensure you have a folder named "Setup" containing these three files:

   - SETUP.bat
   - clone_project.py
   - .env

2. Run the `SETUP.bat` file. This will clone the project into a new folder in the same directory.

3. You can move the newly created folder to any location for convenience.

4. To update the project in the future, simply run the installation process again.

5. Make sure you have a `.env` file with the following variables:

   ```
   NGROK_AUTH_TOKEN=
   NGROK_DOMAIN=
   GITHUB_REPO_URL=
   ```

6. If you don't have the `.env` file, or if any of the variables are missing or incorrect, the application will not work. In this case, contact the developer for assistance.

## Generating the Report

### Export Files from Amazon

1. Log in to your Amazon Seller Central account.
2. Export the following reports into their respective folders within the `amazon exports` directory:
   - `all_listings_report/`: "All listings report" (Essential for SKU classification, mapping, and template updates)
   - `FBA_Inventory/`: "FBA inventory report" (Used for FBA classification and current inventory levels)
   - `restock_report/`: "Restock Inventory report" (Currently used for potential future enhancements, ensure the file is present)
   - `30d/`: "Sales Report" for the last 30 days (Used for WMA forecast and M_30 calculation)
   - `60d/`: "Sales Report" for the last 60 days (Used for WMA forecast calculation)
   - `90d/`: "Sales Report" for the last 90 days (Used for WMA forecast calculation)
   - `12m/`: "Sales Report" for the last 12 months (Used for M_12M calculation)
   - `2yr/`: "Sales Report" for the last 2 years (Optional, data is included in the final report if available)
   - Weekly shipment reports for the last 4 weeks (`1_W/`, `2_W/`, `3_W/`, `4_W/`)

#### Handling Weekly Shipment Reports

- For weekly shipment reports, use the folders named '1_W', '2_W', '3_W', and '4_W'.
- If multiple shipments occurred in a single week, place all corresponding reports in the same folder.
- If there was a week without shipments, you can leave the corresponding folder empty. In this case, the respective column in the final report will remain empty.
- Note that if you accidentally leave any of the '1_W', '2_W', '3_W', or '4_W' folders empty, the program will not throw an error. Instead, it will simply leave the corresponding column empty in the final report.

### Run the Script

1. Run the `RUN.bat` file (or `RUN.command`/`RUN.sh` on macOS/Linux).
2. The script will process the files, perform calculations, and generate the output.
3. When the report generation is complete, you will see the message: "Program finished, results saved to results/result.csv" and the local server for Google Apps Script will be running.

### Understand the Output

The main output is the `results/result.csv` file, which is also imported into Google Sheets. Key columns include:

-   `FBA SKU`: The Seller SKU identified as the FBA listing. (Renamed from the old `SKU` column).
-   `M_SKU`: The corresponding Merchant SKU for the same product (ASIN). Will contain "-" for standalone Merchant listings.
-   Sales data columns (e.g., `30`, `60`, `90`, `12m`, `2yr`): Aggregated sales units for FBA SKUs over different periods.
-   Weekly shipment columns (`1_W` to `4_W`).
-   `M_30`: Units sold via the Merchant SKU in the last 30 days.
-   `M_12M`: Units sold via the Merchant SKU in the last 12 months.
-   `Forecast`: Weighted Moving Average (WMA) sales forecast for the next month for the FBA SKU.
-   `Rec Ship`: Recommended shipment quantity (`Forecast` - `FBA Inventory` - `Inbound`).
-   Other columns from the original reports and template.

### Import CSV to Google Docs

1. Open Google Docs.
2. Go to Extensions -> Macros.
3. Run the macro named `import_report`.
4. Grant necessary permissions, even if you see warning windows.
5. The macro will access the file through the running server and create a new tab with the report.
6. If an error occurs, delete the newly created table, restart the server, and try again.
7. If it still doesn't work, contact the script creator. You can still manually input data from the file `results/result.csv`.

**Note:** If you have created a new Google Sheet and it doesn't have the macro, you need to add it using Google Apps Script. Use the code from the `import_report.gs` file located in the project root for the function.

### Close the Server

1. When the macro execution is complete, press any key in the terminal to close the server.
2. Do not close the terminal using the close button, as it's may live the server running on the background, what can cause errors in the future.

## Folder Cleaning Function

This function is designed to eliminate the need for manual deletion of files in the Amazon exports folder before uploading new files, and to keep historical reports in the Reports history folder.

To run the function:

1. Execute the `CLEAN_FOLDERS.bat` (or `CLEAN_FOLDERS.command`/`CLEAN_FOLDERS.sh` on macOS/Linux) file.

## Configuration File Usage

The script uses a configuration file (`data/config.csv`) to manage the exact names of columns expected in the exported Amazon files. This allows the script to adapt if Amazon changes the column headers in their reports.

### How to Use the Configuration File

1. The `data/config.csv` file maps internal constant names (used by the script) to the actual column names found in Amazon's CSV files.
2. Key constants include:
   - `SELLER_SKU`, `SKU` (for FBA Inventory report), `ASIN1` (for All Listings)
   - `UNITS_ORDERED`, `UNITS_ORDERED_B2B` (for sales reports)
   - `AVAILABLE`, `INBOUND_QUANTITY` (for FBA Inventory)
   - `FBA_SKU`, `M_SKU`, `M_30`, `M_12M`, `WMA_FORECAST`, `REC_SHIP` (These usually map to the desired output column names, but could be adjusted if needed).

### Handling Errors Related to Column Names

1. If Amazon changes a column name in an export file that the script relies on, the script may terminate with an error message indicating the missing expected column name (based on the `config.csv` value).
2. To resolve this:
   a. Open the relevant Amazon export CSV file and find the new name for the column mentioned in the error.
   b. Open `data/config.csv`.
   c. Find the row corresponding to the internal constant mentioned in the error message.
   d. Update the `column name` value in that row with the new name found in the Amazon file.
   e. Save `data/config.csv` and rerun the script (`RUN.bat`).

## Key Features & Logic

### FBA/Merchant Classification

The script employs a robust classification logic to accurately distinguish between FBA and Merchant fulfilled listings, even when Amazon reports show inconsistencies (e.g., an FBA SKU listed as 'DEFAULT' fulfillment in the "All listings report").

1.  **Primary FBA Identification:** SKUs present in the "FBA inventory report" are definitively marked as FBA.
2.  **Secondary FBA Identification:** SKUs listed with `fulfillment-channel` as `AMAZON_NA` (or equivalent based on `config.csv`) in the "All listings report" are also marked as FBA.
3.  **Merchant Identification:** All remaining SKUs from the "All listings report" that were not identified as FBA are classified as Merchant.
4.  **Mapping:** The script then attempts to map FBA SKUs to their corresponding Merchant SKUs based on matching `ASIN1` values from the "All listings report". Standalone Merchant listings (those without a corresponding FBA SKU for the same ASIN) are included in the final report with `FBA SKU` set to "-".

### SKU Mapping and Border Identification

(Formerly "Template Update and SKU Mapping")

1.  **Automatic Template Update:** The `data/template.csv` file (used as a base for the final report) is automatically updated using the latest "All listings report" each time the script runs. This ensures new listings are included.
2.  **SKU Mapping Download:** The script downloads SKU mapping data from a configured Google Sheet `sku_mapping`. This mapping is crucial for identifying which listings are designated 'borders'.
3.  **Border Identification:** Listings are identified as 'borders' based on whether they have an entry in the downloaded mapping data or have word 'border' in the title.
4.  **Potential Unmapped Borders:** The script identifies listings that might be borders but are not yet mapped. Criteria include:
    *   Not having a 'border' mapping.
    *   Not having a 'Blue system' mapping.
    *   Containing "border" in the title OR having a price between $17 and $20 (configurable thresholds might apply).
    *   These potential borders are saved to `results/potential_not_mapped_borders.csv` for manual review and updating in the Google Sheet `sku_mapping`. Maintaining accurate mapping is vital.

### Sales Forecasting & Shipment Recommendation

To simplify inventory management, the script includes forecasting:

1.  **WMA Forecast:** Calculates a Weighted Moving Average forecast (`Forecast` column) for the next month's FBA sales. It uses sales data from the 30d, 60d, and 90d reports, and 12m report for M_12M calculation. Typically weighting recent sales more heavily (e.g., 3:2:1).
2.  **Recommended Shipment:** Calculates a recommended shipment quantity (`Rec Ship` column) using the formula: `Forecast - FBA Inventory - Inbound Quantity`. This provides a quick indicator of how much stock might be needed.

## Troubleshooting

If you encounter any issues not covered by this guide, please contact the script creator for further assistance.

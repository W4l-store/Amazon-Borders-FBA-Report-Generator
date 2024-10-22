# Amazon Borders FBA Report Generator

## Table of Contents

1. [Introduction](#introduction)
2. [Initial Setup](#initial-setup)
   - [Install Git](#install-git)
   - [Install Python](#install-python)
   - [Install ngrok](#install-ngrok)
   - [Set Up Python Path](#set-up-python-path)
   - [Install the Application](#install-the-application)
3. [Generating the Report](#generating-the-report)
   - [Export Files from Amazon](#export-files-from-amazon)
   - [Run the Script](#run-the-script)
   - [Import CSV to Google Docs](#import-csv-to-google-docs)
   - [Close the Server](#close-the-server)
4. [Folder Cleaning Function](#folder-cleaning-function)
5. [Configuration File Usage](#configuration-file-usage)
6. [Troubleshooting](#troubleshooting)

## Introduction

The Amazon Borders FBA Report Generator is a tool designed to help Amazon sellers generate comprehensive reports for their FBA (Fulfillment by Amazon) business. This README file provides step-by-step instructions on how to set up and use the tool.

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
2. Export the following reports:
   - "All listings report"
   - "FBA inventory report"
   - "Restock Inventory report"
   - "Sales Report" for the last 30, 60, 90 days, and 12 months
   - Weekly shipment reports for the last 4 weeks
3. Place these exported files in folders with corresponding names within the application directory.

#### Handling Weekly Shipment Reports

- For weekly shipment reports, use the folders named '1_W', '2_W', '3_W', and '4_W'.
- If multiple shipments occurred in a single week, place all corresponding reports in the same folder.
- If there was a week without shipments, you can leave the corresponding folder empty. In this case, the respective column in the final report will remain empty.
- Note that if you accidentally leave any of the '1_W', '2_W', '3_W', or '4_W' folders empty, the program will not throw an error. Instead, it will simply leave the corresponding column empty in the final report.

### Run the Script

1. Run the `RUN.bat` file.
2. When the report generation is complete, you will see the message: "Program finished, results saved to results/result.csv"

### Import CSV to Google Docs

1. Open Google Docs.
2. Go to Extensions -> Macros.
3. Run the macro named `import_report`.
4. Grant necessary permissions, even if you see warning windows.
5. The macro will access the file through the running server and create a new tab with the report.
6. If an error occurs, delete the newly created table, restart the server, and try again.
7. If it still doesn't work, contact the script creator. You can still manually input data from the file `results/result.csv`.

### Close the Server

1. When the macro execution is complete, press any key in the terminal to close the server.
2. Do not close the terminal using the close button, as it's essential to properly terminate the server execution.

## Folder Cleaning Function

This function is designed to eliminate the need for manual deletion of files in the Amazon exports folder before uploading new files, and to keep historical reports in the Reports history folder.

To run the function:

1. Execute the `CLEAN_FOLDERS.bat` file.

## Configuration File Usage

The script uses a configuration file (`Config.csv`) to manage the names of columns in the exported Amazon files. This ensures the script remains functional even if Amazon changes the names of the export columns.

### How to Use the Configuration File

1. The `Config.csv` file contains the current names of the columns used by the script.
2. Each row in the file corresponds to a specific column name expected in the exported files.

### Handling Errors Related to Column Names

1. If the script encounters an error due to a column name change in the Amazon export files, it will terminate and display an error message indicating the missing column name.
2. To resolve this issue:
   a. Locate the column name mentioned in the error message within the Amazon export file.
   b. Open the `Config.csv` file.
   c. Replace the old column name with the new one from the export file.
   d. Save the changes to `Config.csv` and rerun the script.

## Troubleshooting

If you encounter any issues not covered by this guide, please contact the script creator for further assistance.

## Template Update and SKU Mapping

### Automatic Template Update

The template file is automatically updated each time the script runs, based on the "All listings report". This ensures that the template always reflects the most current listing data.

### SKU Mapping Data

When the script is executed, it downloads the latest SKU mapping information from Google Sheets. This mapping data is crucial for identifying which listings are borders and which are not.

### Border Identification

The script determines whether a listing is a border based on its mapping status. Listings with a mapping are considered borders, while those without are not.

### Potential Unmapped Borders

The script identifies potential unmapped borders using the following criteria:

1. Listings that do not have a mapping for borders
2. Listings that do not have a mapping for the Blue system
3. Listings that either:
   a. Contain the word "border" in the title (case-insensitive), or
   b. Have a price between $17 and $20

These potentially unmapped borders are saved in a separate report for review. To ensure accurate categorization:

1. Check the report located at `results/potential_not_mapped_borders.csv`
2. Review the listings in this report
3. Update the mapping information for these listings in the corresponding Google Sheets document

Keeping the mapping information up-to-date is crucial for accurate report generation.

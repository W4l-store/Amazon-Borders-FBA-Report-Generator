AMAZON BORDERS FBA REPORT GENERATOR

Table of Contents
1. Introduction
2. Initial Setup
   - Install Git
   - Install Python
   - Install ngrok
   - Set Up Python Path
   - Install the Application
3. Generating the Report
   - Export Files from Amazon
   - Run the Script
   - Import CSV to Google Docs
   - Close the Server
4. Configuration File Usage
5. Folder Cleaning Function
6. Troubleshooting

1. INTRODUCTION

The Amazon Borders FBA Report Generator is a tool designed to help Amazon sellers generate comprehensive reports for their FBA (Fulfillment by Amazon) business. This README file provides step-by-step instructions on how to set up and use the tool.

2. INITIAL SETUP

2.1 Install Git

1. Download and install Git from the official Git website: https://git-scm.com/downloads
2. For detailed installation instructions, refer to this Git Installation Guide: https://github.com/git-guides/install-git

2.2 Install Python

1. Download and install Python from the official Python website: https://www.python.org/downloads/
2. For detailed installation instructions, refer to this Python Installation Guide: https://www.geeksforgeeks.org/installation-of-python/

2.3 Install ngrok

1. Install ngrok from the file `Setup/ngrok.exe` provided with this tool.
2. Alternatively, you can download ngrok from the official ngrok website: https://ngrok.com/download

2.4 Set Up Python Path

If you've installed Python but it's not recognized by your system:

1. Restart your computer.
2. If the issue persists, follow these instructions to Add Python to the Windows PATH: https://geek-university.com/add-python-to-the-windows-path/

2.5 Install the Application

1. Ensure you have a folder named "Setup" containing these three files:
   - SETUP.bat
   - clone_project.py
   - .env

2. Run the `SETUP.bat` file. This will clone the project into a new folder in the same directory.

3. You can move the newly created folder to any location for convenience.

4. To update the project in the future, simply run the installation process again.

5. Make sure you have a `.env` file with the following variables:
   NGROK_AUTH_TOKEN= 
   NGROK_DOMAIN=
   GITHUB_REPO_URL=

6. If you don't have the `.env` file, or if any of the variables are missing or incorrect, the application will not work. In this case, contact the developer for assistance.

3. GENERATING THE REPORT

3.1 Export Files from Amazon

1. Log in to your Amazon Seller Central account.
2. Export the following reports:
   - "All listings report"
   - "FBA inventory report"
   - "Restock Inventory report"
   - "Sales Report" for the last 30, 60, 90 days, and 12 months
   - Weekly shipment reports for the last 4 weeks
3. Place these exported files in folders with corresponding names within the application directory.

3.1.1 Handling Weekly Shipment Reports

- For weekly shipment reports, use the folders named '1_W', '2_W', '3_W', and '4_W'.
- If multiple shipments occurred in a single week, place all corresponding reports in the same folder.
- If there was a week without shipments, you can leave the corresponding folder empty. In this case, the respective column in the final report will remain empty.
- Note that if you accidentally leave any of the '1_W', '2_W', '3_W', or '4_W' folders empty, the program will not throw an error. Instead, it will simply leave the corresponding column empty in the final report.

3.2 Run the Script

1. Run the `RUN.bat` file.
2. When the report generation is complete, you will see the message: "Program finished, results saved to results/result.csv"

3.3 Import CSV to Google Docs

1. Open Google Docs.
2. Go to Extensions -> Macros.
3. Run the macro named `import_report`.
4. Grant necessary permissions, even if you see warning windows.
5. The macro will access the file through the running server and create a new tab with the report.
6. If an error occurs, delete the newly created table, restart the server, and try again.
7. If it still doesn't work, contact the script creator. You can still manually input data from the file `results/result.csv`.

3.4 Close the Server

1. When the macro execution is complete, press any key in the terminal to close the server.
2. Do not close the terminal using the close button, as it's essential to properly terminate the server execution.

4. CONFIGURATION FILE USAGE

The script uses a configuration file (`Config.csv`) to manage the names of columns in the exported Amazon files. This ensures the script remains functional even if Amazon changes the names of the export columns.

How to Use the Configuration File:

1. The `Config.csv` file contains the current names of the columns used by the script.
2. Each row in the file corresponds to a specific column name expected in the exported files.

Handling Errors Related to Column Names:

1. If the script encounters an error due to a column name change in the Amazon export files, it will terminate and display an error message indicating the missing column name.
2. To resolve this issue:
   a. Locate the column name mentioned in the error message within the Amazon export file.
   b. Open the `Config.csv` file.
   c. Replace the old column name with the new one from the export file.
   d. Save the changes to `Config.csv` and rerun the script.

5. FOLDER CLEANING FUNCTION

This function is designed to eliminate the need for manual deletion of files in the Amazon exports folder before uploading new files, and to keep historical reports in the Reports history folder.

To run the function:
1. Execute the `CLEAN_FOLDERS.bat` file.

6. TROUBLESHOOTING

If you encounter any issues not covered by this guide, please contact the script creator for further assistance.

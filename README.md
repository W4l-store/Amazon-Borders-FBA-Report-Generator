# README - Amazon Report Generator

## Initial Setup

### Install Python

- Install Python on your computer. The installation file can be found in the `Setup` folder.

### Install ngrok

- Install ngrok from the file `Setup/ngrok.exe`.

### Initialization

- Run the `init.bat` file located in the `Setup` folder. This will install the necessary Python libraries for the script to run and set up the ngrok API key.

### Python Path

- If the library installation fails, it's likely that Python is not added to your system's PATH. Restart your computer. If the issue persists, follow online instructions to add Python to your system's PATH. [Add Python to the Windows PATH](https://geek-university.com/add-python-to-the-windows-path/)

## Generating the Report

### Export Files

- Export the following files from Amazon Seller Central: "All listings report", "FBA inventory report", “Restock Inventory report”, “Sales Report” for the last 30, 60, 90 days, and 12 months. Place these files in the folders with corresponding names.

### Run the Script

- Run the `RUN.bat` file. When the report generation is complete, you will see the message "Program finished, results saved to results/result.csv" and "Press any key to start the server or close the window to stop...".

- If you press any key, the server will start and you will see the message "Server is running. Run macros in Google Docs and after Press any key to stop...".

### Import CSV to Google Docs

- Go to Google Docs Extensions -> Macros -> run the macro `import_csv`. Grant permission despite any warning windows.

- The macro will access the file through the running server and create a new tab with the report. If an error occurs, delete the newly created table, restart the server, and try again.

- If it still doesn't work, contact the script creator. You can still manually input data from the file `results/result.csv`.

### Close the Server

- When the macro execution is complete, press any key in the terminal to close the server.

- Do not close the terminal using the close button, it is essential to properly terminate the server execution.

## Configuration File Usage

The script uses a configuration file (`Config.csv`) to manage the names of columns in the exported Amazon files. This is to ensure the script remains functional even if Amazon changes the names of the export columns.

### How to Use the Configuration File

- The `Config.csv` file contains the current names of the columns used by the script. Each row in the file corresponds to a specific column name expected in the exported files.

### Handling Errors Related to Column Names

- If the script encounters an error due to a column name change in the Amazon export files, it will terminate and display an error message indicating the missing column name.

- To resolve this issue, locate the column name mentioned in the error message within the Amazon export file. Then, open the `Config.csv` file and replace the old column name with the new one from the export file.

- Save the changes to `Config.csv` and rerun the script. This should resolve the error and allow the script to process the export files correctly.

## Troubleshooting

- If you encounter any issues not covered by this guide, please contact the script creator for further assistance.

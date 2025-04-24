// --- Constants ---

// Background colors for different column groups to improve readability.
const COLORS = {
  SHP_BG: "#DAF2F3", // Background for the SHP column.
  WEEKS_BG: "#D9E7FD", // Background for weekly sales columns (1_W, 2_W, 3_W, 4_W).
  INBOUND_BG: "#8DB5F9", // Background for Inbound and Inventory columns.
  DAYS_BG: "#FFE1CC", // Background for short-term sales columns (30, 60, 90 days).
  MONTHS_BG: "#A6E4B7", // Background for long-term FBA sales columns (12m, 2yr).
  MERCHANT_MONTH_BG: "#E8F0FE", // Background for merchant sales columns (M_30, M_12m).
  NEW_COLUMNS_BG: "#FFF2CC", // Background for newly added columns (WMA forecast, Rec Ship).
};

// Colors for conditional formatting rules (currently unused).
const CONDITIONAL_COLORS = {
  WEEKS_LOW: "#FFC7CE", // Intended for low weekly sales.
  INVENTORY_LOW: "#7B9FD7", // Intended for low inventory levels.
  DAYS_LOW: "#FFEB9C", // Intended for low short-term sales.
  MONTHS_LOW: "#C6EFCE", // Intended for low long-term sales.
};

// --- Main Function ---

/**
 * Main function to import CSV data into a Google Sheet.
 * It sets up the sheet, imports data, applies formatting, and finalizes the sheet.
 */
function import_report() {
  // Prepare the spreadsheet and sheet for import.
  const { newDate, sheet } = setupSpreadsheet();

  // Fetch CSV data from the specified URL.
  const csvData = importCsvData();

  // Populate the sheet with CSV data.
  setData(sheet, csvData); // Renamed from setDataAndSort

  // Apply various formatting rules to the sheet.
  applyColumnFormats(sheet);
  applyColumnWidths(sheet);
  applyColorFormatting(sheet);
  applyConditionalFormatting(sheet); // Currently just clears rules.

  // Final adjustments like freezing panes and adding filters.
  finalizeSheet(sheet);
}

// --- Helper Functions ---

/**
 * Sets up the Google Spreadsheet for the import.
 * Calculates the sheet name based on the next day's date.
 * Renames the active spreadsheet and inserts a new sheet with the calculated name.
 * @returns {{newDate: string, sheet: GoogleAppsScript.Spreadsheet.Sheet}} An object containing the sheet name and the sheet object.
 */
function setupSpreadsheet() {
  // Calculate the date for the sheet name (tomorrow's date).
  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);

  // Format the date components (e.g., "Apr_08_24").
  const yy = Utilities.formatDate(tomorrow, "America/New_York", "yy");
  const mm = Utilities.formatDate(tomorrow, "America/New_York", "MMM");
  const dd = Utilities.formatDate(tomorrow, "America/New_York", "dd");
  const newDate = `${mm}_${dd}_${yy}`;

  // Get the active spreadsheet and rename it.
  const activeSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  activeSpreadsheet.rename(`Amazon_BORD_FBA_${newDate}`);

  // Insert a new sheet with the formatted date name.
  const sheet = activeSpreadsheet.insertSheet(newDate);
  return { newDate, sheet };
}

/**
 * Imports CSV data from a specified URL.
 * Includes a header to bypass ngrok browser warnings.
 * @returns {string[][]} A 2D array representing the parsed CSV data.
 */
function importCsvData() {
  // URL of the CSV file to import.
  const csvUrl =
    "https://eminently-noted-rodent.ngrok-free.app/results/result.csv";

  // Options for the URL fetch, including the ngrok bypass header.
  const options = {
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  };

  // Fetch the CSV content as text.
  const csvContent = UrlFetchApp.fetch(csvUrl, options).getContentText();

  // Parse the CSV text into a 2D array.
  return Utilities.parseCsv(csvContent);
}

/**
 * Populates the sheet with the imported CSV data.
 * Data is inserted starting from cell A1.
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet The sheet to populate.
 * @param {string[][]} csvData The 2D array of data to insert.
 */
function setData(sheet, csvData) {
  // Check if there is data to prevent errors with empty CSV.
  if (csvData && csvData.length > 0 && csvData[0].length > 0) {
    // Add the LOCATION column header
    csvData[0].push("LOCATION");

    // Add empty values for LOCATION column in all data rows
    for (let i = 1; i < csvData.length; i++) {
      csvData[i].push("");
    }

    // Set the values in the sheet
    sheet.getRange(1, 1, csvData.length, csvData[0].length).setValues(csvData);
  }
}

/**
 * Applies various formatting rules to the columns, including number formats,
 * alignment, header styles, and borders.
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet The sheet to format.
 */
function applyColumnFormats(sheet) {
  const lrow = sheet.getLastRow();
  // If the sheet is empty or has only a header, skip formatting data rows.
  if (lrow <= 1) return;

  const lastCol = sheet.getLastColumn();

  // Set number formats and right alignment for price columns
  const priceColumns = [6, 7]; // N_Price, Price
  priceColumns.forEach((col) => {
    if (col <= lastCol) {
      const range = sheet.getRange(2, col, lrow - 1, 1);
      range.setNumberFormat("#,##0.00");
      range.setHorizontalAlignment("right");
    }
  });

  // Set number formats and right alignment for integer columns
  const integerColumns = [
    3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
  ];
  integerColumns.forEach((col) => {
    if (col <= lastCol) {
      const range = sheet.getRange(2, col, lrow - 1, 1);
      range.setNumberFormat("#,##0");
      range.setHorizontalAlignment("right");
    }
  });

  // Set text format for Parts_num column to preserve leading zeros
  if (21 <= lastCol) {
    sheet.getRange(2, 21, lrow - 1, 1).setNumberFormat("@");
  }

  // Set header formatting - all headers centered
  const headerRange = sheet.getRange(1, 1, 1, lastCol);
  headerRange
    .setFontWeight("bold")
    .setFontSize(12)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");

  // Set the font color for the SHP header (Column 5) to red
  sheet.getRange(1, 5).setFontColor("#FF0000");

  // Set left alignment for all non-numeric data cells (excluding headers)
  if (lrow > 1) {
    // Text columns (Title, ASIN, Parts_num, FBA_SKU, M_SKU, Status, LOCATION)
    const textColumns = [1, 2, 21, 22, 23, 24, 25];
    textColumns.forEach((col) => {
      if (col <= lastCol) {
        sheet.getRange(2, col, lrow - 1, 1).setHorizontalAlignment("left");
      }
    });
  }

  // Add borders to the entire table
  sheet.getRange(1, 1, lrow, lastCol).setBorder(
    true, // top
    true, // left
    true, // bottom
    true, // right
    true, // vertical
    true, // horizontal
    "black",
    SpreadsheetApp.BorderStyle.SOLID
  );
}

/**
 * Sets specific widths for each column.
 * Column indices and widths are hardcoded based on expected report structure.
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet The sheet to apply column widths to.
 */
function applyColumnWidths(sheet) {
  // Define widths for each column.
  const columnWidths = [
    { col: 1, width: 300 }, // Title
    { col: 2, width: 120 }, // ASIN
    { col: 3, width: 80 }, // WMA forecast
    { col: 4, width: 60 }, // Rec Ship
    { col: 5, width: 60 }, // SHP
    { col: 6, width: 70 }, // N_Price
    { col: 7, width: 70 }, // Price
    { col: 8, width: 40 }, // 1_W
    { col: 9, width: 40 }, // 2_W
    { col: 10, width: 40 }, // 3_W
    { col: 11, width: 40 }, // 4_W
    { col: 12, width: 60 }, // Inbound
    { col: 13, width: 60 }, // Inv
    { col: 14, width: 60 }, // 30
    { col: 15, width: 60 }, // 60
    { col: 16, width: 60 }, // 90
    { col: 17, width: 60 }, // 12m
    { col: 18, width: 60 }, // 2yr
    { col: 19, width: 60 }, // M_30
    { col: 20, width: 60 }, // M_12m
    { col: 21, width: 120 }, // Parts_num
    { col: 22, width: 120 }, // FBA_SKU
    { col: 23, width: 120 }, // M_SKU
    { col: 24, width: 80 }, // Status (will be hidden)
    { col: 25, width: 100 }, // LOCATION (new column)
  ];

  // Apply the defined widths.
  const lastCol = sheet.getMaxColumns();
  columnWidths.forEach((item) => {
    // Ensure the column exists before setting width.
    if (item.col <= lastCol) {
      sheet.setColumnWidth(item.col, item.width);
    }
  });

  // Hide the Status column (24)
  sheet.hideColumn(sheet.getRange("X:X"));
}

/**
 * Applies background colors to specific columns for better visual grouping.
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet The sheet to apply colors to.
 */
function applyColorFormatting(sheet) {
  const lrow = sheet.getLastRow();
  // If the sheet is empty or has only a header, skip coloring data rows.
  if (lrow <= 1) return;

  const lastCol = sheet.getLastColumn();

  // Define column groups and their corresponding background colors.
  const columnColors = [
    { cols: [3, 4], color: COLORS.NEW_COLUMNS_BG }, // WMA forecast, Rec Ship
    { cols: [5], color: COLORS.SHP_BG }, // SHP
    { cols: [8, 9, 10, 11], color: COLORS.WEEKS_BG }, // Weekly columns
    { cols: [12, 13], color: COLORS.INBOUND_BG }, // Inbound and Inventory
    { cols: [14, 15, 16], color: COLORS.DAYS_BG }, // 30/60/90 days
    { cols: [17, 18], color: COLORS.MONTHS_BG }, // 12m/2yr FBA sales
    { cols: [19, 20], color: COLORS.MERCHANT_MONTH_BG }, // Merchant sales
  ];

  // Apply the background colors to headers and data cells.
  columnColors.forEach((item) => {
    item.cols.forEach((col) => {
      // Ensure the column exists before coloring.
      if (col <= lastCol) {
        // Color the header cell.
        sheet.getRange(1, col, 1, 1).setBackground(item.color);
        // Color the data cells in the column.
        sheet.getRange(2, col, lrow - 1, 1).setBackground(item.color);
      }
    });
  });
}

/**
 * Clears any existing conditional formatting rules from the sheet.
 * Currently, no new rules are applied.
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet The sheet to clear rules from.
 */
function applyConditionalFormatting(sheet) {
  // Clear all existing conditional format rules.
  sheet.clearConditionalFormatRules();
  // Note: Conditional formatting rules were previously defined here.
}

/**
 * Finalizes the sheet setup after data import and formatting.
 * Freezes the header row and the first column, adds filters,
 * prevents text wrapping in the title column, and moves the sheet
 * to the first position.
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet The sheet to finalize.
 */
function finalizeSheet(sheet) {
  // Freeze only the top row (headers).
  sheet.setFrozenRows(1);

  // Add filter controls to the entire data range.
  // Check if there is data beyond the header row before creating filter.
  if (sheet.getLastRow() > 1) {
    sheet.getDataRange().createFilter();
  }

  // Prevent text wrapping in the first column (Title).
  if (sheet.getMaxColumns() >= 1) {
    sheet.getRange(1, 1, sheet.getLastRow(), 1).setWrap(false);
  }

  // Move this sheet to be the first tab in the spreadsheet.
  SpreadsheetApp.getActiveSpreadsheet().moveActiveSheet(1); // Use 1 for the first position.

  // Apply all pending changes.
  SpreadsheetApp.flush();
}

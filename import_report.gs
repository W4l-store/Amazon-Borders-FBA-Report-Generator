// Constants
const COLORS = {
  SHP_BG: "#DAF2F3",
  WEEKS_BG: "#D9E7FD",
  INBOUND_BG: "#8DB5F9",
  DAYS_BG: "#FFE1CC",
  MONTHS_BG: "#A6E4B7",
  MERCHANT_MONTH_BG: "#E8F0FE", // Подобранный цвет для merchant inventory в той же гамме
};

const CONDITIONAL_COLORS = {
  WEEKS_LOW: "#FFC7CE", // Розовый для низких значений недельных продаж
  INVENTORY_LOW: "#7B9FD7", // Чуть более темный оттенок INBOUND_BG (#8DB5F9)
  DAYS_LOW: "#FFEB9C", // Желтый для низких значений дней
  MONTHS_LOW: "#C6EFCE", // Зеленый для низких значений месяцев
};

function import_report() {
  // Setup date and spreadsheet
  const { newDate, sheet } = setupSpreadsheet();

  // Import and set data
  const csvData = importCsvData();
  setDataAndSort(sheet, csvData);

  // Apply formatting
  applyColumnFormats(sheet);
  applyColumnWidths(sheet);
  applyColorFormatting(sheet);
  applyConditionalFormatting(sheet);

  // Final setup
  finalizeSheet(sheet);
}

function setupSpreadsheet() {
  const testDate = new Date();
  const secondDate = new Date();
  secondDate.setDate(testDate.getDate() + 1);

  const yy = Utilities.formatDate(secondDate, "America/New_York", "yy");
  const mm = Utilities.formatDate(secondDate, "America/New_York", "MMM");
  const dd = Utilities.formatDate(secondDate, "America/New_York", "dd");
  const newDate = mm + "_" + dd + "_" + yy;

  const activeSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  activeSpreadsheet.rename("Amazon_BORD_FBA_" + newDate);

  const sheet = activeSpreadsheet.insertSheet(newDate);
  return { newDate, sheet };
}

function importCsvData() {
  const csvUrl =
    "https://eminently-noted-rodent.ngrok-free.app/results/result.csv";
  const options = {
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  };
  const csvContent = UrlFetchApp.fetch(csvUrl, options).getContentText();
  return Utilities.parseCsv(csvContent);
}

function setDataAndSort(sheet, csvData) {
  // Set data
  sheet.getRange(1, 1, csvData.length, csvData[0].length).setValues(csvData);

  // Sort by 90 days column if there's data
  if (csvData.length > 1) {
    const range = sheet.getRange(2, 1, csvData.length - 1, csvData[0].length);
    range.sort({ column: 15, ascending: false });
  }

  // Add sequential numbers
  const lrow = sheet.getLastRow();
  const idValues = Array.from({ length: lrow - 1 }, (_, i) => [i + 1]);
  sheet.getRange(2, 1, idValues.length, 1).setValues(idValues);
}

function applyColumnFormats(sheet) {
  const lrow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();

  // Set number formats
  // Price columns with 2 decimal places
  const priceColumns = [4, 5, 6];
  priceColumns.forEach((col) => {
    sheet.getRange(2, col, lrow - 1, 1).setNumberFormat("#,##0.00");
  });

  // Other numeric columns without decimals
  const integerColumns = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
  integerColumns.forEach((col) => {
    sheet.getRange(2, col, lrow - 1, 1).setNumberFormat("#,##0");
  });

  // Center align columns
  const centerColumns = [1, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
  centerColumns.forEach((col) => {
    sheet.getRange(1, col, lrow, 1).setHorizontalAlignment("center");
  });

  // Set header formatting
  const headerRange = sheet.getRange(1, 1, 1, lastCol);
  headerRange
    .setFontWeight("bold")
    .setFontSize(12)
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");

  // Set SHP header color
  sheet.getRange(1, 4).setFontColor("#FF0000");

  // Add borders to the entire table
  sheet
    .getRange(1, 1, lrow, lastCol)
    .setBorder(
      true,
      true,
      true,
      true,
      true,
      true,
      "black",
      SpreadsheetApp.BorderStyle.SOLID
    );
}

function applyColumnWidths(sheet) {
  const columnWidths = [
    { col: 1, width: 40 }, // id
    { col: 2, width: 300 }, // Title
    { col: 3, width: 120 }, // ASIN
    { col: 4, width: 60 }, // SHP
    { col: 5, width: 70 }, // N_Price
    { col: 6, width: 70 }, // Price
    { col: 7, width: 40 }, // 1_W
    { col: 8, width: 40 }, // 2_W
    { col: 9, width: 40 }, // 3_W
    { col: 10, width: 40 }, // 4_W
    { col: 11, width: 60 }, // Inbound
    { col: 12, width: 60 }, // Inv
    { col: 13, width: 60 }, // 30
    { col: 14, width: 60 }, // 60
    { col: 15, width: 60 }, // 90
    { col: 16, width: 60 }, // 12m
    { col: 17, width: 60 }, // 2yr
    { col: 18, width: 60 }, // M_30
    { col: 19, width: 60 }, // M_12m
    { col: 20, width: 120 }, // Parts__Num
    { col: 21, width: 120 }, // FBA_SKU
    { col: 22, width: 120 }, // M_SKU
    { col: 23, width: 80 }, // Status
  ];

  columnWidths.forEach((item) => sheet.setColumnWidth(item.col, item.width));
}

function applyColorFormatting(sheet) {
  const lrow = sheet.getLastRow();

  // Apply background colors to columns with matching headers
  const columnColors = [
    { cols: [4], color: COLORS.SHP_BG }, // SHP
    { cols: [7, 8, 9, 10], color: COLORS.WEEKS_BG }, // Weekly columns
    { cols: [11, 12], color: COLORS.INBOUND_BG }, // Inbound and Inventory
    { cols: [13, 14, 15], color: COLORS.DAYS_BG }, // 30/60/90 days
    { cols: [16, 17], color: COLORS.MONTHS_BG }, // 12m/2yr
    { cols: [18, 19], color: COLORS.MERCHANT_MONTH_BG }, // Merchant months
  ];

  columnColors.forEach((item) => {
    item.cols.forEach((col) => {
      // Color the header
      sheet.getRange(1, col, 1, 1).setBackground(item.color);
      // Color the data cells
      sheet.getRange(2, col, lrow - 1, 1).setBackground(item.color);
    });
  });
}

function applyConditionalFormatting(sheet) {
  const lrow = sheet.getLastRow();
  sheet.clearConditionalFormatRules();

  const rules = [];

  // Inventory conditional formatting only
  const invRange = sheet.getRange(2, 12, lrow - 1, 1);
  rules.push(
    SpreadsheetApp.newConditionalFormatRule()
      .whenNumberLessThan(1)
      .setBackground(CONDITIONAL_COLORS.INVENTORY_LOW)
      .setRanges([invRange])
      .build()
  );

  sheet.setConditionalFormatRules(rules);
}

function finalizeSheet(sheet) {
  // Freeze rows and columns
  sheet.setFrozenRows(1);
  sheet.setFrozenColumns(1);

  // Add filters
  sheet.getDataRange().createFilter();

  // Ensure title column doesn't wrap
  sheet.getRange(1, 2, sheet.getLastRow(), 1).setWrap(false);

  // Move to first position and flush changes
  SpreadsheetApp.getActiveSpreadsheet().moveActiveSheet(0);
  SpreadsheetApp.flush();
}

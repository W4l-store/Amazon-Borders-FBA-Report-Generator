function import_report() {
  var testDate = new Date();
  var secondDate = new Date();
  secondDate.setDate(testDate.getDate() + 1);

  var yy = Utilities.formatDate(secondDate, "America/New_York", "yy");
  var mm = Utilities.formatDate(secondDate, "America/New_York", "MMM");
  var dd = Utilities.formatDate(secondDate, "America/New_York", "dd");
  var newDate = mm + "_" + dd + "_" + yy;

  var activeSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  activeSpreadsheet.rename("Amazon_BORD_FBA_" + newDate);

  var sheet = activeSpreadsheet.insertSheet(newDate);
  var sheet2 = activeSpreadsheet.getSheetByName("format");
  var source = sheet2.getDataRange();

  var csvUrl =
    "https://eminently-noted-rodent.ngrok-free.app/results/result.csv";
  var options = {
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  };
  var csvContent = UrlFetchApp.fetch(csvUrl, options).getContentText();
  var csvData = Utilities.parseCsv(csvContent);

  // Set data in one operation
  sheet.getRange(1, 1, csvData.length, csvData[0].length).setValues(csvData);

  // Apply formats only to the filled range
  var dataRange = sheet.getDataRange();
  source.copyTo(dataRange, { formatOnly: true });

  // Sort data
  if (csvData.length > 1) {
    // Check if there's data to sort
    var range = sheet.getRange(2, 1, csvData.length - 1, csvData[0].length);
    range.sort({ column: 15, ascending: false });
  }

  // Add sequential numbers
  var lrow = sheet.getLastRow();
  var idValues = [];
  for (var i = 1; i <= lrow - 1; i++) {
    idValues.push([i]);
  }
  sheet.getRange(2, 1, idValues.length, 1).setValues(idValues);

  // Set column widths in one operation
  var columnWidths = [
    { col: 1, width: 60 }, // id
    { col: 2, width: 72 }, // title
    { col: 3, width: 100 }, // asin
    { col: 4, width: 60 }, // shp
    { col: 5, width: 90 }, // n_price
    { col: 6, width: 70 }, // price
    { col: 7, width: 40 }, // 1_w
    { col: 8, width: 40 }, // 2_w
    { col: 9, width: 40 }, // 3_w
    { col: 10, width: 40 }, // 4_w
    { col: 11, width: 100 }, // inbound
    { col: 12, width: 70 }, // inv
    { col: 13, width: 70 }, // 30
    { col: 14, width: 70 }, // 60
    { col: 15, width: 70 }, // 90
    { col: 16, width: 70 }, // 12m
    { col: 17, width: 5 }, // 2000-2025
    { col: 18, width: 120 }, // parts__num
    { col: 19, width: 120 }, // sku
  ];
  columnWidths.forEach(function (item) {
    sheet.setColumnWidth(item.col, item.width);
  });
  sheet.setColumnWidths(7, 9, 40);

  // Move sheet to the first position
  activeSpreadsheet.moveActiveSheet(0);

  // Freeze the top row
  sheet.setFrozenRows(1);

  // Apply changes
  SpreadsheetApp.flush();
}

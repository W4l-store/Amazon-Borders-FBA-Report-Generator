function test_Macro_eug4() {
  var spreadsheet = SpreadsheetApp.getActive();
  spreadsheet.getActiveSheet().setColumnWidth(1, 55);

  spreadsheet.getRange("A2").activate();
  spreadsheet.getCurrentCell().setValue("1");
  spreadsheet.getRange("A3").activate();
  spreadsheet.getCurrentCell().setFormula("=A2+1");

  var lrow = spreadsheet.getLastRow();
  spreadsheet.getRange("A3:A" + lrow).activate();
  spreadsheet
    .getRange("A3")
    .copyTo(
      spreadsheet.getActiveRange(),
      SpreadsheetApp.CopyPasteType.PASTE_NORMAL,
      false
    );
}

function test_Macro_eug5() {
  var spreadsheet = SpreadsheetApp.getActive();

  var lrow = spreadsheet.getLastRow();

  //spreadsheet.getRange('A2:A'+lrow).activate();
  spreadsheet
    .getRange("A2:A" + lrow)
    .copyTo(
      spreadsheet.getActiveRange(),
      SpreadsheetApp.CopyPasteType.PASTE_VALUES,
      false
    );
}

function test_Macro_eug6() {
  var spreadsheet = SpreadsheetApp.getActive();
  spreadsheet.getRange("A2").activate();
  var currentCell = spreadsheet.getCurrentCell();
  spreadsheet
    .getSelection()
    .getNextDataRange(SpreadsheetApp.Direction.DOWN)
    .activate();
  currentCell.activateAsCurrentCell();
  spreadsheet
    .getRange("A2:A2643")
    .copyTo(
      spreadsheet.getActiveRange(),
      SpreadsheetApp.CopyPasteType.PASTE_VALUES,
      false
    );
}

function _112233() {
  var spreadsheet = SpreadsheetApp.getActive();
  spreadsheet.getRange("A2").activate();
}

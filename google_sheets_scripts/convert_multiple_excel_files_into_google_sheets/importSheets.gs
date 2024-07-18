function importSheetsFromConvertedFilesInBatches() {
  var folderId = '10WO8xdmnLMJSJFiaCS9fm1453n_tyZyH'; // Replace with the ID of the folder containing your converted Google Sheets files
  var folder = DriveApp.getFolderById(folderId);
  var files = folder.getFiles();
  var properties = PropertiesService.getScriptProperties();
  var lastProcessedIndex = parseInt(properties.getProperty('importLastProcessedIndex')) || 0;
  var batchSize = 30; // Adjust the batch size based on the execution limit

  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  Logger.log('Active Spreadsheet: ' + spreadsheet.getName());

  Logger.log('Starting from index: ' + lastProcessedIndex);

  var index = 0;

  while (files.hasNext()) {
    var file = files.next();
    if (index >= lastProcessedIndex) {
      if (file.getMimeType() === MimeType.GOOGLE_SHEETS) {
        Logger.log('Processing file number: ' +lastProcessedIndex+' File name: '+ file.getName());
        var tempSpreadsheet = SpreadsheetApp.openById(file.getId());
        var sheets = tempSpreadsheet.getSheets();

        sheets.forEach(function(sheet) {
          Logger.log('Copying sheet: ' + sheet.getName());
          var newSheet = sheet.copyTo(spreadsheet).setName(file.getName() + " - " + sheet.getName());
          Logger.log('New Sheet: ' + newSheet.getName());
        });

        lastProcessedIndex = index + 1;
        properties.setProperty('importLastProcessedIndex', lastProcessedIndex);
      } else {
        Logger.log('Skipping file (not a Google Sheets file): ' + file.getName());
        lastProcessedIndex = index + 1;
        properties.setProperty('importLastProcessedIndex', lastProcessedIndex);
      }

      // Decrease batchSize and stop if it reaches 0
      batchSize--;
      if (batchSize <= 0) {
        Logger.log('Batch completed. Stopping execution.');
        return;
      }
    }

    index++;
  }

  Logger.log('All files processed.');
  properties.deleteProperty('importLastProcessedIndex'); // Reset the index after all files are processed
}

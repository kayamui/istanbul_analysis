function convertXlsToGoogleSheetsInBatches() {
  var folderId = '1br1HkdDJyXAtOTyTVYZxY_8VMLeHegKL'; // Replace with the ID of the folder containing your Excel files
  var folder = DriveApp.getFolderById(folderId);
  var files = folder.getFiles();
  var properties = PropertiesService.getScriptProperties();
  var lastProcessedIndex = parseInt(properties.getProperty('lastProcessedIndex')) || 0;
  var batchSize = 30; // Adjust the batch size based on the execution limit

  // Create a new folder for converted files
  var convertedFolderName = 'Converted'; // You can change this name
  var convertedFolder;
  
  // Check if the folder already exists, otherwise create it
  var existingFolders = folder.getFoldersByName(convertedFolderName);
  if (existingFolders.hasNext()) {
    convertedFolder = existingFolders.next();
  } else {
    convertedFolder = folder.createFolder(convertedFolderName);
  }

  Logger.log('Starting from index: ' + lastProcessedIndex);

  var index = 0;

  while (files.hasNext()) {
    var file = files.next();
    if (index >= lastProcessedIndex) {
      if (file.getMimeType() === MimeType.MICROSOFT_EXCEL || file.getMimeType() === MimeType.MICROSOFT_EXCEL_LEGACY) {
        Logger.log('Converting file: '+ lastProcessedIndex+ ' File Name: ' + file.getName());
        var blob = file.getBlob();

        // Create a temporary file in Drive
        var tempFile = DriveApp.createFile(blob).setName(file.getName());

        // Convert the temporary file to Google Sheets format in the new folder
        var resource = {
          title: file.getName(),
          mimeType: MimeType.GOOGLE_SHEETS
        };
        var convertedFile = Drive.Files.copy(resource, tempFile.getId(), {convert: true});
        
        // Move the converted file to the new folder
        var googleSheetFile = DriveApp.getFileById(convertedFile.id);
        googleSheetFile.moveTo(convertedFolder);

        // Move the original temporary file to trash
        tempFile.setTrashed(true);

        lastProcessedIndex = index + 1;
        properties.setProperty('lastProcessedIndex', lastProcessedIndex);
      } else {
        Logger.log('Skipping file (not an Excel file): ' + file.getName());
        lastProcessedIndex = index + 1;
        properties.setProperty('lastProcessedIndex', lastProcessedIndex);
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
  properties.deleteProperty('lastProcessedIndex'); // Reset the index after all files are processed
}

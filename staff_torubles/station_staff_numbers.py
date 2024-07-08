def station_staff_numbers():

  import pandas as pd
  import numpy as np
  import xlsxwriter

  excel_path= str(input('Enter the path of the Excel File: '))
  excel_file= pd.ExcelFile(excel_path)

  #read the dataframe
  dataframes= {}
  for sheet_name in excel_file.sheet_names:
    dataframes[sheet_name]= excel_file.parse(sheet_name)

  #reshape the columns
  for i in dataframes:
    dataframes[i].columns= dataframes[i].iloc[0]
    dataframes[i]= dataframes[i][1:]
    dataframes[i]= dataframes[i].reset_index(drop= True)

  #fill the null values
  for i in dataframes:
    dataframes[i]= dataframes[i].fillna(0)

  #leave only the first 240 rows
  for sheet_name in dataframes:
    dataframes[sheet_name] = dataframes[sheet_name].iloc[0:240]

  #Enter the Data
  for sheet_name in dataframes:
    sheet= dataframes[sheet_name]
    sheet['EKSİK DR']= sheet['FİİLİ MEVCUT DR'].astype(int) - sheet['ÖZLÜK-DR PDC'].astype(int)
    sheet['EKSİK AABT']= sheet['FİİLİ MEVCUT AABT'].astype(int) - sheet['ÖZLÜK-AABT PDC'].astype(int)
    sheet['EKSİK ATT']= sheet['FİİLİ MEVCUT ATT'].astype(int) - sheet['ÖZLÜK-ATT PDC'].astype(int)
    sheet['EKSİK SRC']= sheet['FİİLİ MEVCUT SRC/24'].astype(int) + sheet['FİİLİ MEVCUT SRC/12-36'].astype(int) - sheet['ÖZLÜK-SRC PDC'].astype(int)

  #write the file

  # Create a Pandas Excel writer using XlsxWriter as the engine.
  writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

  # Write each dataframe to a separate sheet in the Excel file.
  for sheet_name, dataframe in dataframes.items():
      dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

  # Save the Excel file by closing the writer.
  writer.close() # Use .close()
  print("Muhammed'den Sevgilerle :* ")

station_staff_numbers()
  
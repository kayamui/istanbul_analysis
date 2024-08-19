# -*- coding: utf-8 -*-
"""inspections.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TYPi27QZx3_-gYezQ30ZOHppwmXZumGE
"""

import pandas as pd
import numpy as np

excel_file= pd.ExcelFile('departments/inspection/inspection1.xlsx')

dataframes= {sheet_name:excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}

dataframes.keys()

import pandas as pd
import numpy as np

import openpyxl

def inspections():

  concatenated_df = pd.DataFrame(columns= ['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTANAK TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR','KONU BASLIGI', 'YAPILAN ISLEM'])

  excel_path= str(input('Lütfen Excel Dosyanın Konumunu Giriniz: '))
  excel_file= pd.ExcelFile(excel_path)
  dataframes= {sheet_name.lower():excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}

  print(dataframes.keys())
  sheet_path= str(input('Lütfen Analiz Etmek İstediğiniz Ayı Yazınız, Tüm Veri Analizi İçin x Tuşuna Basınız: '))
  sheet_path= sheet_path.lower()

  if sheet_path == 'x':
    for i in dataframes.keys():
      df_temp = dataframes[i]
      df_temp.columns= df_temp.iloc[0]
      df_temp.drop(df_temp.index[0], inplace= True)
      df_temp.columns= ['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTANAK TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR','KONU BASLIGI', 'YAPILAN ISLEM']
      df_temp['SAYI']= 1
      concatenated_df= pd.concat([concatenated_df, df_temp])
      concatenated_df['HAKKINDA TUTANAK TUTULAN KISI'] = concatenated_df['HAKKINDA TUTANAK TUTULAN KISI'].str.split('-')
      df_exploded = concatenated_df.explode('HAKKINDA TUTANAK TUTULAN KISI').reset_index(drop=True)
      df_exploded['HAKKINDA TUTANAK TUTULAN KISI']= df_exploded['HAKKINDA TUTANAK TUTULAN KISI'].apply(lambda x: x.strip())

      df_exploded.groupby(['HAKKINDA TUTANAK TUTULAN KISI', 'KONU BASLIGI']).agg({'SAYI':'sum'}).sort_values(by= 'SAYI', ascending= False).reset_index().to_excel('inceleme_tum_aylar.xlsx')
      df_exploded.groupby('KONU BASLIGI').agg({'VALUE':'sum'}).sort_values(by= 'VALUE', ascending=False).to_excel('inceleme_tum_aylar_konu_basligi.xlsx')

  else:
    try:
      df_temp = dataframes[sheet_path]
      df_temp.columns= df_temp.iloc[0]
      df_temp.drop(df_temp.index[0], inplace= True)
      df_temp.columns= ['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTANAK TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR','KONU BASLIGI', 'YAPILAN ISLEM']
      df_temp['SAYI']= 1
      concatenated_df= pd.concat([concatenated_df, df_temp])
      concatenated_df['HAKKINDA TUTANAK TUTULAN KISI'] = concatenated_df['HAKKINDA TUTANAK TUTULAN KISI'].str.split('-')
      df_exploded = concatenated_df.explode('HAKKINDA TUTANAK TUTULAN KISI').reset_index(drop=True)
      df_exploded['HAKKINDA TUTANAK TUTULAN KISI']= df_exploded['HAKKINDA TUTANAK TUTULAN KISI'].apply(lambda x: x.strip())

      df_exploded.groupby(['HAKKINDA TUTANAK TUTULAN KISI', 'KONU BASLIGI']).agg({'SAYI':'sum'}).sort_values(by= 'SAYI', ascending= False).reset_index().to_excel(f'inceleme_{sheet_path}.xlsx')
      df_exploded.groupby('KONU BASLIGI').agg({'VALUE':'sum'}).sort_values(by= 'VALUE', ascending=False).to_excel(f'inceleme_{sheet_path}_konu_basligi.xlsx')

    except:
      print('Lütfen Geçerli Bir Ay Giriniz!')
      return inspections()

sheet_path in dataframes.keys()

df_exploded

df= dataframes['Sayfa1']

df_temp = df.copy()

df_temp.columns= df_temp.iloc[0]

df_temp.drop(df_temp.index[0], inplace= True)

df_temp

for i in df_temp.columns:
  print(i + ',')

df_temp.columns= ['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTANAK TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR','KONU BASLIGI', 'YAPILAN ISLEM']

df_temp['VALUE']= 1

df_temp

df_grouped= df_temp.groupby(['HAKKINDA TUTANAK TUTULAN KISI', 'KONU BASLIGI']).agg({'VALUE':'sum'}).sort_values('VALUE', ascending= False).reset_index()

df_grouped

# prompt: split df_grouped['HAKKINDA TUTANAK TUTULAN KISI'] and add each value in a same row with the same KONU BASLIGI and VALUE

df_grouped['HAKKINDA TUTANAK TUTULAN KISI'] = df_grouped['HAKKINDA TUTANAK TUTULAN KISI'].str.split('-')
df_exploded = df_grouped.explode('HAKKINDA TUTANAK TUTULAN KISI').reset_index(drop=True)
df_exploded

df_exploded['HAKKINDA TUTANAK TUTULAN KISI']= df_exploded['HAKKINDA TUTANAK TUTULAN KISI'].apply(lambda x: x.strip())

df_exploded.groupby(['HAKKINDA TUTANAK TUTULAN KISI', 'KONU BASLIGI']).agg({'VALUE':'sum'}).sort_values('VALUE', ascending= False).to_excel('Inceleme.xlsx')

df_exploded.groupby('KONU BASLIGI').agg({'VALUE':'sum'}).sort_values(by= 'VALUE', ascending=False)


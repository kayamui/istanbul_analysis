# -*- coding: utf-8 -*-
"""Hourly Case Counts.ipynb
"""

import pandas as pd
import numpy as np
from datetime import datetime # Import the datetime module
import plotly.express as px
import plotly.graph_objects as go

current_datetime= datetime.now() # Call the now function from the datetime module


def read_file():

    # Asks user for choose excel file, it might a single or multiple ones
    file_path= str(input('Please enter the file path: '))
    excel_file= pd.ExcelFile(file_path)

    # The program parses the sheet pages and creates new dataframe dictionaries
    file_df = {sheet_name: excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}

    #Asks user to choose the proper page
    print(file_df.keys())
    page= str(input('Please select the proper page: '))
    
    return file_df[page]

dataframe= read_file()

df= dataframe


%run find_district.py

df= find_district(df)

rural= {
    'SARIYER':'Bahçeköy, Demirciköy, Garipçe, Gümüşdere, Kısırkaya, Kumköy, Rumelifeneri, Uskumru, Zekeriye',
    'ARNAVUTKÖY':'Baklalı, Balaban, Boyalık, Çilingir, Dursunköy, Hacımaşlı, Karaburun, Sazlıbosna, Tayakadın, Yassıören, Yeniköy, Yeşilbayır',
    'ÇATALCA':'Atatürk, Akalan, Aydınlar, Bahşayiş, Başak, Belgrat, Celepköy, Çakıl, Çanakça, Çiftlikköy, Dağyenice, Elbasan, Fatih, Gökçeali, Gümüşpınar, Hallaçlı, Hisarbeyli, İhsaniye (Merkez ve Pınarca Mevkii), İnceğiz, İzzettin, Kabakça, Kalfa, Karacaköy Merkez, Karamandere, Kestanelik, Kızılcaali, Muratbey Merkez (Merkez ve Mezra), Nakkaş, Oklalı, Ormanlı, Ovayenice, Örcünlü, Örencik, Subaşı, Yalıköy, Yaylacık, Yazlık',
    'SİLİVRİ':'Akören, Alipaşa, Bekirli, Beyciler, Büyükçavuşlu, Büyükkılıçlı, Büyüksinekli, Çayırdere, Çeltik, Danamandıra, Fener, Gazitepe, Kadıköy, Kurfallı, Küçükkılıçlı, Küçüksinekli, Sayalar, Seymen, Yolçatı',
    'BEYKOZ':'Akbaba, Alibahadır, Anadolufeneri, Bozhane, Cumhuriyet, Dereseki, Elmalı, Göllü, Görele, İshaklı, Kaynarca, Kılıçlı, Mahmutşevketpaşa , Öğümce, Örnekköy, Paşamandıra, Polonezköy,  Poyrazköy, Riva, Zerzevatçı',
    'ŞİLE':'Şile: Ağaçdere, Ahmetli, Akçakese, Alacalı, Avcıkoru, Bıçkıdere, Bozgoca, Bucaklı, Çataklı, Çayırbaşı, Çelebi, Çengilli, Darlık, Değirmençayırı, Doğancalı, Erenler, Esenceli, Geredeli, Göçe, Gökmaşlı, Göksu, Hacılı, Hasanlı, İmrendere, İmrenli, İsaköy, Kabakoz, Kadıköy, Kalem, Karabeyli, Karacaköy, Karakiraz, Karamandere, Kervansaray, Kızılca, Korucu, Kömürlük, Kurfallı, Kurna, Meşrutiyet, Oruçoğlu, Osmanköy, Ovacık, Sahilköy, Satmazlı, Sofular, Soğullu, Sortullu, Şuayipli, Teke, Ulupelit, Üvezli, Yaka, Yaylalı,Yazımanayır, Yeniköy, Yeşilvadi'
    }

rural_new = dict()
for key, value in rural.items():
  value= ','.join(value.replace('i','İ').replace('ı','I').replace('ö','Ö').replace('ü','Ü').replace('ş','Ş').replace('ç','Ç').replace('ğ','Ğ').upper().split(','))
  rural_new[key]= value

def find_rural(row, keyword):
  if row['İLÇE_ARGE'] in keyword.keys():
    if row['MAHALLE_ARGE'] in keyword[row['İLÇE_ARGE']]:
      return 'KIRSAL'
    else:
      return 'KENTSEL'
  else:
    return 'KENTSEL'

df['URBAN-RURAL'] = df.apply(find_rural, keyword= rural_new, axis=1)

df['VAKA VERILIS TARIH SAAT']= df['VAKA VERILIS\nTARIHI'] + ' ' + df['VAKA VERILIS\nSAATI']

#df['VAKA CIKIS TARIH SAAT'] = df['VAKAYA CIKIS TARIHI'] + ' '+ df['VAKAYA CIKIS SAATI']
#df['OLAY YER VARIS TARIH SAAT']= df['OLAY YERI VARIS TARIHI'] + ' ' + df['OLAY YERI VARIS SAATI']

def to_datetime(row):
  try:
    return pd.to_datetime(row, format= '%d-%m-%Y %H:%M:%S')
  except:
    try:
      return pd.to_datetime(row, format= '%Y-%m-%d %H:%M:%S')
    except:
      return '-'
    

df['VAKA VERILIS TARIH SAAT'] = df['VAKA VERILIS TARIH SAAT'].apply(to_datetime)

df['VAKA CIKIS TARIH SAAT'] = df['VAKA CIKIS TARIH SAAT'].apply(to_datetime)
#df['OLAY YER VARIS TARIH SAAT'] = df['OLAY YER VARIS TARIH SAAT'].apply(to_datetime)

df['hour']= df['VAKA VERILIS TARIH SAAT'].dt.strftime('%H')

temp_df= df.copy()

temp_df= temp_df[temp_df['İLÇE_ARGE']!='BELİRTİLMEMİŞ']

temp_df['Gün'] = temp_df['VAKA VERILIS TARIH SAAT'].dt.day_name(locale= 'tr_TR')
temp_df['Ay']= temp_df['VAKA VERILIS TARIH SAAT'].dt.month

temp_df['Gün']= temp_df['Gün'].str.replace('ý','I').str.replace('þ','Ş')

temp_df['Gün']= temp_df['Gün'].str.replace('i','İ').str.replace('ı','I').str.replace('ö','Ö').str.replace('ü','Ü').str.replace('ş','Ş').str.replace('ç','Ç').str.replace('ğ','Ğ').str.upper()


temp_df['ulasim_suresi']= (temp_df['OLAY YER VARIS TARIH SAAT'] - temp_df['VAKA CIKIS TARIH SAAT']).dt.seconds
temp_df['ulasim_suresi']= temp_df['ulasim_suresi'].astype('float32')

day_of_week= ['PAZARTESİ', 'SALI', 'ÇARŞAMBA', 'PERŞEMBE', 'CUMA', 'CUMARTESİ', 'PAZAR']
temp_df['Gün'] = pd.Categorical(temp_df['Gün'], categories=day_of_week, ordered=True)


#temp_df['gecikme']= temp_df.apply(lambda x: 1 if (((x['URBAN-RURAL'] == 'KENTSEL') and (x['ulasim_suresi'] > 600)) or ((x['URBAN-RURAL']=='KIRSAL') and x['ulasim_suresi'] > 1800)) else 0, axis=1)
#temp_df.groupby(['İLÇE_ARGE','MAHALLE_ARGE','Saat Aralığı']).agg({'Value':'sum'}).drop(index='BELİRTİLMEMİŞ').reset_index().to_excel('saatlik_vaka_sayisi.xlsx')
#temp_df[(temp_df['ulasim_suresi']>1800) & (temp_df['URBAN-RURAL']=='KIRSAL')]

temp_df['Value']= 1

temp_df['Value']= temp_df['Value'].astype(int)

temp_df.rename(columns={'ulasim_suresi':'reach_time'}, inplace=True)

unnormal_lates_path= str(input('Please choose unnormal late path: '))

temp_df[(temp_df['reach_time']>=3600)].to_excel(unnormal_lates_path+f'hourly_district_reach_times/unnormal_late_{current_datetime}.xlsx')

temp_df[temp_df['OLAY YER VARIS TARIH SAAT'] < temp_df["VAKA CIKIS TARIH SAAT"]].to_excel(f'wrong_time_inputs_{current_datetime}.xlsx')

temp_df= temp_df[((temp_df['reach_time']<=3600) & (temp_df['OLAY YER VARIS TARIH SAAT'] > temp_df["VAKA CIKIS TARIH SAAT"]))]

temp_df['hour']= temp_df['hour'].astype(int)

hour_df= temp_df[(temp_df['hour'] >= 10) & (temp_df['hour']<22)]

backup_df= temp_df.copy()


district_locations= pd.read_excel('C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/locations/district_locations.xlsx')

district_locations['Latitude']= district_locations['Latitude'].astype('float32')
district_locations['Longitude']= district_locations['Longitude'].astype('float32')

district_locations

temp_df= pd.merge(temp_df, district_locations, on=['İLÇE_ARGE', 'MAHALLE_ARGE'], how='inner')

temp_df['MAHALLE_ARGE']= temp_df['MAHALLE_ARGE'].str.strip()
temp_df['İLÇE_ARGE']= temp_df['İLÇE_ARGE'].str.strip()
temp_df['Ay']= temp_df['Ay'].astype(int)
temp_df['Gün']= temp_df['Gün'].str.strip()
temp_df['hour']= temp_df['hour'].astype(int)

#temp_df.head(50).to_excel('test.xlsx')

def location_set(row):
  if row['VAKANIN ENLEMI']=='-':
    row['VAKANIN ENLEMI']= row['Latitude']
    row['VAKANIN BOYLAMI']= row['Longitude']
  return row

temp_df = temp_df.apply(location_set, axis=1)

temp_df['VAKANIN ENLEMI']= temp_df['VAKANIN ENLEMI'].astype('float32')
temp_df['VAKANIN BOYLAMI']= temp_df['VAKANIN BOYLAMI'].astype('float32')
temp_df[temp_df['VAKANIN ENLEMI'] != '-']


hour_df= temp_df[['KKM PROTOKOL','EKIP NO','Ay','Gün','hour','VAKANIN ENLEMI','VAKANIN BOYLAMI','Latitude','Longitude']]

hour_df.drop_duplicates(inplace=True)

try:
    main_df= pd.concat([main_df,hour_df])
except:
  main_df= pd.DataFrame()
  main_df= pd.concat([main_df,hour_df])


def filter_cases(df):

  selected_df= pd.DataFrame()

  print(df['Ay'].unique())
  month= int(input('Enter a month, for all data select 0: '))

  if month==0:
    selected_df= df.copy()

  elif month not in df['Ay'].unique():
    print('Month not found')
    return filter_cases(df)

  else:
    selected_df= df[df['Ay']==month]

  print(selected_df['Gün'].unique())
  day= str(input('Enter a day: '))

  if day not in selected_df['Gün'].unique():
    print('Day not found')
    return filter_cases(df)

  else:
    selected_df= selected_df[selected_df['Gün']==day]
    return selected_df

selected_df= filter_cases(main_df)



def location_set(row):
  if row['VAKANIN ENLEMI']=='-':
    row['VAKANIN ENLEMI']= row['Latitude']
    row['VAKANIN BOYLAMI']= row['Longitude']
  return row

selected_df = selected_df.apply(location_set, axis=1)


def visualize_map(selected_df):
  radius=int()
  # Filter the necessary columns for the heatmap
  df_map = selected_df
  lat_center = df_map['Latitude'].mean()
  lon_center = df_map['Longitude'].mean()
  if len(df_map)>15000:
    radius= 10
  else:
    radius= 20

  # Create a heatmap using Plotly with Mapbox (blue to yellow to red gradient)
  fig = px.density_mapbox(df_map, lat='VAKANIN ENLEMI', lon='VAKANIN BOYLAMI',
                          radius=radius,  # Adjusted for smoothness
                          center=dict(lat= lat_center,lon= lon_center),  # Center of Istanbul
                          zoom=10,
                          mapbox_style="open-street-map",
                          opacity=0.7,  # Transparency for better visual effect
                          color_continuous_scale=["blue", "yellow", "red"],
                          animation_frame='hour')

  #path= str(input('Please select '))

  # Show the plot
  fig.write_html(f'{current_datetime}_mapbox_graph.html')


visualize_map(selected_df)

# -*- coding: utf-8 -*-
"""Hourly Case Counts.ipynb

Automatically generated by Colab.

"""

import pandas as pd
import numpy as np



excel_jan= pd.ExcelFile(path+'2024/monthly/'+'1-OCAK 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')
excel_feb= pd.ExcelFile(path+'2024/monthly/'+'2-ŞUBAT 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')
excel_mar= pd.ExcelFile(path+'2024/monthly/'+'3-MART 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')
excel_apr= pd.ExcelFile(path+'2024/monthly/'+'4-NİSAN 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')
excel_may= pd.ExcelFile(path+'2024/monthly/'+'5-MAYIS 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')
excel_jun= pd.ExcelFile(path+'2024/monthly/'+'6-HAZİRAN 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')

excel_jul= pd.ExcelFile(path+'2024/monthly/'+'7-TEMMUZ 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')

df3= {sheet_name:excel_jan.parse(sheet_name) for sheet_name in excel_jan.sheet_names}
df4= {sheet_name:excel_feb.parse(sheet_name) for sheet_name in excel_feb.sheet_names}
df5= {sheet_name:excel_mar.parse(sheet_name) for sheet_name in excel_mar.sheet_names}
df6= {sheet_name:excel_apr.parse(sheet_name) for sheet_name in excel_apr.sheet_names}
df7= {sheet_name:excel_may.parse(sheet_name) for sheet_name in excel_may.sheet_names}
df8= {sheet_name:excel_jun.parse(sheet_name) for sheet_name in excel_jun.sheet_names}

df9= {sheet_name:excel_jul.parse(sheet_name) for sheet_name in excel_jul.sheet_names}

df9.keys()

df3['54230']['MONTH'] = 1
df4['48247']['MONTH'] = 2
df5['49926']['MONTH'] = 3
df6['NİSAN - 50.014']['MONTH'] = 4
df7['52340']['MONTH'] = 5
df8['52852-DEFTER']['MONTH'] = 6
df9['55923 defter avrupa']['MONTH'] = 7

df= pd.concat([df3['54230'],df4['48247'], df5['49926'],df6['NİSAN - 50.014'], df7['52340'], df8['52852-DEFTER'], df9['55923 defter avrupa']])

# Commented out IPython magic to ensure Python compatibility.
# %run find_district.py

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

df['URBAN-RURAL'] = df.apply(find_rural, keyword= rural_new, axis=1)

df['VAKA VERILIS TARIH SAAT']= df['VAKA VERILIS\nTARIHI'] + ' ' + df['VAKA VERILIS\nSAATI']
df['VAKA CIKIS TARIH SAAT'] = df['VAKAYA CIKIS TARIHI'] + ' '+ df['VAKAYA CIKIS SAATI']
df['OLAY YER VARIS TARIH SAAT']= df['OLAY YERI VARIS TARIHI'] + ' ' + df['OLAY YERI VARIS SAATI']

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
df['OLAY YER VARIS TARIH SAAT'] = df['OLAY YER VARIS TARIH SAAT'].apply(to_datetime)

df

df['Saat Aralığı']= df['VAKA VERILIS TARIH SAAT'].dt.strftime('%H')

temp_df= df.copy()

temp_df= temp_df[temp_df['İLÇE_ARGE']!='BELİRTİLMEMİŞ']

temp_df['Gün'] = temp_df['VAKA VERILIS TARIH SAAT'].dt.day_name(locale= 'tr_TR')

temp_df

temp_df['Gün']= temp_df['Gün'].str.replace('ý','I').str.replace('þ','Ş')

temp_df['Gün']= temp_df['Gün'].str.replace('i','İ').str.replace('ı','I').str.replace('ö','Ö').str.replace('ü','Ü').str.replace('ş','Ş').str.replace('ç','Ç').str.replace('ğ','Ğ').str.upper()

day_of_week= list(temp_df['Gün'].unique())

#temp_df['Gün'] = pd.Categorical(temp_df['Gün'], categories=day_of_week, ordered=True)

temp_df['Gün'].unique()

temp_df['Saat Aralığı'].unique()

temp_df

#temp_df.groupby(['İLÇE_ARGE','MAHALLE_ARGE','Saat Aralığı']).agg({'Value':'sum'}).drop(index='BELİRTİLMEMİŞ').reset_index().to_excel('saatlik_vaka_sayisi.xlsx')

temp_df['Ay']= temp_df['VAKA VERILIS TARIH SAAT'].dt.month



temp_df

temp_df['Value']= 1

temp_df['Value']= temp_df['Value'].astype(int)

hour_pivot= temp_df.pivot_table(index=['İLÇE_ARGE','MAHALLE_ARGE','Saat Aralığı'], columns=['Ay','Gün'], values='Value', aggfunc='sum')

hour_pivot

#sort hour_pivot Gün by day_of_week

hour_pivot = hour_pivot.reindex(columns=day_of_week, level='Gün')

hour_pivot= hour_pivot.reindex(columns=day_of_week, level='Gün').reset_index().fillna(0)

hour_pivot.to_excel('saatlik_vaka_sayisi.xlsx')

hour_pivot

station_locations= pd.read_excel('C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/locations/station_locations.xlsx')

station_locations['latitude']= station_locations['KOORDİNAT'].apply(lambda x: x.split(',')[0])
station_locations['longitude']= station_locations['KOORDİNAT'].apply(lambda x: x.split(',')[1])
station_locations.drop(columns=['KOORDİNAT'], inplace=True)

station_locations.rename(columns={'Ekip Adı':'EKIP NO'}, inplace=True)

temp_df= pd.merge(temp_df, station_locations, on='EKIP NO', how='inner')

hourly_team_cases= temp_df.pivot_table(index= ['EKIP NO','Saat Aralığı'], columns=['Ay','Gün'], values='Value', aggfunc='sum').fillna(0)

day_of_week

hourly_team_cases

hourly_team_cases= hourly_team_cases.reindex(columns=day_of_week, level='Gün').reset_index().fillna(0)

hourly_team_cases

hourly_team_cases.to_excel('ekip_bazli_saatlik_vaka.xlsx')

temp_df.rename(columns={'EKIP NO':'team'})

hourly_team_cases

# prompt: create a column of temp_df named hourly_case and check hourly team cases, add the value of the hourly_team_cases where equal to temp_df on EKIP NO , Gün, Ay, Saat Aralığı

temp_df['hourly_case'] = 0
for index, row in temp_df.iterrows():
  team = row['EKIP NO']
  gun = row['Gün']
  ay = row['Ay']
  saat = row['Saat Aralığı']
  hourly_case = hourly_team_cases[(hourly_team_cases['EKIP NO'] == team) & (hourly_team_cases['Gün'] == gun) & (hourly_team_cases['Ay'] == ay) & (hourly_team_cases['Saat Aralığı'] == saat)].iloc[0, 4:].sum()
  temp_df.at[index, 'hourly_case'] = hourly_case

import pandas as pd
from geopy.distance import great_circle

# Sample dataset
data = {
    'team': ['A', 'B', 'C', 'D'],
    'latitude': [41.015137, 41.025137, 41.035137, 41.045137],
    'longitude': [28.979530, 28.989530, 28.999530, 29.009530],
    'hourly_cases': [1.5, 0.8, 0.6, 1.3]
}

df = pd.DataFrame(data)

# Thresholds
case_threshold = 1.2

# Function to calculate the distance between two points
def calculate_distance(lat1, lon1, lat2, lon2):
    return great_circle((lat1, lon1), (lat2, lon2)).kilometers

# Identify teams with case load under the threshold
underloaded_teams = df[df['hourly_cases'] < case_threshold]

# Function to find the closest team for overloaded teams
def find_closest_team(overloaded_team):
    overloaded_lat = overloaded_team['latitude']
    overloaded_lon = overloaded_team['longitude']

    # Calculate distance to all underloaded teams
    underloaded_teams['distance'] = underloaded_teams.apply(
        lambda row: calculate_distance(overloaded_lat, overloaded_lon, row['latitude'], row['longitude']), axis=1)

    # Find the closest team
    closest_team = underloaded_teams.loc[underloaded_teams['distance'].idxmin()]
    return closest_team

# Iterate over teams with a case load over the threshold
for index, overloaded_team in df[df['hourly_cases'] > case_threshold].iterrows():
    closest_team = find_closest_team(overloaded_team)
    print(f"Team {overloaded_team['team']} is overloaded. The closest team is {closest_team['team']} with {closest_team['hourly_cases']} cases.")



#set colors of fig for False = Red , for True= Blue and by 'Ay'
dff = temp_df.copy()
fig = px.scatter_mapbox(dff, lat="ENLEM", lon="BOYLAM", color="Gecikme", size="Aylık Vaka Sayısı",hover_data=['Ortalama Vaka Süresi'],hover_name='Mahalle Adı',
                  color_discrete_map={'Yok':'blue','Var':'red'}, size_max=15, zoom=10, animation_frame='Ay',
                  mapbox_style="carto-positron")
fig.write_html("C:/Users/mkaya/Onedrive/Masaüstü/urban_total_delay_map.html")

data_pivot.drop(columns=['ATAŞEHİR', 'BELİRTİLMEMİŞ', 'BEYKOZ', 'KADIKÖY','KARTAL','TUZLA','ÇEKMEKÖY','ÜMRANİYE','ÜSKÜDAR','ŞİLE'], inplace=True)

import plotly.express as px
import pandas as pd

# Pivot the DataFrame to create a matrix where:
#  - index is 'Saat Aralığı'
#  - columns are 'İLÇE_ARGE'
#  - values are 'Toplam Vaka Sayısı'
data_pivot = hourly_counts.pivot(index='İLÇE_ARGE', columns='Saat Aralığı', values='Toplam Vaka Sayısı')
data_pivot.drop(index=['ATAŞEHİR', 'BELİRTİLMEMİŞ', 'BEYKOZ', 'KADIKÖY','KARTAL','TUZLA','ÇEKMEKÖY','ÜMRANİYE','ÜSKÜDAR','ŞİLE'], inplace=True)

fig = px.imshow(data_pivot,
                labels=dict(x="Saat Aralığı", y="İLÇE_ARGE", color="Toplam Vaka Sayısı"),
                color_continuous_scale='hot'
               )
fig.update_xaxes(side="top")
fig.write_html("C:/Users/mkaya/Onedrive/Masaüstü/saatlik_vaka_sayisi.html")

hourly_counts = temp_df.groupby(['İLÇE_ARGE', 'MAHALLE_ARGE','Saat Aralığı']).agg({'Saat Aralığı':'count'})
hourly_counts.rename(columns={'Saat Aralığı':'Toplam Vaka Sayısı'}, inplace=True)
hourly_counts.reset_index(inplace=True)

hourly_counts

lat_lons= pd.read_excel('C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/district locations/lat_lon.xlsx')

lat_lons.drop(columns=['Unnamed: 0'], inplace=True)

lat_lons

hourly_counts.columns= ['İlçe Adı','Mahalle Adı', 'Saat Aralığı','Toplam Vaka Sayısı']

hourly_neighbourhoods= pd.merge(hourly_counts, lat_lons, on=['İlçe Adı','Mahalle Adı'], how='inner')

hourly_neighbourhoods

dff = hourly_neighbourhoods
fig = px.scatter_mapbox(dff, lat="Latitude", lon="Longitude", color="İlçe Adı", size="Toplam Vaka Sayısı",hover_data=['Toplam Vaka Sayısı'],hover_name='Mahalle Adı',size_max=15, zoom=10, animation_frame='Saat Aralığı',
                  mapbox_style="carto-positron")
fig.write_html("C:/Users/mkaya/Onedrive/Masaüstü/saatlik_vaka3.html")

temp_df['VAKANIN ENLEMI']

temp_df['MONTH']

import pandas as pd
dff = temp_df

import plotly.express as px
fig = px.density_mapbox(dff, lat='VAKANIN ENLEMI', lon='VAKANIN BOYLAMI', z='Value', radius=10,
                        center=dict(lat=0, lon=180), zoom=0,animation_frame='MONTH',
                        mapbox_style="open-street-map")
fig.write_html('vaka_sicaklik_haritasi.html')

temp_df[]

temp_df.rename(columns={'VAKANIN ENLEMI':'latitude', 'VAKANIN BOYLAMI':'longitude'}, inplace=True)

len(temp_df)

temp_df= temp_df[temp_df['latitude']!='-']
temp_df= temp_df[temp_df['longitude']!='-']



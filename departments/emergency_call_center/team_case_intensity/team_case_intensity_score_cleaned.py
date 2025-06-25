import pandas as pd
import numpy as np

import datetime as dt

import os

import geopandas as gpd
from shapely.geometry import Point

from sklearn.preprocessing import MinMaxScaler
scaler= MinMaxScaler()

import json

istanbul_population_density= pd.read_csv(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\istanbul_population_density.csv")
icd_scores= pd.read_csv(r"C:\Users\mkaya\OneDrive\Belgeler\GitHub\istanbul_analysis\ipynb_workouts\icd10_diagnoses_scored.csv")
team_codes= pd.read_csv(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\keywords\team_code_match\eu_team_code.csv")
df_population_density = pd.read_csv(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\istanbul_population_density.csv")


dataframes_2018_2019= {}
dataframes_2020_2021= {}
dataframes_2022_2023= {}
dataframes_2024_2025= {}


case_files_2018_2019= os.listdir(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2018_2019\\")
case_files_2020_2021= os.listdir(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2020_2021\\")
case_files_2022_2023= os.listdir(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2022_2023\\")
case_files_2024_2025= os.listdir(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2024_2025\\")


case_files_2018_2019= [file for file in case_files_2018_2019 if file.endswith(".parquet")]
case_files_2020_2021= [file for file in case_files_2020_2021 if file.endswith(".parquet")]
case_files_2022_2023= [file for file in case_files_2022_2023 if file.endswith(".parquet")]
case_files_2024_2025= [file for file in case_files_2024_2025 if file.endswith(".parquet")]

# Read the parquet files into dataframes
# Using a loop to read each file and store it in the respective dictionary
for file in case_files_2018_2019:
  dataframes_2018_2019[file.replace(".parquet", "")]= pd.read_parquet(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2018_2019\\" + file)
  print(file, ' has been read')
for file in case_files_2020_2021:
  dataframes_2020_2021[file.replace(".parquet", "")]= pd.read_parquet(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2020_2021\\" + file)
  print(file, ' has been read')
for file in case_files_2022_2023:
  dataframes_2022_2023[file.replace(".parquet", "")]= pd.read_parquet(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2022_2023\\" + file)
  print(file, ' has been read')
for file in case_files_2024_2025:
  dataframes_2024_2025[file.replace(".parquet", "")]= pd.read_parquet(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\2024_2025\\" + file)
  print(file, ' has been read')
  
def rename_columns(df):
    for key in df.keys():
        for col in df[key].columns:
            if col=="ICD10 TANI \nADI":
                df[key].rename(columns={'ICD10 TANI \nADI':'ICD10 TANI\nADI'}, inplace=True)
            if col=="ICD10 TANI \nADI":
                df[key].rename(columns={'ICD10 TANI \nADI':'ICD10 TANI\nADI'}, inplace=True)
            if col=='Vaka Veriliş':
                df[key].rename(columns={'Vaka Veriliş':'Vaka Veriliş Tarih Saat'}, inplace=True)
            if col == 'Ulaşım Sn':
                df[key].rename(columns={'Ulaşım Sn':'Ulaşım Sn\n(Olay Yeri Varış Tarihi - Çağrı Tarihi)'}, inplace=True)
            if col == 'İhbar Tarihi':
                df[key].rename(columns={'İhbar Tarihi':'İhbar/Çağrı Tarih Saat'}, inplace=True)
            if col == 'Olay Yeri Varış':
                df[key].rename(columns={'Olay Yeri Varış':'Olay Yeri Varış Tarih Saat'}, inplace=True)
            if col == 'Olay Yeri Ayrılış':
                df[key].rename(columns={'Olay Yeri Ayrılış':'Olay Yeri Ayrılış Tarih Saat'}, inplace=True)
            if col == 'Hastaneye Varış':
                df[key].rename(columns={'Hastaneye Varış':'Hastaneye Varış Tarih Saat'}, inplace=True)
            if col == 'Hastaneden Ayrılış':
                df[key].rename(columns={'Hastaneden Ayrılış':'Hastaneden Ayrılış Tarih Saat'}, inplace=True)
            if col == 'İstasyona Dönüş':
                df[key].rename(columns={'İstasyona Dönüş':'İstasyona Dönüş Tarih Saat'}, inplace=True)
            
    return df
dataframes_2018_2019 = rename_columns(dataframes_2018_2019)
dataframes_2020_2021 = rename_columns(dataframes_2020_2021)
dataframes_2022_2023 = rename_columns(dataframes_2022_2023)
dataframes_2024_2025 = rename_columns(dataframes_2024_2025)

necessary_columns= ['KKM Protokol','Ekip No', 'İhbar/Çağrı Tarih Saat', 'Cinsiyet', 'Yeni Doğan', 'Yaş', 'Adli Vaka', 'Çağrı Nedeni', 'Sonuç', 'Nakledilen Hastane', 'ICD10 TANI\nADI', 'Triaj', 'Bilinç', 'Nabız', 'Vaka Veriliş Tarih Saat', 'Olay Yeri Varış Tarih Saat', 'Olay Yeri Ayrılış Tarih Saat', 'Hastaneye Varış Tarih Saat', 'Hastaneden Ayrılış Tarih Saat', 'Müdahale Süresi Sn', 'Hastane Teslim Süresi Sn', 'Çıkış KM', 'Varış KM', 'Hastaneye Varış KM', 'Dönüş KM', 'Vakanın Enlemi', 'Vakanın Boylamı', 'Tansiyon', 'Glukoz', 'Ateş', 'SPO2', 'Solunum Değeri', 'Nabız Değeri']
columns_to_process= ['İhbar/Çağrı Tarih Saat','Vaka Veriliş Tarih Saat', 'Olay Yeri Varış Tarih Saat','Olay Yeri Ayrılış Tarih Saat','Hastaneye Varış Tarih Saat','Hastaneden Ayrılış Tarih Saat']

all_datas= [dataframes_2018_2019,dataframes_2020_2021, dataframes_2022_2023, dataframes_2024_2025]

for dataframe in all_datas:
  for key in dataframe.keys():
    print(f"Processing {key}")

    # Rename column if necessary
    if "Hastaneye Varış Saati\n" in dataframe[key].columns:
      dataframe[key].rename(columns={"Hastaneye Varış Saati\n": "Hastaneye Varış Saati"}, inplace=True)

    # Process 'İhbar/Çağrı Tarih Saat' or create it if needed
    if "İhbar/Çağrı Tarih Saat" not in dataframe[key].columns:
      print(f"Creating İhbar/Çağrı Tarih Saat for {key}")
      # First, apply the parse_date function to the original date column
      if 'İhbar/Çağrı Tarihi' in dataframe[key].columns and 'İhbar/Çağrı  Saati' in dataframe[key].columns:

        # Convert time column to string, handling potential non-string types
        dataframe[key]['İhbar/Çağrı  Saati'] = dataframe[key]['İhbar/Çağrı  Saati']
        # Combine date and time columns, coercing errors
        dataframe[key]["İhbar/Çağrı Tarih Saat"] = pd.to_datetime(
            dataframe[key]['İhbar/Çağrı Tarihi']+ ' ' + dataframe[key]['İhbar/Çağrı  Saati'],
            format='mixed'
        )
      else:
          print(f"Warning: 'İhbar/Çağrı Tarihi' or 'İhbar/Çağrı  Saati' not found in {key}. Cannot create 'İhbar/Çağrı Tarih Saat'.")
    else:
        # If 'İhbar/Çağrı Tarih Saat' already exists, ensure it's in datetime format
        print(f"Converting İhbar/Çağrı Tarih Saat to datetime for {key}")
        dataframe[key]['İhbar/Çağrı Tarih Saat'] = pd.to_datetime(dataframe[key]['İhbar/Çağrı Tarih Saat'], format= 'mixed')


    # Process 'Vaka Veriliş Tarih Saat'
    if "Vaka Veriliş Tarih Saat" not in dataframe[key].columns:
      print(f"Creating Vaka Veriliş Tarih Saat for {key}")
      if 'Vaka Veriliş\nTarihi' in dataframe[key].columns and 'Vaka Veriliş\nSaati' in dataframe[key].columns:
        dataframe[key]['Vaka Veriliş\nSaati'] = dataframe[key]['Vaka Veriliş\nSaati']
        dataframe[key]["Vaka Veriliş Tarih Saat"] = pd.to_datetime(
            dataframe[key]['Vaka Veriliş\nTarihi'] + ' ' + dataframe[key]['Vaka Veriliş\nSaati'],
            format='mixed'
        )
      else:
           print(f"Warning: 'Vaka Veriliş\\nTarihi' or 'Vaka Veriliş\\nSaati' not found in {key}. Cannot create 'Vaka Veriliş Tarih Saat'.")
    else:
        print(f"Converting Vaka Veriliş Tarih Saat to datetime for {key}")
        dataframe[key]['Vaka Veriliş Tarih Saat'] = pd.to_datetime(dataframe[key]['Vaka Veriliş Tarih Saat'], format= 'mixed')


    # Process 'Olay Yeri Varış Tarih Saat'
    if "Olay Yeri Varış Tarih Saat" not in dataframe[key].columns:
      print(f"Creating Olay Yeri Varış Tarih Saat for {key}")
      if 'Olay Yeri Varış Tarihi' in dataframe[key].columns and 'Olay Yeri Varış Saati' in dataframe[key].columns:
        dataframe[key]['Olay Yeri Varış Saati'] = dataframe[key]['Olay Yeri Varış Saati']
        dataframe[key]["Olay Yeri Varış Tarih Saat"] = pd.to_datetime(
            dataframe[key]['Olay Yeri Varış Tarihi'] + ' ' + dataframe[key]['Olay Yeri Varış Saati'],
            format='mixed'
        )
      else:
          print(f"Warning: 'Olay Yeri Varış Tarihi' or 'Olay Yeri Varış Saati' not found in {key}. Cannot create 'Olay Yeri Varış Tarih Saat'.")
    else:
        print(f"Converting Olay Yeri Varış Tarih Saat to datetime for {key}")
        dataframe[key]['Olay Yeri Varış Tarih Saat'] = pd.to_datetime(dataframe[key]['Olay Yeri Varış Tarih Saat'], format='mixed')

    # Process 'Olay Yeri Ayrılış Tarih Saat'
    if 'Olay Yeri Ayrılış Tarih Saat' not in dataframe[key].columns:
      print(f"Creating Olay Yeri Ayrılış Tarih Saat for {key}")
      if 'Olay Yeri Ayrılış Tarihi' in dataframe[key].columns and 'Olay Yeri Ayrılış Saati' in dataframe[key].columns:
        dataframe[key]['Olay Yeri Ayrılış Saati'] = dataframe[key]['Olay Yeri Ayrılış Saati']
        dataframe[key]["Olay Yeri Ayrılış Tarih Saat"] = pd.to_datetime(
            dataframe[key]['Olay Yeri Ayrılış Tarihi'] + ' ' + dataframe[key]['Olay Yeri Ayrılış Saati'],
            format='mixed'
        )
      else:
          print(f"Warning: 'Olay Yeri Ayrılış Tarihi' or 'Olay Yeri Ayrılış Saati' not found in {key}. Cannot create 'Olay Yeri Ayrılış Tarih Saat'.")
    else:
        print(f"Converting Olay Yeri Ayrılış Tarih Saat to datetime for {key}")
        dataframe[key]['Olay Yeri Ayrılış Tarih Saat'] = pd.to_datetime(dataframe[key]['Olay Yeri Ayrılış Tarih Saat'], format= 'mixed')

    # Process 'Hastaneye Varış Tarih Saat'
    # Note the inconsistent column name 'Hastaneye varış Tarih Saat' found in the traceback
    if 'Hastaneye Varış Tarih Saat' not in dataframe[key].columns and 'Hastaneye varış Tarih Saat' in dataframe[key].columns:
         dataframe[key].rename(columns={'Hastaneye varış Tarih Saat':'Hastaneye Varış Tarih Saat'}, inplace=True)

    if 'Hastaneye Varış Tarih Saat' not in dataframe[key].columns:
      print(f"Creating Hastaneye Varış Tarih Saat for {key}")
      if 'Hastaneye Varış Tarihi' in dataframe[key].columns and 'Hastaneye Varış Saati' in dataframe[key].columns:
        dataframe[key]['Hastaneye Varış Saati'] = dataframe[key]['Hastaneye Varış Saati']
        dataframe[key]["Hastaneye Varış Tarih Saat"] = pd.to_datetime(
            dataframe[key]['Hastaneye Varış Tarihi'] + ' ' + dataframe[key]['Hastaneye Varış Saati'],
            format='mixed'
        )
      else:
          print(f"Warning: 'Hastaneye Varış Tarihi' or 'Hastaneye Varış Saati' not found in {key}. Cannot create 'Hastaneye Varış Tarih Saat'.")
    else:
        print(f"Converting Hastaneye Varış Tarih Saat to datetime for {key}")
        dataframe[key]['Hastaneye Varış Tarih Saat'] = pd.to_datetime(dataframe[key]['Hastaneye Varış Tarih Saat'], format='mixed')

    # Process 'Hastaneden Ayrılış Tarih Saat'
    if 'Hastaneden Ayrılış Tarih Saat' not in dataframe[key].columns:
      print(f"Creating Hastaneden Ayrılış Tarih Saat for {key}")
      if 'Hastaneden Ayrılış Tarihi' in dataframe[key].columns and 'Hastaneden Ayrılış Saati' in dataframe[key].columns:
        dataframe[key]['Hastaneden Ayrılış Saati'] = dataframe[key]['Hastaneden Ayrılış Saati']
        dataframe[key]["Hastaneden Ayrılış Tarih Saat"] = pd.to_datetime(
            dataframe[key]['Hastaneden Ayrılış Tarihi'] + ' ' + dataframe[key]['Hastaneden Ayrılış Saati'],
            format='mixed'
        )
      else:
          print(f"Warning: 'Hastaneden Ayrılış Tarihi' or 'Hastaneden Ayrılış Saati' not found in {key}. Cannot create 'Hastaneden Ayrılış Tarih Saat'.")
    else:
        print(f"Converting Hastaneden Ayrılış Tarih Saat to datetime for {key}")
        dataframe[key]['Hastaneden Ayrılış Tarih Saat'] = pd.to_datetime(dataframe[key]['Hastaneden Ayrılış Tarih Saat'], format='mixed')
        

for dataframes in all_datas:
  for dataframe in dataframes.keys():
    dataframes[dataframe].rename(columns={'Varış Km':'Varış KM', 'Hastaneye Varış Km':'Hastaneye Varış KM'}, inplace=True)
    
for dataframes in all_datas:
  for dataframe in dataframes.keys():
    #print(dataframe)
    #print([col for col in necessary_columns if col not in dataframes[dataframe].columns], "\n")
    columns_to_add= [col for col in necessary_columns if col not in dataframes[dataframe].columns]
    for col in columns_to_add:
      dataframes[dataframe][col]= pd.NA
      
df= pd.DataFrame()

for dataframes in all_datas:
  for dataframe in dataframes.keys():
    df= pd.concat([df, dataframes[dataframe][necessary_columns]])



def print_lonLat_columns(df):
    """Prints columns containing the substring 'enlem' (case-insensitive)."""

    for col in df.columns:
        if ('enlem' in col.lower()) | ('boylam' in col.lower()) | (col.lower() == 'lat') | (col.lower() == 'lon'):
            print(col)


def get_district_neighbourhood(df):
  # Load districts
  with open("C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/locations/istanbul-districts.json", "r", encoding="utf-8") as f:
      districts_data = json.load(f)
      districts_gdf = gpd.GeoDataFrame.from_features(districts_data["features"])
  print_lonLat_columns(df)
  lat = "Vakanın Enlemi" if "Vakanın Enlemi" in df.columns else str(input('latitude column: '))
  lon = "Vakanın Boylamı" if "Vakanın Boylamı" in df.columns else str(input('longitude column: '))
  
  columns= [col for col in df.columns] + ['Neighbourhood', 'District']
  # Load neighborhoods
  neighbourhoods_gdf = gpd.read_file("C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/locations/istanbul_neighbourhoods.geojson")

  # Convert latitude and longitude columns to numeric, coercing errors to NaN
  df[lat] = pd.to_numeric(df[lat], errors='coerce')
  df[lon] = pd.to_numeric(df[lon], errors='coerce')
  df_cleaned = df
  # Convert Vakanın Enlemi and Vakanın Boylamı to geometry points
  df_cleaned["geometry"] = df_cleaned.apply(lambda row: Point(row[lon], row[lat]), axis=1)
  points_gdf = gpd.GeoDataFrame(df_cleaned, geometry="geometry", crs="EPSG:4326")

  # Spatial join to find districts
  points_gdf = gpd.sjoin(points_gdf, districts_gdf, how="left", predicate="within")
  points_gdf.rename(columns={"name": "District"}, inplace=True)

  # Drop 'index_right' before the second spatial join
  if 'index_right' in points_gdf.columns:
      points_gdf = points_gdf.drop(columns=['index_right'])

  # Spatial join to find neighborhoods
  points_gdf = gpd.sjoin(points_gdf, neighbourhoods_gdf, how="left", predicate="within")
  points_gdf.rename(columns={"name": "Neighbourhood"}, inplace=True)

  # Select relevant columns and return
  return points_gdf[columns]

df= get_district_neighbourhood(df)

istanbul_population_density['Ilce']= istanbul_population_density['Ilce'].str.strip()
istanbul_population_density= istanbul_population_density[['Ilce', 'Nüfus']]
istanbul_population_density.rename(columns={'Nüfus':'District Population Density', 'Ilce':'District'}, inplace=True)

df['District']= df['District'].str.strip()

istanbul_population_density_dict= istanbul_population_density.set_index('District').to_dict()['District Population Density']
df['District Population Density']= df['District'].map(istanbul_population_density_dict)

df['case_response_time'] = round((pd.to_datetime(df['Olay Yeri Varış Tarih Saat']) - pd.to_datetime(df['İhbar/Çağrı Tarih Saat'])).dt.total_seconds(), 2)  # Convert to seconds
df.fillna({'Çıkış KM': np.nan}, inplace=True)
df.fillna({'Varış KM':np.nan}, inplace=True)

df['total_distance'] = df["Dönüş KM"].astype(float) - df['Çıkış KM'].astype(float)
df['field_operation_time'] = round((pd.to_datetime(df['Olay Yeri Ayrılış Tarih Saat']) - pd.to_datetime(df['İhbar/Çağrı Tarih Saat'])).dt.total_seconds(), 2)  # Convert to seconds
df['hospital_delivery_time'] = round((pd.to_datetime(df['Hastaneye Varış Tarih Saat']) - pd.to_datetime(df['Olay Yeri Ayrılış Tarih Saat'])).dt.total_seconds(), 2)  # Convert to seconds


df['Yaş']= df['Yaş'].str.replace('-', '')

df['Ateş']= df['Ateş'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
df['Yaş']= df['Yaş'].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else np.nan)
df['Nabız Değeri']= df['Nabız Değeri'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
df['Glukoz']= df['Glukoz'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
df['SPO2']= df['SPO2'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
df['Solunum Değeri']= df['Solunum Değeri'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)

df.loc[(df['total_distance']>1000) | (df['total_distance']<0), 'total_distance']= np.nan
df.loc[(df['case_response_time']>43200) | (df['case_response_time']<0), 'case_response_time']= np.nan
df.loc[(df['field_operation_time']>86400) | (df['field_operation_time']<0), 'field_operation_time']= np.nan
df.loc[(df['hospital_delivery_time']>86400) | (df['hospital_delivery_time']<0), 'hospital_delivery_time']= np.nan
df.loc[(df['Ateş'] > 50) | (df['Ateş'] < 0), 'Ateş'] = np.nan
df.loc[(df['Yaş'] > 120) | (df['Yaş'] < 0), 'Yaş'] = np.nan
df.loc[(df['Nabız Değeri'] > 300) | (df['Nabız Değeri'] < 0), 'Nabız Değeri'] = np.nan
df.loc[(df['Glukoz'] > 1000) | (df['Glukoz'] < 0), 'Glukoz'] = np.nan
df.loc[(df['SPO2'] > 100) | (df['SPO2'] < 0), 'SPO2'] = np.nan
df.loc[(df['Solunum Değeri'] > 100) | (df['Solunum Değeri'] < 0), 'Solunum Değeri'] = np.nan
df.fillna({'Ateş':np.nan}, inplace=True)
df.fillna({'Yaş':np.nan}, inplace=True)  
df.fillna({'Nabız Değeri': np.nan}, inplace=True)
df.fillna({'Glukoz':np.nan}, inplace=True)
df.fillna({'SPO2':np.nan}, inplace=True)
df.fillna({'Solunum Değeri':np.nan}, inplace=True)
icd_scores['ICD10 TANI']= icd_scores['ICD10 TANI'].str.strip()
icd_scores_dict= icd_scores.set_index('ICD10 TANI').to_dict()['Expanded Score']


# Scoring functions
df['icd_score'] = df['ICD10 TANI\nADI'].map(icd_scores_dict)

def age_score(age):
    try:
        age = int(age)
        return age
    except:
        return 32.7

def cagri_score(val):
    high_impact = ["Terör", "Trafik Kazası", "Yaralama", "Beyaz Kod Sağlık Personeline Şiddet"]
    med_impact = ["Medikal", "Diğer Kazalar", "İntihar"]
    if val in high_impact:
        return 100
    elif val in med_impact:
        return 75
    else:
        return 25

def sonuc_score(val):
    high_impact = [
        "Nakil - Hastaneye", "Ex - Yerinde Bırakıldı", "Nakil - Eve",
        "Nakil - Tıbbi Tetkik İçin", "Nakil - Hastaneler Arası", "Ex - Morga Nakil"
    ]
    med_impact = ["Diğer", "Olay Yerinde Bekleme", "Yerinde Müdahale", "Nakil - Diğer"]
    if val in high_impact:
        return 100
    elif val in med_impact:
        return 75
    else:
        return 10

def tansiyon_score(val):
    try:
        s, d = map(int, str(val).split("/"))
        score = 1
        if s < 80 or s > 180 or d < 50 or d > 110:
            score = 100
        elif (80 <= s < 90 or 140 < s <= 180) or (50 <= d < 60 or 90 < d <= 110):
            score = 75
        elif (90 <= s < 100 or 130 < s <= 140) or (60 <= d < 70 or 80 < d <= 90):
            score = 50
        return score
    except:
        return 25

def glukoz_score(val):
    try:
        g = float(val)
        if g < 40 or g > 400:
            return 100
        elif 40 <= g < 60 or 200 < g <= 400:
            return 75
        elif 60 <= g < 70 or 140 < g <= 200:
            return 50
        else:
            return 25
    except:
        return 25

def ates_score(val):
    try:
        t = float(val)
        if t < 30 or t > 41:
            return 100
        elif 30 <= t < 34 or 39 < t <= 41:
            return 75
        elif 34 <= t < 36 or 38 < t <= 39:
            return 50
        else:
            return 25
    except:
        return 25

def spo2_score(val):
    try:
        s = float(val)
        if s < 70:
            return 100
        elif 70 <= s < 85:
            return 75
        elif 85 <= s < 94:
            return 50
        else:  # 94-100
            return 25
    except:
        return 25

def solunum_score(val):
    try:
        v = float(val)
        if v < 5 or v > 40:
            return 100
        elif 5 <= v < 10 or 30 < v <= 40:
            return 75
        elif 10 <= v < 12 or 24 < v <= 30:
            return 50
        else:  # 12-24
            return 25
    except:
        return 25

def nabiz_deg_score(val):
    try:
        v = float(val)
        if v < 40 or v > 150:
            return 100
        elif 40 <= v < 50 or 130 < v <= 150:
            return 75
        elif 50 <= v < 60 or 120 < v <= 130:
            return 50
        else:  # 60-120 normal
            return 25
    except:
        return 25


# Apply all scores
df["cinsiyet_score"] = df["Cinsiyet"].map({
    "ERKEK": 100,
    "KADIN": 50
}).fillna(75)

df["yeni_dogan_score"] = df["Yeni Doğan"].apply(lambda x: 75 if x == "Yeni Doğan" else 25)
df["yas_score"] = df["Yaş"].apply(age_score)
df["adli_vaka_score"] = df["Adli Vaka"].apply(lambda x: 75 if x == "Adli Vaka" else 25)
df["cagri_nedeni_score"] = df["Çağrı Nedeni"].apply(cagri_score)
df["sonuc_score"] = df["Sonuç"].apply(sonuc_score)
df["triaj_score"] = df["Triaj"].map({"Kırmızı Kod": 100, "Sarı Kod": 75, "Yeşil Kod": 50}).fillna(10)

bilinç_map = {
    "Koma": 100, "Semikoma": 100, "Kapalı": 100, "Sedatize": 100,
    "Bulanık": 75, "Konfüze": 75, "Açık": 50
}
df["bilinc_score"] = df["Bilinç"].map(bilinç_map).fillna(25)

nabiz_map = {
    "Alınmıyor": 100, "Filiform": 100, "Aritmik": 75, "Düzenli": 50
}
df["nabiz_score"] = df["Nabız"].map(nabiz_map).fillna(25)

df["tansiyon_score"] = df["Tansiyon"].apply(tansiyon_score)
df["glukoz_score"] = df["Glukoz"].apply(glukoz_score)
df["ates_score"] = df["Ateş"].apply(ates_score)
df["spo2_score"] = df["SPO2"].apply(spo2_score)
df["solunum_score"] = df["Solunum Değeri"].apply(solunum_score)
df["nabiz_deger_score"] = df["Nabız Değeri"].apply(nabiz_deg_score)

team_codes['ASOS']= team_codes['ASOS'].str.strip()
df= df[df['Ekip No'].isin(team_codes['ASOS'])]
df= df[~df['Ekip No'].isin(['KÇK6', 'ESY4','BAG5','ZTB3', 'FTH5','BKR6', 'STG7B', 'SLV2'])]

df['ihbar_date'] = df['İhbar/Çağrı Tarih Saat'].apply(lambda x: x.date() - pd.Timedelta(days=1) if 0< x.hour < 8 else x.date())
last_year = df['ihbar_date'] >= (pd.to_datetime(df['ihbar_date'].max()) - pd.DateOffset(years=1)).date()

df_last_year = df[last_year].copy()
daily_counts = df.groupby(['Ekip No', 'ihbar_date']).size().reset_index(name='daily_case_count')
last_year_daily_counts = df_last_year.groupby(['Ekip No', 'ihbar_date']).size().reset_index(name='daily_case_count')
mean_daily_cases = daily_counts.groupby('Ekip No')['daily_case_count'].mean().rename('mean_daily_case_count')
mean_last_year_daily_cases = last_year_daily_counts.groupby('Ekip No')['daily_case_count'].mean().rename('mean_daily_case_count')

european_side_districts= [
    'Arnavutköy',
    'Avcılar',
    'Bağcılar',
    'Bahçelievler',
    'Bakırköy',
    'Bayrampaşa',
    'Başakşehir',
    'Beylikdüzü',
    'Beyoğlu',
    'Beşiktaş',
    'Büyükçekmece',
    'Çatalca',
    'Çekmeköy',
    'Esenler',
    'Esenyurt',
    'Eyüpsultan',
    'Fatih',
    'Gaziosmanpaşa',
    'Güngören',
    'Kağıthane',
    'Küçükçekmece',
    'Sarıyer',
    'Silivri',
    'Sultangazi',
    'Zeytinburnu',
    'Şişli'
    ]



df_population_density['Ilce'] = df_population_density['Ilce'].str.strip()
df_population_density['Nüfus']= df_population_density['Nüfus'].astype(float)

df_population_density= df_population_density[df_population_density['Ilce'].isin(european_side_districts)]
#df_population_density.to_csv(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\istanbul_population_density_european_side.csv")
#df_population_density.to_excel(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\istanbul_population_density_european_side.xlsx", index=False)

df_population_density= df_population_density.groupby('Ilce')['Nüfus'].sum().reset_index()

population_density_dict= df_population_density.set_index('Ilce').to_dict()['Nüfus']

df['District Population Density']= df['District'].map(population_density_dict)
df_last_year['District Population Density']= df_last_year['District'].map(population_density_dict)
df['case_count'] = 1
df_last_year['case_count'] = 1
df_district_case_counts =df.groupby(['District', 'Ekip No']).agg({'case_count':'sum', 'District Population Density':'mean'}).reset_index().sort_values(by=['District', 'case_count'], ascending=[True, False])
last_year_district_case_counts = df_last_year.groupby(['District', 'Ekip No']).agg({'case_count':'sum', 'District Population Density':'mean'}).reset_index().sort_values(by=['District', 'case_count'], ascending=[True, False])


df_district_case_counts['case_count_percentage'] = df_district_case_counts.groupby('District')['case_count'].transform(lambda x: x / x.sum() * 100)
last_year_district_case_counts['case_count_percentage'] = last_year_district_case_counts.groupby('District')['case_count'].transform(lambda x: x / x.sum() * 100)
df_district_case_counts['teams_population_density'] = df_district_case_counts['District Population Density'] / 100 * df_district_case_counts['case_count_percentage']
last_year_district_case_counts['teams_population_density'] = last_year_district_case_counts['District Population Density'] / 100 * last_year_district_case_counts['case_count_percentage']

#df_district_case_counts.to_excel(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\district_case_counts_european_side.xlsx", index=False)
#last_year_district_case_counts.to_excel(r"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\district_case_counts_european_side_last_year.xlsx", index=False)

team_population_densities= df_district_case_counts.groupby(['Ekip No']).agg({'case_count': 'sum', 'teams_population_density': 'sum'}).reset_index().sort_values(by='teams_population_density', ascending=False)
last_year_team_population_densities= last_year_district_case_counts.groupby(['Ekip No']).agg({'case_count': 'sum', 'teams_population_density': 'sum'}).reset_index().sort_values(by='teams_population_density', ascending=False)



def get_day_name_and_season(date):
    """
    Returns the current day name and season name.
    Day name is in uppercase (e.g., 'MONDAY').
    Season name is in uppercase (e.g., 'SUMMER').
    """
    date= pd.to_datetime(date, format='mixed')
    
    # Get day name
    day_name = date.strftime('%A') # e.g., 'WEDNESDAY'

    # Get season name
    def get_season(date):
        Y = date.year
        seasons = [
            ('Winter', dt.datetime(Y, 1, 1), dt.datetime(Y, 3, 21)),
            ('Spring', dt.datetime(Y, 3, 21), dt.datetime(Y, 6, 21)),
            ('Summer', dt.datetime(Y, 6, 21), dt.datetime(Y, 9, 23)),
            ('Autumn', dt.datetime(Y, 9, 23), dt.datetime(Y, 12, 21)),
            ('Winter', dt.datetime(Y, 12, 21), dt.datetime(Y+1, 1, 1))
        ]
        for season, start, end in seasons:
            if start <= date <= end:
                return season
        return 'UNKNOWN'

    season_name = get_season(date)

    return season_name, day_name


df['season'], df['day'] = zip(*df['İhbar/Çağrı Tarih Saat'].apply(get_day_name_and_season))
df_last_year['season'], df_last_year['day'] = zip(*df_last_year['İhbar/Çağrı Tarih Saat'].apply(get_day_name_and_season))

#df['season'] = df['İhbar/Çağrı Tarih Saat'].apply(lambda x: 'Winter' if x.month in [12, 1, 2] else ('Spring' if x.month in [3, 4, 5] else ('Summer' if x.month in [6, 7, 8] else 'Autumn')))
#df_last_year['season'] = df_last_year['İhbar/Çağrı Tarih Saat'].apply(lambda x: 'Winter' if x.month in [12, 1, 2] else ('Spring' if x.month in [3, 4, 5] else ('Summer' if x.month in [6, 7, 8] else 'Autumn')))
#df['day']= df['İhbar/Çağrı Tarih Saat'].dt.day_name()
#df_last_year['day']= df_last_year['İhbar/Çağrı Tarih Saat'].dt.day_name()

def logarithmic_score(value, base=10, scale=1):
    if value <= 0:
        return 0
    return scale * np.log(value + 1) / np.log(base)

def robust_z_score(series):
    median = np.nanmedian(series)
    mad = np.nanmedian(np.abs(series - median))
    
    if mad == 0:
        return pd.Series([0]*len(series), index=series.index)
    
    return (series - median) / mad

column_weights = {
    "total_distance": 4,
    "mean_daily_case_count": 1,
    "case_response_time": 2.5,
    "field_operation_time": 2.5,
    "hospital_delivery_time": 2.5,
    "cagri_nedeni_score": 2,
    "triaj_score": 4,
    "icd_score": 5,
    "yas_score": 1.5,
    "cinsiyet_score": 1.5,
    "yeni_dogan_score": 1.5,
    "adli_vaka_score": 1.5,
    "sonuc_score": 4,
    "bilinc_score": 1.5,
    "nabiz_score": 3,
    "tansiyon_score": 1.5,
    "glukoz_score": 1.5,
    "ates_score": 1.5,
    "spo2_score": 3,
    "solunum_score": 1.5,
    "nabiz_deger_score": 1,
    "teams_population_density": 1,
    "case_count": 1
}

# Grouping and calculating scores for each team by season and day
for season in df['season'].unique():
    for day in df['day'].unique():
        subset = df[(df['season'] == season) & (df['day'] == day)]
        if not subset.empty:
            df_team_grouped = subset.groupby('Ekip No').agg({
                'total_distance': 'mean',
                'field_operation_time': 'mean',
                'hospital_delivery_time': 'mean',
                'case_response_time': 'mean',
                'yas_score': 'mean',
                'cinsiyet_score': 'mean',
                'yeni_dogan_score': 'mean',
                'adli_vaka_score': 'mean',
                'cagri_nedeni_score': 'mean',
                'sonuc_score': 'mean',
                'triaj_score': 'mean',
                'bilinc_score': 'mean',
                'nabiz_score': 'mean',
                'tansiyon_score': 'mean',
                'glukoz_score': 'mean',
                'ates_score': 'mean',
                'spo2_score': 'mean',
                'solunum_score': 'mean',
                'nabiz_deger_score': 'mean',
                'icd_score': 'mean',
            })

            df_team_grouped = df_team_grouped.merge(mean_daily_cases, left_index=True, right_index=True)
            df_team_grouped= pd.merge(df_team_grouped, team_population_densities, on='Ekip No', how='left', suffixes=('', '_team_density'))
            #df_team_grouped\.drop\(columns='case_count', inplace=True, errors='ignore'\)
            
            for col in df_team_grouped.columns[1:]:
                new_col = col + '_logarithmic_score'
                df_team_grouped[new_col]= df_team_grouped[col].apply(lambda x: logarithmic_score(x, base=10, scale=1))

            for col in df_team_grouped.columns:
                if col.endswith('_logarithmic_score'):
                    new_col= col + '_MinMax_score'
                    df_team_grouped[new_col] = scaler.fit_transform(df_team_grouped[[col]]) * column_weights[col.replace('_logarithmic_score', '')]
                    df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
                
            for col in df_team_grouped.columns:
                if col.endswith('_MinMax_score'):
                    new_col = col + '_z_score'
                    df_team_grouped[new_col] = robust_z_score(df_team_grouped[col])
                    df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
            
            df_team_grouped['total_score']= df_team_grouped[[col for col in df_team_grouped.columns if col.endswith('_MinMax_score')]].sum(axis=1)
            df_team_grouped['strategic_score']= df_team_grouped['total_score'] / df_team_grouped['mean_daily_case_count']
            df_team_grouped['total_score']= df_team_grouped['total_score'] * df_team_grouped['mean_daily_case_count']* df_team_grouped['sonuc_score']
            #df_team_grouped['strategic_total_score']= df_team_grouped[[col for col in df_team_grouped.columns if not col.endswith('_logarithmic_score') and col != 'total_score' and col !='mean_daily_case_count' and col!= 'Ekip No' and col != 'teams_population_density' or col == 'case_count_logarithmic_score' or col == 'teams_population_density_logarithmic_score']].sum(axis=1)
            
            df_team_grouped['total_score_z']= robust_z_score(df_team_grouped['total_score'])
            df_team_grouped['strategic_score_z']= robust_z_score(df_team_grouped['strategic_score'])
            total_score_mean= df_team_grouped['total_score'].mean()
            strategic_score_mean= df_team_grouped['strategic_score'].mean()
            df_team_grouped['station_expendable']= df_team_grouped.apply(lambda x: 'Expendable' if x['total_score_z'] < 0 and x['strategic_score_z'] < -1.5 else 'Hardly Expendable' if x['total_score_z'] < 1 and x['strategic_score_z'] < 0 else 'Non-Expendable', axis=1)
            df_team_grouped= df_team_grouped.sort_values(by='total_score_z', ascending=False).reset_index()

            df_team_grouped.reset_index(drop=True).to_excel(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\overall\{season}_{day}_total scores.xlsx")


# Grouping and calculating scores for each team by season and day
for season in df_last_year['season'].unique():
    for day in df_last_year['day'].unique():
        subset = df_last_year[(df_last_year['season'] == season) & (df_last_year['day'] == day)]
        if not subset.empty:
            df_team_grouped = subset.groupby('Ekip No').agg({
                'total_distance': 'mean',
                'field_operation_time': 'mean',
                'hospital_delivery_time': 'mean',
                'case_response_time': 'mean',
                'yas_score': 'mean',
                'cinsiyet_score': 'mean',
                'yeni_dogan_score': 'mean',
                'adli_vaka_score': 'mean',
                'cagri_nedeni_score': 'mean',
                'sonuc_score': 'mean',
                'triaj_score': 'mean',
                'bilinc_score': 'mean',
                'nabiz_score': 'mean',
                'tansiyon_score': 'mean',
                'glukoz_score': 'mean',
                'ates_score': 'mean',
                'spo2_score': 'mean',
                'solunum_score': 'mean',
                'nabiz_deger_score': 'mean',
                'icd_score': 'mean',
            })

            df_team_grouped = df_team_grouped.merge(mean_last_year_daily_cases, left_index=True, right_index=True)
            df_team_grouped= pd.merge(df_team_grouped, last_year_team_population_densities, on='Ekip No', how='left', suffixes=('', '_team_density'))
            #df_team_grouped\.drop\(columns='case_count', inplace=True, errors='ignore'\)
            
            for col in df_team_grouped.columns[1:]:
                new_col = col + '_logarithmic_score'
                df_team_grouped[new_col]= df_team_grouped[col].apply(lambda x: logarithmic_score(x, base=10, scale=1))

            for col in df_team_grouped.columns:
                if col.endswith('_logarithmic_score'):
                    new_col= col + '_MinMax_score'
                    df_team_grouped[new_col] = scaler.fit_transform(df_team_grouped[[col]]) * column_weights[col.replace('_logarithmic_score', '')]
                    df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
                
            for col in df_team_grouped.columns:
                if col.endswith('_MinMax_score'):
                    new_col = col + '_z_score'
                    df_team_grouped[new_col] = robust_z_score(df_team_grouped[col])
                    df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
            
            df_team_grouped['total_score']= df_team_grouped[[col for col in df_team_grouped.columns if col.endswith('_MinMax_score')]].sum(axis=1)
            df_team_grouped['strategic_score']= df_team_grouped['total_score'] / df_team_grouped['mean_daily_case_count'] 
            df_team_grouped['total_score']= df_team_grouped['total_score'] * df_team_grouped['mean_daily_case_count']* df_team_grouped['sonuc_score']
            #df_team_grouped['strategic_total_score']= df_team_grouped[[col for col in df_team_grouped.columns if not col.endswith('_logarithmic_score') and col != 'total_score' and col !='mean_daily_case_count' and col!= 'Ekip No' or col == 'case_count_logarithmic_score' or col == 'teams_population_density_logarithmic_score']].sum(axis=1)
            
            df_team_grouped['total_score_z']= robust_z_score(df_team_grouped['total_score'])
            df_team_grouped['strategic_score_z']= robust_z_score(df_team_grouped['strategic_score'])
            total_score_mean= df_team_grouped['total_score'].mean()
            strategic_score_mean= df_team_grouped['strategic_score'].mean()
            df_team_grouped['station_expendable']= df_team_grouped.apply(lambda x: 'Expendable' if x['total_score_z'] < 0 and x['strategic_score_z'] < -1.5 else 'Hardly Expendable' if x['total_score_z'] < 1 and x['strategic_score_z'] < 0 else 'Non-Expendable', axis=1)
            df_team_grouped= df_team_grouped.sort_values(by='total_score_z', ascending=False).reset_index()

            df_team_grouped.reset_index(drop=True).to_excel(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\last_year\{season}_{day}_total scores.xlsx")
            
# Final aggregation for last year
df_team_grouped = df_last_year.groupby('Ekip No').agg({
                'total_distance': 'mean',
                'field_operation_time': 'mean',
                'hospital_delivery_time': 'mean',
                'case_response_time': 'mean',
                'yas_score': 'mean',
                'cinsiyet_score': 'mean',
                'yeni_dogan_score': 'mean',
                'adli_vaka_score': 'mean',
                'cagri_nedeni_score': 'mean',
                'sonuc_score': 'mean',
                'triaj_score': 'mean',
                'bilinc_score': 'mean',
                'nabiz_score': 'mean',
                'tansiyon_score': 'mean',
                'glukoz_score': 'mean',
                'ates_score': 'mean',
                'spo2_score': 'mean',
                'solunum_score': 'mean',
                'nabiz_deger_score': 'mean',
                'icd_score': 'mean',
            })


df_team_grouped = df_team_grouped.merge(mean_last_year_daily_cases, left_index=True, right_index=True)
df_team_grouped= pd.merge(df_team_grouped, last_year_team_population_densities, on='Ekip No', how='left', suffixes=('', '_team_density'))
#df_team_grouped\.drop\(columns='case_count', inplace=True, errors='ignore'\)

for col in df_team_grouped.columns[1:]:
    new_col = col + '_logarithmic_score'
    df_team_grouped[new_col]= df_team_grouped[col].apply(lambda x: logarithmic_score(x, base=10, scale=1))

for col in df_team_grouped.columns:
    if col.endswith('_logarithmic_score'):
        new_col= col + '_MinMax_score'
        df_team_grouped[new_col] = scaler.fit_transform(df_team_grouped[[col]]) * column_weights[col.replace('_logarithmic_score', '')]
        df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
    
for col in df_team_grouped.columns:
    if col.endswith('_MinMax_score'):
        new_col = col + '_z_score'
        df_team_grouped[new_col] = robust_z_score(df_team_grouped[col])
        df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))

df_team_grouped['total_score']= df_team_grouped[[col for col in df_team_grouped.columns if col.endswith('_MinMax_score')]].sum(axis=1)
df_team_grouped['strategic_score']= df_team_grouped['total_score'] / df_team_grouped['mean_daily_case_count']
df_team_grouped['total_score']= df_team_grouped['total_score'] * df_team_grouped['mean_daily_case_count']* df_team_grouped['sonuc_score']
#df_team_grouped['strategic_total_score']= df_team_grouped[[col for col in df_team_grouped.columns if not col.endswith('_logarithmic_score') and col != 'total_score' and col !='mean_daily_case_count' and col!= 'Ekip No' or col == 'case_count_logarithmic_score' or col == 'teams_population_density_logarithmic_score']].sum(axis=1)

df_team_grouped['total_score_z']= robust_z_score(df_team_grouped['total_score'])
df_team_grouped['strategic_score_z']= robust_z_score(df_team_grouped['strategic_score'])
total_score_mean= df_team_grouped['total_score'].mean()
strategic_score_mean= df_team_grouped['strategic_score'].mean()
df_team_grouped['station_expendable']= df_team_grouped.apply(lambda x: 'Expendable' if x['total_score_z'] < 0 and x['strategic_score_z'] < -1.5 else 'Hardly Expendable' if x['total_score_z'] < 1 and x['strategic_score_z'] < 0 else 'Non-Expendable', axis=1)
df_team_grouped= df_team_grouped.sort_values(by='total_score_z', ascending=False).reset_index()

df_team_grouped.reset_index(drop=True).to_excel(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\last_year\1- GENERAL_last year_total scores.xlsx")

# Final aggregation for all data   
df_team_grouped = df.groupby('Ekip No').agg({
                'total_distance': 'mean',
                'field_operation_time': 'mean',
                'hospital_delivery_time': 'mean',
                'case_response_time': 'mean',
                'yas_score': 'mean',
                'cinsiyet_score': 'mean',
                'yeni_dogan_score': 'mean',
                'adli_vaka_score': 'mean',
                'cagri_nedeni_score': 'mean',
                'sonuc_score': 'mean',
                'triaj_score': 'mean',
                'bilinc_score': 'mean',
                'nabiz_score': 'mean',
                'tansiyon_score': 'mean',
                'glukoz_score': 'mean',
                'ates_score': 'mean',
                'spo2_score': 'mean',
                'solunum_score': 'mean',
                'nabiz_deger_score': 'mean',
                'icd_score': 'mean',
            })


df_team_grouped = df_team_grouped.merge(mean_daily_cases, left_index=True, right_index=True)
df_team_grouped= pd.merge(df_team_grouped, team_population_densities, on='Ekip No', how='left', suffixes=('', '_team_density'))
#df_team_grouped\.drop\(columns='case_count', inplace=True, errors='ignore'\)
        
for col in df_team_grouped.columns[1:]:
    new_col = col + '_logarithmic_score'
    df_team_grouped[new_col]= df_team_grouped[col].apply(lambda x: logarithmic_score(x, base=10, scale=1))

for col in df_team_grouped.columns:
    if col.endswith('_logarithmic_score'):
        new_col= col + '_MinMax_score'
        df_team_grouped[new_col] = scaler.fit_transform(df_team_grouped[[col]]) * column_weights[col.replace('_logarithmic_score', '')]
        df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
    
for col in df_team_grouped.columns:
    if col.endswith('_MinMax_score'):
        new_col = col + '_z_score'
        df_team_grouped[new_col] = robust_z_score(df_team_grouped[col])
        df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))

df_team_grouped['total_score']= df_team_grouped[[col for col in df_team_grouped.columns if col.endswith('_MinMax_score')]].sum(axis=1)
df_team_grouped['strategic_score']= df_team_grouped['total_score'] / df_team_grouped['mean_daily_case_count']
df_team_grouped['total_score']= df_team_grouped['total_score'] * df_team_grouped['mean_daily_case_count']* df_team_grouped['sonuc_score']
#df_team_grouped['strategic_total_score']= df_team_grouped[[col for col in df_team_grouped.columns if not col.endswith('_MinMax_score') and col != 'total_score' and col !='mean_daily_case_count' and col!= 'Ekip No' or col == 'case_count_logarithmic_score' or col == 'teams_population_density_logarithmic_score']].sum(axis=1)

df_team_grouped['total_score_z']= robust_z_score(df_team_grouped['total_score'])
df_team_grouped['strategic_score_z']= robust_z_score(df_team_grouped['strategic_score'])
total_score_mean= df_team_grouped['total_score'].mean()
strategic_score_mean= df_team_grouped['strategic_score'].mean()
df_team_grouped['station_expendable']= df_team_grouped.apply(lambda x: 'Expendable' if x['total_score_z'] < 0 and x['strategic_score_z'] < -1.5 else 'Hardly Expendable' if x['total_score_z'] < 1 and x['strategic_score_z'] < 0 else 'Non-Expendable', axis=1)
df_team_grouped= df_team_grouped.sort_values(by='total_score_z', ascending=False).reset_index()

df_team_grouped.reset_index(drop=True).to_excel(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\overall\1- GENERAL_total scores.xlsx")            

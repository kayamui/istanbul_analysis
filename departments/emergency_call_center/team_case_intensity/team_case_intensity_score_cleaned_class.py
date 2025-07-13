import pandas as pd
import numpy as np

import datetime as dt

import os

import geopandas as gpd
from shapely.geometry import Point

from sklearn.preprocessing import MinMaxScaler
scaler= MinMaxScaler()

import json

import logging

RAW_DATA_PATH= rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\test\raw_datas"
OVERALL_SAVE_PATH= rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\test\overall"
LAST_YEAR_SAVE_PATH= rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\test\last_year"

POPULATION_DENSITY_PATH= rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\populations\istanbul_population_density.csv"
DISTRICTS_DATA_PATH= rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\locations\istanbul-districts.json"
NEIGHBOURHOODS_GDF_PATH= rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\locations\istanbul_neighbourhoods.geojson"

ICD_DIAGNOSES_PATH= rf"C:\Users\mkaya\OneDrive\Belgeler\GitHub\istanbul_analysis\ipynb_workouts\icd10_diagnoses_scored.csv"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataCreator:
    
    def __init__(self, path, districts_data, neighbourhoods_gdf):
        
        self.districts_data= districts_data
        self.neighbourhoods_gdf= neighbourhoods_gdf
        self.path= path
        
        self.df= pd.DataFrame()
        self.df= pd.DataFrame()
        self.region= None
        
    def read_files(self):
        case_files= list(set([file for file in os.listdir(self.path) if file.endswith('.parquet')]))
        
        if case_files.empty:
            raise ValueError("No parquet files found in the specified directory!")
        
        for file in case_files:
            file_path= os.path.join(self.path, file)
            logging.info(f"Reading file: {file_path}")
            df= pd.read_parquet(file_path)
            logging.info(f"==================================================\nFile {file} read successfully with shape {df.shape}\n==================================================")
            df= self.get_district_neighbourhood(df)
            logging.info(f"==================================================\nFile {file} region assigned successfully with shape {df.shape}\n==================================================")
            df= self.convert_columns(df)
            logging.info(f"==================================================\nFile {file} columns converted successfully with shape {df.shape}\n==================================================")
            df= self.necessary_columns(df)
            logging.info(f"==================================================\nFile {file} necessary columns assigned successfully with shape {df.shape}\n==================================================")
            
            logging.info(f"File {file} processed and necessary columns assigned.")

            self.df= pd.concat([self.df, df], ignore_index=True)
            
            logging.info(f"==================================================\nThe shape of dataframe is {self.df.shape}\n==================================================")
        
        self.df= self.assign_region()
        logging.info("Regions assigned successfully.")
    
        return self.df
    
    def assign_region(self):
        """Assigns a region based on the key."""
        
        eu_team_codes= [
            'ARN',
            'AVC',
            'BAG',
            'BKR',
            'BEŞ',
            'BEY',
            'BÇK',
            'BDZ',
            'BHC',
            'BKR',
            'BŞK',
            'BYR',
            'ÇTL',
            'ESN',
            'ESY',
            'EYP',
            'FTH',
            'GNG',
            'GOP',
            'KÇK',
            'KĞT',
            'SLV',
            'SRY',
            'STG',
            'ŞİŞ',
            'ZTB',
        ]
        
        asia_team_codes= [
            'ATŞ',
            'BYZ',
            'KDY',
            'KRL',
            'MLT',
            'PND',
            'PDN',
            'SNC',
            'SBY',
            'TZL',
            'ÇKY',
            'ÜMR',
            'ÜSK',
            'ŞLE'
        ]
        
        not_assigned_regions= [
            'MTR',
            'ADL',
        ]
        
        non_included_codes = ['KÇK6', 'ESY4','BAG5','ZTB3', 'FTH5','BKR6', 'STG7B', 'SLV2']
        logging.info(f"non_included team codes excluded new shape of self.df is {self.df.shape}")
        
        if self.df[self.df['Ekip No'].apply(lambda x: x[:3] in eu_team_codes)].shape[0] > self.df[self.df['Ekip No'].apply(lambda x: x[:3] in asia_team_codes)].shape[0] * 9:
            team_codes= eu_team_codes
            logging.warning("More than %90 of cases are from Europe, setting region to Europe!")
            self.region= 'Europe'
        
        elif self.df[self.df['Ekip No'].apply(lambda x: x[:3] in asia_team_codes)].shape[0] > self.df[self.df['Ekip No'].apply(lambda x: x[:3] in eu_team_codes)].shape[0] * 9:
            team_codes= asia_team_codes
            logging.warning("More than %90 of cases are from Asia, setting region to Asia!")
            self.region= 'Asia'
        else:
            logging.warning("No specific region found, setting region to Both!")
            self.region= 'Both'
            team_codes= eu_team_codes + asia_team_codes
            
        self.df['Ekip No']= self.df['Ekip No'].apply(lambda x: x if isinstance(x, str) and x[:3] not in not_assigned_regions and x not in non_included_codes and len(x) >= 3 and x else 'Unknown').map(
            lambda x: x if x[:3] in team_codes else 'Unknown'
        )
        
        self.df= self.df[self.df['Ekip No'] != 'Unknown']
        
        logging.info(f"=============================================================\n\n\nUnknown stations excluded, new shape of self.df is {self.df.shape}")
        logging.info(f"Regions assigned based on team codes: {team_codes}\n")
        logging.info(f"regions existing in self.df is {self.df['Ekip No'].unique()}\n=============================================================\n\n\n")
        
        return self.df

    def get_district_neighbourhood(self, df):

        districts_gdf = gpd.GeoDataFrame.from_features(self.districts_data["features"])
        
        lat = "Vakanın Enlemi" if "Vakanın Enlemi" in df.columns else str(input('latitude column: '))
        lon = "Vakanın Boylamı" if "Vakanın Boylamı" in df.columns else str(input('longitude column: '))
        
        columns= [col for col in df.columns] + ['Neighbourhood', 'District']
        # Load neighborhoods
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
        points_gdf = gpd.sjoin(points_gdf, self.neighbourhoods_gdf, how="left", predicate="within")
        points_gdf.rename(columns={"name": "Neighbourhood"}, inplace=True)
        points_gdf['District']= points_gdf['District'].astype(str).str.strip()
        
        # Select relevant columns and return
        logging.info(f"\n\n==================================================\nShape of points_gdf: {points_gdf.shape}\n\n==================================================")
        return points_gdf[columns]
    
    def get_districts(self):
        """Returns a list of European side districts."""
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
            'Şişli']
        
        asian_side_districts= [
            'Adalar',
            'Ataşehir',
            'Beykoz',
            'Çekmeköy',
            'Kadıköy',
            'Kartal',
            'Maltepe',
            'Pendik',
            'Sancaktepe',
            'Sultanbeyli',
            'Tuzla',
            'Ümraniye',
            'Üsküdar'
            ]
        if self.region == 'Europe':
            european_side_districts= [district.upper() for district in european_side_districts]
            return self.df[self.df['District'].isin(european_side_districts)]
        elif self.region == 'Asia':
            return self.df[self.df['District'].isin(asian_side_districts)]
        else:
            return self.df[self.df['District'].isin(european_side_districts + asian_side_districts)]
    
    def convert_columns(self,df):
        for col in df.columns:
            if col=="ICD10 TANI \nADI":
                df.rename(columns={'ICD10 TANI \nADI':'ICD10 TANI\nADI'}, inplace=True)
            if col=="ICD10 TANI \nADI":
                df.rename(columns={'ICD10 TANI \nADI':'ICD10 TANI\nADI'}, inplace=True)
            if col=='Vaka Veriliş':
                df.rename(columns={'Vaka Veriliş':'Vaka Veriliş Tarih Saat'}, inplace=True)
                df['Vaka Veriliş Tarih Saat'] = pd.to_datetime(df['Vaka Veriliş Tarih Saat'], format='mixed', errors='coerce')
            if col == 'Ulaşım Sn':
                df.rename(columns={'Ulaşım Sn':'Ulaşım Sn\n(Olay Yeri Varış Tarihi - Çağrı Tarihi)'}, inplace=True)
            if col == 'İhbar Tarihi':
                df.rename(columns={'İhbar Tarihi':'İhbar/Çağrı Tarih Saat'}, inplace=True)
                df['İhbar/Çağrı Tarih Saat'] = pd.to_datetime(df['İhbar/Çağrı Tarih Saat'], format='mixed', errors='coerce')
            if col == 'Olay Yeri Varış':
                df.rename(columns={'Olay Yeri Varış':'Olay Yeri Varış Tarih Saat'}, inplace=True)
                df['Olay Yeri Varış Tarih Saat'] = pd.to_datetime(df['Olay Yeri Varış Tarih Saat'], format='mixed', errors='coerce')
            if col == 'Olay Yeri Ayrılış':
                df.rename(columns={'Olay Yeri Ayrılış':'Olay Yeri Ayrılış Tarih Saat'}, inplace=True)
            if col == 'Hastaneye Varış':
                df.rename(columns={'Hastaneye Varış':'Hastaneye Varış Tarih Saat'}, inplace=True)
                df['Hastaneye Varış Tarih Saat'] = pd.to_datetime(df['Hastaneye Varış Tarih Saat'], format='mixed', errors='coerce')
            if col == 'Hastaneden Ayrılış':
                df.rename(columns={'Hastaneden Ayrılış':'Hastaneden Ayrılış Tarih Saat'}, inplace=True)
                df['Hastaneden Ayrılış Tarih Saat'] = pd.to_datetime(df['Hastaneden Ayrılış Tarih Saat'], format='mixed', errors='coerce')
            if col == 'İstasyona Dönüş':
                df.rename(columns={'İstasyona Dönüş':'İstasyona Dönüş Tarih Saat'}, inplace=True)
                df['İstasyona Dönüş Tarih Saat'] = pd.to_datetime(df['İstasyona Dönüş Tarih Saat'], format='mixed', errors='coerce')
                
            # Rename column if necessary
            if "Hastaneye Varış Saati\n" in df.columns:
                df.rename(columns={"Hastaneye Varış Saati\n": "Hastaneye Varış Saati"}, inplace=True)

            # Process 'İhbar/Çağrı Tarih Saat' or create it if needed
            if "İhbar/Çağrı Tarih Saat" not in df.columns:
                logging.info(f"Creating İhbar/Çağrı Tarih Saat")
                # First, apply the parse_date function to the original date column
                if 'İhbar/Çağrı Tarihi' in df.columns and 'İhbar/Çağrı  Saati' in df.columns:

                    # Convert time column to string, handling potential non-string types
                    df['İhbar/Çağrı  Saati'] = df['İhbar/Çağrı  Saati']
                    # Combine date and time columns, coercing errors
                    df["İhbar/Çağrı Tarih Saat"] = pd.to_datetime(
                        df['İhbar/Çağrı Tarihi']+ ' ' + df['İhbar/Çağrı  Saati'],
                        format='mixed'
                    )
                else:
                    logging.warning(f"Warning: 'İhbar/Çağrı Tarihi' or 'İhbar/Çağrı  Saati' not found. Cannot create 'İhbar/Çağrı Tarih Saat'.")
            else:
                # If 'İhbar/Çağrı Tarih Saat' already exists, ensure it's in datetime format
                #logging.info(f"Converting İhbar/Çağrı Tarih Saat to datetime for df")
                df['İhbar/Çağrı Tarih Saat'] = pd.to_datetime(df['İhbar/Çağrı Tarih Saat'], format= 'mixed')


            # Process 'Vaka Veriliş Tarih Saat'
            if "Vaka Veriliş Tarih Saat" not in df.columns:
                logging.info(f"Creating Vaka Veriliş Tarih Saat")
                if 'Vaka Veriliş\nTarihi' in df.columns and 'Vaka Veriliş\nSaati' in df.columns:
                    df['Vaka Veriliş\nSaati'] = df['Vaka Veriliş\nSaati']
                    df["Vaka Veriliş Tarih Saat"] = pd.to_datetime(
                        df['Vaka Veriliş\nTarihi'] + ' ' + df['Vaka Veriliş\nSaati'],
                        format='mixed'
                    )
                else:
                    logging.warning(f"Warning: 'Vaka Veriliş\\nTarihi' or 'Vaka Veriliş\\nSaati' not found. Cannot create 'Vaka Veriliş Tarih Saat'.")
            else:
                #logging.info(f"Converting Vaka Veriliş Tarih Saat to datetime for df")
                df['Vaka Veriliş Tarih Saat'] = pd.to_datetime(df['Vaka Veriliş Tarih Saat'], format= 'mixed')


            # Process 'Olay Yeri Varış Tarih Saat'
            if "Olay Yeri Varış Tarih Saat" not in df.columns:
                logging.info(f"Creating Olay Yeri Varış Tarih Saat")
                if 'Olay Yeri Varış Tarihi' in df.columns and 'Olay Yeri Varış Saati' in df.columns:
                    df['Olay Yeri Varış Saati'] = df['Olay Yeri Varış Saati']
                    df["Olay Yeri Varış Tarih Saat"] = pd.to_datetime(
                        df['Olay Yeri Varış Tarihi'] + ' ' + df['Olay Yeri Varış Saati'],
                        format='mixed'
                    )
                else:
                    logging.warning(f"Warning: 'Olay Yeri Varış Tarihi' or 'Olay Yeri Varış Saati' not found. Cannot create 'Olay Yeri Varış Tarih Saat'.")
            else:
                #logging.info(f"Converting Olay Yeri Varış Tarih Saat to datetime for df")
                df['Olay Yeri Varış Tarih Saat'] = pd.to_datetime(df['Olay Yeri Varış Tarih Saat'], format='mixed')

            # Process 'Olay Yeri Ayrılış Tarih Saat'
            if 'Olay Yeri Ayrılış Tarih Saat' not in df.columns:
                logging.info(f"Creating Olay Yeri Ayrılış Tarih Saat")
                if 'Olay Yeri Ayrılış Tarihi' in df.columns and 'Olay Yeri Ayrılış Saati' in df.columns:
                    df['Olay Yeri Ayrılış Saati'] = df['Olay Yeri Ayrılış Saati']
                    df["Olay Yeri Ayrılış Tarih Saat"] = pd.to_datetime(
                        df['Olay Yeri Ayrılış Tarihi'] + ' ' + df['Olay Yeri Ayrılış Saati'],
                        format='mixed'
                    )
                else:
                    logging.warning(f"Warning: 'Olay Yeri Ayrılış Tarihi' or 'Olay Yeri Ayrılış Saati' not found. Cannot create 'Olay Yeri Ayrılış Tarih Saat'.")
            else:
                #logging.info(f"Converting Olay Yeri Ayrılış Tarih Saat to datetime")
                df['Olay Yeri Ayrılış Tarih Saat'] = pd.to_datetime(df['Olay Yeri Ayrılış Tarih Saat'], format= 'mixed')

            # Process 'Hastaneye Varış Tarih Saat'
            # Note the inconsistent column name 'Hastaneye varış Tarih Saat' found in the traceback
            if 'Hastaneye Varış Tarih Saat' not in df.columns and 'Hastaneye varış Tarih Saat' in df.columns:
                df.rename(columns={'Hastaneye varış Tarih Saat':'Hastaneye Varış Tarih Saat'}, inplace=True)

            if 'Hastaneye Varış Tarih Saat' not in df.columns:
                logging.info(f"Creating Hastaneye Varış Tarih Saat")
                if 'Hastaneye Varış Tarihi' in df.columns and 'Hastaneye Varış Saati' in df.columns:
                    df['Hastaneye Varış Saati'] = df['Hastaneye Varış Saati']
                    df["Hastaneye Varış Tarih Saat"] = pd.to_datetime(
                        df['Hastaneye Varış Tarihi'] + ' ' + df['Hastaneye Varış Saati'],
                        format='mixed'
                    )
                else:
                    logging.warning(f"Warning: 'Hastaneye Varış Tarihi' or 'Hastaneye Varış Saati' not found. Cannot create 'Hastaneye Varış Tarih Saat'.")
            else:
                #logging.info(f"Converting Hastaneye Varış Tarih Saat to datetime")
                df['Hastaneye Varış Tarih Saat'] = pd.to_datetime(df['Hastaneye Varış Tarih Saat'], format='mixed')

            # Process 'Hastaneden Ayrılış Tarih Saat'
            if 'Hastaneden Ayrılış Tarih Saat' not in df.columns:
                logging.info(f"Creating Hastaneden Ayrılış Tarih Saat")
                if 'Hastaneden Ayrılış Tarihi' in df.columns and 'Hastaneden Ayrılış Saati' in df.columns:
                    df['Hastaneden Ayrılış Saati'] = df['Hastaneden Ayrılış Saati']
                    df["Hastaneden Ayrılış Tarih Saat"] = pd.to_datetime(
                        df['Hastaneden Ayrılış Tarihi'] + ' ' + df['Hastaneden Ayrılış Saati'],
                        format='mixed'
                    )
                else:
                    logging.warning(f"Warning: 'Hastaneden Ayrılış Tarihi' or 'Hastaneden Ayrılış Saati' not found. Cannot create 'Hastaneden Ayrılış Tarih Saat'.")
            else:
                #logging.info(f"Converting Hastaneden Ayrılış Tarih Saat to datetime for df")
                df['Hastaneden Ayrılış Tarih Saat'] = pd.to_datetime(df['Hastaneden Ayrılış Tarih Saat'], format='mixed')
            
        return df
    
    def necessary_columns(self,df):
        # Ensure necessary columns are present
        necessary_columns= ['KKM Protokol',
                            'Ekip No',
                            'İhbar/Çağrı Tarih Saat',
                            'Cinsiyet',
                            'Yeni Doğan',
                            'Yaş',
                            'Adli Vaka',
                            'Çağrı Nedeni',
                            'Sonuç',
                            'Nakledilen Hastane',
                            'ICD10 TANI\nADI',
                            'Triaj', 'Bilinç',
                            'Nabız',
                            'Vaka Veriliş Tarih Saat',
                            'Olay Yeri Varış Tarih Saat',
                            'Olay Yeri Ayrılış Tarih Saat',
                            'Hastaneye Varış Tarih Saat',
                            'Hastaneden Ayrılış Tarih Saat',
                            'Müdahale Süresi Sn',
                            'Hastane Teslim Süresi Sn',
                            'Çıkış KM',
                            'Varış KM',
                            'Hastaneye Varış KM',
                            'Dönüş KM',
                            'Vakanın Enlemi',
                            'Vakanın Boylamı',
                            'Tansiyon',
                            'Glukoz',
                            'Ateş',
                            'SPO2',
                            'Solunum Değeri',
                            'Nabız Değeri']
        
        columns_to_be_added= [col for col in necessary_columns if col not in df.columns]
        
        for col in columns_to_be_added:
            df[col]= np.nan
        
        return df
    

class DataConverter:
    def __init__(self, population_density, icd_diagnoses, df):
        self.population_density = population_density
        self.icd_diagnoses = icd_diagnoses
        self.df = df
        self.districts_data = districts_data
        self.neighbourhoods_gdf = neighbourhoods_gdf

    
    def create_population_dict(self):
        
        self.population_density['Ilce']= self.population_density['Ilce'].str.strip()
        self.population_density['Nüfus']= self.population_density['Nüfus'].astype(float)
        self.population_density= self.population_density[['Ilce', 'Nüfus']]
        self.population_density.rename(columns={'Nüfus':'District Population Density', 'Ilce':'District'}, inplace=True)
        population_density_dict= self.population_density.set_index('District').to_dict()['District Population Density']
        
        return population_density_dict
    
    def create_icd_dict(self):
        self.icd_diagnoses['ICD10 TANI']= self.icd_diagnoses['ICD10 TANI'].str.strip()
        icd_scores_dict= self.icd_diagnoses.set_index('ICD10 TANI').to_dict()['Expanded Score']
        
        return icd_scores_dict
    
    def convert_dataframe(self):
        """Converts columns to appropriate data types and handles errors."""
        if 'Yaş' not in self.df.columns:
            logging.error("Yaş column not found in the DataFrame.")
            raise KeyError("Yaş column not found in the DataFrame.")
        elif self.df['Yaş'].isnull().all():
            logging.warning("Yaş column is empty or contains only NaN values.")
        
        else:
            logging.info("Yaş column found in the DataFrame.")
        try:
            self.df['Yaş']= self.df['Yaş'].astype(str).str.replace('-', '')
        except Exception as e:
            logging.error(f"Error converting Yaş column: {e}")

        self.df['Ateş']= self.df['Ateş'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
        self.df['Yaş']= self.df['Yaş'].apply(lambda x: int(x) if isinstance(x, str) and x.isdigit() else np.nan)
        self.df['Nabız Değeri']= self.df['Nabız Değeri'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
        self.df['Glukoz']= self.df['Glukoz'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
        self.df['SPO2']= self.df['SPO2'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)
        self.df['Solunum Değeri']= self.df['Solunum Değeri'].apply(lambda x: float(x) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else np.nan)

        self.df.loc[(self.df['total_distance']>1000) | (self.df['total_distance']<0), 'total_distance']= np.nan
        self.df.loc[(self.df['case_response_time']>43200) | (self.df['case_response_time']<0), 'case_response_time']= np.nan
        self.df.loc[(self.df['field_operation_time']>86400) | (self.df['field_operation_time']<0), 'field_operation_time']= np.nan
        self.df.loc[(self.df['hospital_delivery_time']>86400) | (self.df['hospital_delivery_time']<0), 'hospital_delivery_time']= np.nan
        self.df.loc[(self.df['Ateş'] > 50) | (self.df['Ateş'] < 0), 'Ateş'] = np.nan
        self.df.loc[(self.df['Yaş'] > 120) | (self.df['Yaş'] < 0), 'Yaş'] = np.nan
        self.df.loc[(self.df['Nabız Değeri'] > 300) | (self.df['Nabız Değeri'] < 0), 'Nabız Değeri'] = np.nan
        self.df.loc[(self.df['Glukoz'] > 1000) | (self.df['Glukoz'] < 0), 'Glukoz'] = np.nan
        self.df.loc[(self.df['SPO2'] > 100) | (self.df['SPO2'] < 0), 'SPO2'] = np.nan
        self.df.loc[(self.df['Solunum Değeri'] > 100) | (self.df['Solunum Değeri'] < 0), 'Solunum Değeri'] = np.nan
        self.df.fillna({'Ateş':np.nan}, inplace=True)
        self.df.fillna({'Yaş':np.nan}, inplace=True)  
        self.df.fillna({'Nabız Değeri': np.nan}, inplace=True)
        self.df.fillna({'Glukoz':np.nan}, inplace=True)
        self.df.fillna({'SPO2':np.nan}, inplace=True)
        self.df.fillna({'Solunum Değeri':np.nan}, inplace=True)
        self.df.fillna({'Çıkış KM': np.nan}, inplace=True)
        self.df.fillna({'Varış KM':np.nan}, inplace=True)

        return self.df
    
    def create_columns(self):
        
        icd_dict= self.create_icd_dict()
        self.df['case_count']= 1
        self.df['District Population Density']= self.df['District'].map(self.create_population_dict())
        self.df['case_count_percentage']= self.df.groupby('District')['case_count'].transform(lambda x: x / x.sum() * 100)
        
        self.df['teams_population_density']= self.df['District Population Density'] / 100 * self.df['case_count_percentage']
        
        self.df['icd_score']= self.df['ICD10 TANI\nADI'].map(icd_dict)
    
        self.df['case_response_time'] = round((pd.to_datetime(self.df['Olay Yeri Varış Tarih Saat']) - pd.to_datetime(self.df['İhbar/Çağrı Tarih Saat'])).dt.total_seconds(), 2)  # Convert to seconds

        self.df['total_distance'] = self.df["Dönüş KM"].astype(float) - self.df['Çıkış KM'].astype(float)
        self.df['field_operation_time'] = round((pd.to_datetime(self.df['Olay Yeri Ayrılış Tarih Saat']) - pd.to_datetime(self.df['İhbar/Çağrı Tarih Saat'])).dt.total_seconds(), 2)        # Convert to seconds
        self.df['hospital_delivery_time'] = round((pd.to_datetime(self.df['Hastaneye Varış Tarih Saat']) - pd.to_datetime(self.df['Olay Yeri Ayrılış Tarih Saat'])).dt.total_seconds(), 2)  # Convert to seconds
        
        if 'İhbar/Çağrı Tarih Saat' not in self.df.columns:
            logging.error("İhbar/Çağrı Tarih Saat column not found in the DataFrame.")
            raise KeyError("İhbar/Çağrı Tarih Saat column not found in the DataFrame.")
        else:
            logging.info("İhbar/Çağrı Tarih Saat column found in the DataFrame.")
        
        try:
            results = list(self.df['İhbar/Çağrı Tarih Saat'].apply(self.get_day_name_and_season))
            if results:
                self.df['season'], self.df['day'] = zip(*results)
            else:
                logging.warning("No results returned from get_day_name_and_season")
                self.df['season'] = 'Unknown'
                self.df['day'] = 'Unknown'
        except ValueError as e:
            logging.error(f"Error unpacking results: {e}")
            self.df['season'] = 'Unknown'
            self.df['day'] = 'Unknown'
        
        return self.df
    
    def get_day_name_and_season(self,date):
        
        """
        Returns the current day name and season name.
        Day name is in uppercase (e.g., 'MONDAY').
        Season name is capitalized (e.g., 'Summer').
        """
        try:
            date = pd.to_datetime(date, format='mixed')
            
            # Get day name
            day_name = date.strftime('%A')  # e.g., 'WEDNESDAY'

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
                return 'Unknown'  # Fallback if no season is found
            
            season_name = get_season(date)
            
            return season_name, day_name
        
        except Exception as e:
            # Return default values if there's any error
            logging.warning(f"Error processing date {date}: {e}")
            return 'Unknown', 'Unknown'
    
    def get_chief_day(self, date):
        
        return date.apply(lambda x: x.date() - pd.Timedelta(days=1) if 0< x.hour < 8 else x.date())
    
    def get_daily_counts(self):
        
        daily_case_counts = self.df.groupby(['Ekip No', 'ihbar_date']).size().reset_index(name='daily_case_count')
        
        return daily_case_counts
    
    def get_mean_daily_case_count(self):
        """
        Returns the mean daily case count for each team.
        """
        self.daily_mean_case_counts= self.get_daily_counts().groupby('Ekip No')['daily_case_count'].mean().rename('mean_daily_case_count')
        
        return self.daily_mean_case_counts
    
    def team_population_densities(self):
        
        df_district_case_counts =self.df.groupby(['District', 'Ekip No']).agg({'case_count':'sum', 'District Population Density':'mean'}).reset_index().sort_values(by=['District', 'case_count'], ascending=[True, False])
        df_district_case_counts['case_count_percentage'] = df_district_case_counts.groupby('District')['case_count'].transform(lambda x: x / x.sum() * 100)
        df_district_case_counts['teams_population_density'] = df_district_case_counts['District Population Density'] / 100 * df_district_case_counts['case_count_percentage']
        self.team_population_densities= df_district_case_counts.groupby(['Ekip No']).agg({'case_count': 'sum', 'teams_population_density': 'sum'}).reset_index().sort_values(by='teams_population_density', ascending=False)

        return self.team_population_densities
    
    """def get_team_population_density(self):
        
        #Returns the population density for each team.
        
        team_population_density = self.df.groupby('Ekip No')['teams_population_density'].mean().rename('teams_population_density')

        return team_population_density"""
    
    def convert_data(self):
        
        self.df= self.create_columns()
        self.df= self.convert_dataframe()
        
        #self.df['ihbar_date'] = pd.to_datetime(self.df['İhbar/Çağrı Tarih Saat']).dt.date
        self.df['ihbar_date'] = self.get_chief_day(self.df['İhbar/Çağrı Tarih Saat'])
    
class DataScorer:
    def __init__(self, df, save_path, team_population_densities, mean_daily_case_counts):
        
        self.df = df
        self.save_path = save_path
        
        self.team_population_densities = team_population_densities
        self.mean_daily_case_counts = mean_daily_case_counts
    
    def get_last_year(self):
        
        """
        Returns the last year of the dataset.
        """
        if self.save_path == LAST_YEAR_SAVE_PATH:
            last_year = self.df['ihbar_date'] >= (pd.to_datetime(self.df['ihbar_date'].max()) - pd.DateOffset(years=1)).date()
        
            return self.df[last_year]
        else:
            return self.df
    
    def get_weights(self):
        
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
        
        return column_weights

    def age_score(self, age):
        try:
            age = int(age)
            return age
        except:
            return 32.7
        
    def cagri_score(self, val):
        high_impact = ["Terör", "Trafik Kazası", "Yaralama", "Beyaz Kod Sağlık Personeline Şiddet"]
        med_impact = ["Medikal", "Diğer Kazalar", "İntihar"]
        if val in high_impact:
            return 100
        elif val in med_impact:
            return 75
        else:
            return 25
    
    def sonuc_score(self, val):
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
    
    def tansiyon_score(self, val):
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
    
    def glukoz_score(self, val):
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
        
    def ates_score(self, val):
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
        
    def spo2_score(self, val):
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
        
    def solunum_score(self, val):
        try:
            v = float(val)
            if v < 5 or v > 40:
                return 100
            elif 5 <= v < 10 or 30 < v <= 40:
                return 75
            elif 10 <= v < 20 or 24 < v <= 30:
                return 50
            else:  # 12-24
                return 25
        except:
            return 25
        
    def nabiz_deg_score(self, val):
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
        
    def cinsiyet_score(self, val):
        
        if pd.isna(val):
            return 75
        if isinstance(val, str):
            val = val.strip().upper()
        if val not in ['KADIN', 'ERKEK']:
            return 75
        
        if val == 'KADIN':
            return 50
        elif val == 'ERKEK':
            return 100
        else:
            return 75  # Default score if not recognized
    
    def yenidogan_score(self, val):
        
        if pd.isna(val):
            return 25
        if val == 'Yeni Doğan':
            return 100
        else:
            return 25
        
    def adli_vaka_score(self, val):
        
        if pd.isna(val):  
            return 25
        if val == 'Adli Vaka':
            return 100
    
    def triage_score(self, val):
        
        triage_scores = {
            'Kırmızı': 100,
            'Sarı': 75,
            'Yeşil': 50
        }
        return triage_scores.get(val, 10)  # Default to 10 if not found
    
    def bilinç_score(self, val):
        
        bilinc_map = {
            "Koma": 100, "Semikoma": 100, "Kapalı": 100, "Sedatize": 100,
            "Bulanık": 75, "Konfüze": 75, "Açık": 50}
        
        return bilinc_map.get(val,25)
        
    def pulse_type_score(self, val):
        
        nabiz_map = {
            "Alınmıyor": 100, "Filiform": 100, "Aritmik": 75, "Düzenli": 50
        }
        
        return nabiz_map.get(val, 25) # Default to 25 if not found
    
    def logarithmic_score(self, value, base=10, scale=1):
        if value <= 0:
            return 0
        return scale * np.log(value + 1) / np.log(base)
    
    def robust_z_score(self, series):
        median = np.nanmedian(series)
        mad = np.nanmedian(np.abs(series - median))
        
        if mad == 0:
            return pd.Series([0]*len(series), index=series.index)
        
        return (series - median) / mad
    
    def score_data(self):
        # Grouping and calculating scores for each team by season and day
        for season in self.df['season'].unique():
            for day in self.df['day'].unique():
                subset = self.df[(self.df['season'] == season) & (self.df['day'] == day)]
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
                    
                    df_team_grouped = df_team_grouped.merge(self.mean_daily_case_counts, left_index=True, right_index=True)
                    df_team_grouped = df_team_grouped.merge(self.team_population_densities,  on='Ekip No', how='left', suffixes=('', '_team_density'))
                    
                    for col in df_team_grouped.columns[1:]:
                        new_col = col + '_logarithmic_score'
                        df_team_grouped[new_col]= df_team_grouped[col].apply(lambda x: self.logarithmic_score(x, base=10, scale=1))

                    for col in df_team_grouped.columns:
                        if col.endswith('_logarithmic_score'):
                            new_col= col + '_MinMax_score'
                            df_team_grouped[new_col] = scaler.fit_transform(df_team_grouped[[col]]) * self.get_weights()[col.replace('_logarithmic_score', '')]
                            df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
                        
                    for col in df_team_grouped.columns:
                        if col.endswith('_MinMax_score'):
                            new_col = col + '_z_score'
                            df_team_grouped[new_col] = self.robust_z_score(df_team_grouped[col])
                            df_team_grouped.insert(df_team_grouped.columns.get_loc(col) + 1, new_col, df_team_grouped.pop(new_col))
                    
                    df_team_grouped['total_score']= df_team_grouped[[col for col in df_team_grouped.columns if col.endswith('_MinMax_score')]].sum(axis=1)
                    df_team_grouped['strategic_score']= df_team_grouped['total_score'] / df_team_grouped['mean_daily_case_count']
                    df_team_grouped['total_score']= df_team_grouped['total_score'] * df_team_grouped['mean_daily_case_count']* df_team_grouped['sonuc_score']
                    #df_team_grouped['strategic_total_score']= df_team_grouped[[col for col in df_team_grouped.columns if not col.endswith('_logarithmic_score') and col != 'total_score' and col !='mean_daily_case_count' and col!= 'Ekip No' and col != 'teams_population_density' or col == 'case_count_logarithmic_score' or col == 'teams_population_density_logarithmic_score']].sum(axis=1)
                    
                    df_team_grouped['total_score_z']= self.robust_z_score(df_team_grouped['total_score'])
                    df_team_grouped['strategic_score_z']= self.robust_z_score(df_team_grouped['strategic_score'])

                    df_team_grouped['station_expendable']= df_team_grouped.apply(lambda x: 0 if x['total_score_z'] < 0 and x['strategic_score_z'] < -1.5 else 1 if x['total_score_z'] < 1 and x['strategic_score_z'] < 0 else 2 if x['total_score_z'] < 1.5 and x['strategic_score_z'] < 0.5 else 3 if x['total_score_z'] < 2 and x['strategic_score_z'] < 1 else 4 if x['total_score_z'] < 2.5 and x['strategic_score_z'] < 1.5 else 5, axis=1)

                    df_team_grouped= df_team_grouped.sort_values(by='total_score_z', ascending=False).reset_index()

                    df_team_grouped.reset_index(drop=True).to_excel(rf"{self.save_path}\{season}_{day}_total scores.xlsx")
                    logging.info(f"Scores for {season} {day} saved to {self.save_path}")
                    
        return logging.info(f"All Scores calculated and saved to {self.save_path}")
    
    def datascorer(self):
        
        self.df= self.get_last_year()
        logging.info("The shape of the DataFrame is: %s", self.df.shape)
        
        try:
            logging.info("Calculating cagri nedeni score...")
            self.df['cagri_nedeni_score'] = self.df['Çağrı Nedeni'].apply(self.cagri_score)
            
            logging.info("calculating triage score...")
            self.df['triaj_score'] = self.df['Triaj'].apply(self.triage_score)
            
            logging.info("Calculating Yas score...")
            self.df['yas_score'] = self.df['Yaş'].apply(self.age_score)
            
            logging.info(f"Calculating cinsiyet score...")
            self.df['cinsiyet_score'] = self.df['Cinsiyet'].apply(self.cinsiyet_score)
            
            logging.info("Calculating yeni dogan score...")
            self.df['yeni_dogan_score'] = self.df['Yeni Doğan'].apply(self.yenidogan_score)
            
            logging.info("Calculating adli vaka score...")
            self.df['adli_vaka_score'] = self.df['Adli Vaka'].apply(self.adli_vaka_score)
            
            logging.info("Calculating sonuc score...")
            self.df['sonuc_score'] = self.df['Sonuç'].apply(self.sonuc_score)
            
            logging.info("Calculating bilinc score...")
            self.df['bilinc_score'] = self.df['Bilinç'].apply(self.bilinç_score)
            
            logging.info("Calculating nabiz score...")
            self.df['nabiz_score'] = self.df['Nabız'].apply(self.pulse_type_score)
            
            logging.info("Calculating tansiyon score...")
            self.df['tansiyon_score'] = self.df['Tansiyon'].apply(self.tansiyon_score)
            
            logging.info("Calculating glukoz score...")
            self.df['glukoz_score'] = self.df['Glukoz'].apply(self.glukoz_score)
            
            logging.info("Calculating ates score...")
            self.df['ates_score'] = self.df['Ateş'].apply(self.ates_score)
            
            logging.info("Calculating spo2 score...")
            self.df['spo2_score'] = self.df['SPO2'].apply(self.spo2_score)
            
            logging.info("Calculating solunum degeri score...")
            self.df['solunum_score'] = self.df['Solunum Değeri'].apply(self.solunum_score)
            
            logging.info("Calculating nabiz score...")
            self.df['nabiz_deger_score'] = self.df['Nabız Değeri'].apply(self.nabiz_deg_score)
            
        
        except KeyError as e:
            raise KeyError(f"KeyError: {e}. Please ensure all necessary columns are present in the DataFrame.")
            
        self.score_data()
        logging.info(f"Data scoring completed and saved to {self.save_path}")
        
        return self.df
    
    
def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    creator = DataCreator(RAW_DATA_PATH, districts_data, neighbourhoods_gdf)
    data= creator.read_files()
    
    # Create DataConverter instance
    converter = DataConverter(population_density, icd_diagnoses, data)

    # Convert data
    converter.convert_data()

    team_population_densities = converter.team_population_densities()
    logging.info(f"First 5 Team Population Densities:\n{team_population_densities.head(5)}")
    mean_daily_case_counts = converter.get_mean_daily_case_count()
    logging.info(f"First 5 Mean Daily Case Counts:\n{mean_daily_case_counts.head(5)}")
    
    # Create DataScorer instance
    scorer = DataScorer(converter.df, OVERALL_SAVE_PATH,team_population_densities,  mean_daily_case_counts)

    # Score data
    scorer.datascorer()

if __name__ == '__main__':
    # Load data
    population_density = pd.read_csv(POPULATION_DENSITY_PATH)
    icd_diagnoses = pd.read_csv(ICD_DIAGNOSES_PATH)
    
    # Load districts and neighbourhoods data
    with open(DISTRICTS_DATA_PATH, 'r') as f:
        districts_data = json.load(f)
    
    neighbourhoods_gdf = gpd.read_file(NEIGHBOURHOODS_GDF_PATH)
    
    main()
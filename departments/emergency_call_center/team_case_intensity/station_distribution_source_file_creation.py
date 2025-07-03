import pandas as pd
import numpy as np

import json
import datetime as dt

import logging

SOURCE_DATA_NAME = 'data.json'

class DataCreator:
    
    def __init__(self, shift_list, scoring, df_signs):
        
        self.shift_list = shift_list
        self.scoring = scoring
        self.df_signs= df_signs
        date= dt.datetime.now()
        self.date= date
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def get_day_name(self):
        
        """
        Returns the current day name and season name.
        Day name is in uppercase (e.g., 'MONDAY').
        Season name is in uppercase (e.g., 'SUMMER').
        """
        # Get day name
        day_name = self.date.strftime('%A') # e.g., 'WEDNESDAY'

        return day_name
    
    # Get season name
    def get_season(self):
        Y = self.date.year
        seasons = [
            ('Winter', dt.datetime(Y, 1, 1), dt.datetime(Y, 3, 21)),
            ('Spring', dt.datetime(Y, 3, 21), dt.datetime(Y, 6, 21)),
            ('Summer', dt.datetime(Y, 6, 21), dt.datetime(Y, 9, 23)),
            ('Autumn', dt.datetime(Y, 9, 23), dt.datetime(Y, 12, 21)),
            ('Winter', dt.datetime(Y, 12, 21), dt.datetime(Y+1, 1, 1))
        ]
        for season, start, end in seasons:
            if start <= self.date <= end:
                return season
        return 'UNKNOWN'
        
    
    def get_scoring_file_name(self):
        """
        Returns the name of the scoring file based on the current date.
        The file name is formatted as 'scoring_YYYYMMDD.csv'.
        """
        season = self.get_season()
        day_name = self.get_day_name()
        
        return f"{season}_{day_name}_total scores.xlsx"
    
    
    def staff_shift_file_cleaning(self):

        # WARNING: READ YOUR EXCEL FILE WITH header=None , F.e = pd.read_excel("df.xlsx", header=None)

        # Identify station rows: col1 has value, cols 2–4 are empty
        station_mask = self.shift_list[1].notna() & self.shift_list[[2, 3, 4]].isna().all(axis=1)
        self.shift_list["RawStation"] = self.shift_list[1].where(station_mask)

        # Forward fill station names
        logging.info(f"station columns are {self.shift_list.columns}")
        
        self.shift_list["İstasyon"] = self.shift_list["RawStation"].ffill()
        self.shift_list.columns= self.shift_list.loc[self.shift_list[self.shift_list[1] == 'İsim'].index[0]]
        self.shift_list= self.shift_list[[col for col in self.shift_list.columns if pd.notna(col)]]
        self.shift_list.rename(columns={self.shift_list.columns[-1]: 'İstasyon'}, inplace=True)
        
        self.shift_list= self.shift_list[(self.shift_list['Kimlik No'].notna()) & (self.shift_list['Kimlik No'] != 'Kimlik No')]
        self.shift_list['Kimlik No']= self.shift_list['Kimlik No'].astype(str).str.strip()
        self.shift_list['İsim Soyisim']= self.shift_list['İsim'].astype(str).str.strip() + ' ' + self.shift_list['Soyisim'].astype(str).str.strip()
        self.shift_list= self.shift_list[(self.shift_list['Başlangıç Tarihi'].notna()) & ((pd.to_datetime(self.shift_list['Bitiş Tarihi'], format= 'mixed') - pd.to_datetime(self.shift_list['Başlangıç Tarihi'], format='mixed')) > pd.Timedelta(hours=8))]
                
        cleaned = self.shift_list['İstasyon'].apply(self.clean_team_codes)
        self.shift_list['İstasyon'] = cleaned.apply(lambda x: x[0] if isinstance(x, tuple) else pd.NA)
        self.shift_list['region'] = cleaned.apply(lambda x: x[1] if isinstance(x, tuple) else pd.NA)
        
        self.shift_list= self.shift_list[self.shift_list['İstasyon'].notna()]
        self.shift_list= self.shift_list[pd.to_datetime(self.shift_list['Başlangıç Tarihi'], format='mixed').dt.hour < 11]
        
        self.shift_list['roles']= self.assign_roles()

        return self.shift_list
    
    def clean_signs(self):
        self.df_signs= self.df_signs[self.df_signs[2].notna()]
        self.df_signs.dropna(how= 'all', inplace=True)
        self.df_signs.columns= self.df_signs.iloc[0]
        self.df_signs= self.df_signs[1:]
        self.df_signs['Adı Soyadı']= self.df_signs['Adı Soyadı'].astype(str).str.strip()
        
        try:
            self.df_signs= self.df_signs[self.df_signs['Başlama Tarihi'].notna()]
        except KeyError:
            logging.warning("Column 'Başlama Tarihi' not found in df_signs.\n__________________")
            logging.warning("Existing columns: ",self.df_signs.columns, '\n__________________\n')
            
            new_col_name = input("Enter the new column name: ")
            self.df_signs = self.df_signs[self.df_signs[new_col_name].notna()]
    
    def scoring_type(self):
        return self.scoring['total_score_z'].astype('float32')
    
    def clean_team_codes(self, key):
        
        """Cleans the team codes DataFrame by renaming columns and filtering rows."""
        
        distinct_codes = {
            'BAYRAMP': 'BYR',
            'BEYOĞLU': 'BEY',
            'BEŞİKTAŞ': 'BEŞ',
            'EYÜP': 'EYP',
            'FATİH': 'FTH',
            'GAZİOSMANPAŞA': 'GOP',
            'GÜNGÖREN': 'GNG',
            'KAĞITHANE': 'KĞT',
            'SARIYER': 'SRY',
            'SLTGAZİ': 'STG',
            'ŞİŞLİ': 'ŞİŞ',
            'Z.BURNU': 'ZTB',
            'ARNKÖY': 'ARN',
            'AVCILAR':'AVC',
            'B.EVLER':'BHC',
            'B.ÇEKMECE':'BÇK',
            'BAKIRKÖY':'BKR',
            'BAĞCILAR':'BAG',
            'BEYDÜZÜ':'BDZ',
            'BŞKŞEHİR':'BŞK',
            'ESENLER':'ESN',
            'ESENYURT':'ESY',
            'K.ÇEKMECE':'KÇK',
            'SİLİVRİ':'SLV',
            'ÇATALCA':'ÇTL'
            # Add other distinct codes as needed
        }
        
        k = key.split(' ')[0]
        num= key.split(' ')[1]
        
        if num.startswith('0'):
            num = num[1:]
        
        key= k+num
        
        if k in distinct_codes.keys():
            v = distinct_codes[k]
            region= self.assign_region(v)
            key= key.replace(k, v)
        else:
            return pd.NA
        
        return key.strip(), region
    
    def assign_region(self, key):
        """Assigns a region based on the key."""
        regions = {
            'ARN':'Arnavutköy',
            'AVC':'Avcılar',
            'BAG':'Bağcılar',
            'BKR':'Bakırköy',
            'BEŞ':'Beşiktaş',
            'BEY':'Beyoğlu',
            'BÇK':'Büyükçekmece',
            'BDZ':'Beylikdüzü',
            'BHC':'Bahçelievler',
            'BKR':'Bakırköy',
            'BŞK':'Başakşehir',
            'BYR':'Bayrampaşa',
            'ÇTL':'Çatalca',
            'ESN':'Esenler',
            'ESY':'Esenyurt',
            'EYP':'Eyüpsultan',
            'FTH':'Fatih',
            'GNG':'Güngören',
            'GOP':'Gaziosmanpaşa',
            'KÇK':'Küçükçekmece',
            'KĞT':'Kağıthane',
            'SLV':'Silivri',
            'SRY':'Sarıyer',
            'STG':'Sultangazi',
            'ŞİŞ':'Şişli',
            'ZTB':'Zeytinburnu'
            # Add other regions as needed
        }
        return regions.get(key, pd.NA)
    
    def assign_roles(self):
        """
        Assigns roles based on the 'Görev' column in the shift list.
        Returns a DataFrame with roles assigned.
        """
        
        assignment_mask = np.select(
            [
                self.shift_list["Görev"] == "Sürücü",
                (self.shift_list["Görev"]=="Ekip Sorumlusu") | (self.shift_list['Görev']=="Yardımcı Sağlık Personeli")
            ],
            [
                "driver",
                "medic"
            ],
            default=pd.NA
        )
        return assignment_mask
    
    def get_json_data(self):
        """
        Returns a JSON string with the cleaned shift data.
        """
        json_input = '''
            {
                "stations": [],
                "neighboringRegions" : {
                    "Adalar": ["Kartal", "Pendik"],
                    "Arnavutköy": ["Çatalca", "Esenler", "Başakşehir", "Eyüpsultan"],
                    "Ataşehir": ["Üsküdar", "Kadıköy", "Maltepe", "Ümraniye"],
                    "Avcılar": ["Küçükçekmece", "Bağcılar", "Başakşehir"],
                    "Bağcılar": ["Küçükçekmece", "Bahçelievler", "Güngören", "Esenler", "Avcılar"],
                    "Bahçelievler": ["Bağcılar", "Bakırköy", "Güngören"],
                    "Bakırköy": ["Bahçelievler", "Güngören", "Küçükçekmece", "Esenyurt"],
                    "Başakşehir": ["Arnavutköy", "Eyüpsultan", "Esenler", "Avcılar", "Küçükçekmece"],
                    "Bayrampaşa": ["Gaziosmanpaşa", "Eyüpsultan", "Fatih", "Şişli"],
                    "Beşiktaş": ["Şişli", "Beyoğlu", "Sarıyer", "Kağıthane"],
                    "Beykoz": ["Ümraniye", "Çekmeköy", "Sancaktepe", "Üsküdar"],
                    "Beylikdüzü": ["Büyükçekmece", "Esenyurt", "Avcılar"],
                    "Beyoğlu": ["Şişli", "Kağıthane", "Fatih", "Beşiktaş", "Eyüpsultan"],
                    "Büyükçekmece": ["Çatalca", "Silivri", "Esenyurt", "Beylikdüzü"],
                    "Çatalca": ["Silivri", "Büyükçekmece", "Arnavutköy"],
                    "Çekmeköy": ["Ümraniye", "Beykoz", "Üsküdar", "Sancaktepe"],
                    "Esenler": ["Bağcılar", "Güngören", "Bakırköy", "Başakşehir", "Gaziosmanpaşa"],
                    "Esenyurt": ["Küçükçekmece", "Avcılar", "Bakırköy", "Beylikdüzü", "Büyükçekmece"],
                    "Eyüpsultan": ["Sarıyer", "Kağıthane", "Beyoğlu", "Gaziosmanpaşa", "Bayrampaşa", "Fatih", "Sultangazi", "Başakşehir", "Arnavutköy"],
                    "Fatih": ["Beyoğlu", "Şişli", "Eminönü", "Esenler"],
                    "Gaziosmanpaşa": ["Eyüpsultan", "Sultangazi", "Esenler", "Bayrampaşa"],
                    "Güngören": ["Bağcılar", "Bahçelievler", "Bakırköy", "Esenler", "Zeytinburnu"],
                    "Kadıköy": ["Ümraniye", "Ataşehir", "Maltepe", "Kartal", "Sancaktepe"],
                    "Kağıthane": ["Şişli", "Beşiktaş", "Beyoğlu", "Eyüpsultan", "Sarıyer", "Sultangazi"],
                    "Kartal": ["Maltepe", "Pendik", "Tuzla", "Adalar"],
                    "Küçükçekmece": ["Avcılar", "Bağcılar", "Bakırköy", "Esenyurt", "Başakşehir"],
                    "Maltepe": ["Kadıköy", "Kartal", "Pendik", "Sancaktepe", "Ümraniye"],
                    "Pendik": ["Kartal", "Tuzla", "Sancaktepe", "Maltepe", "Ümraniye"],
                    "Sancaktepe": ["Çekmeköy", "Ümraniye", "Kadıköy", "Maltepe", "Pendik", "Tuzla", "Kartal"],
                    "Sarıyer": ["Eyüpsultan", "Kağıthane", "Beşiktaş", "Beykoz", "Şile"],
                    "Silivri": ["Çatalca", "Büyükçekmece"],
                    "Sultanbeyli": ["Pendik", "Kartal", "Sancaktepe", "Ümraniye"],
                    "Sultangazi": ["Eyüpsultan", "Gaziosmanpaşa", "Kağıthane"],
                    "Şile": ["Sarıyer"],
                    "Şişli": ["Beyoğlu", "Beşiktaş", "Kağıthane", "Bayrampaşa", "Fatih"],
                    "Tuzla": ["Pendik", "Kartal"],
                    "Ümraniye": ["Üsküdar","Ataşehir", "Kadıköy", "Maltepe", "Sancaktepe", "Çekmeköy",  "Beykoz"],
                    "Üsküdar": ["Ümraniye", "Çekmeköy", "Beykoz", "Kadıköy", "Ataşehir"],
                    "Zeytinburnu": ["Bakırköy", "Güngören", "Fatih", "Bayrampaşa"]
                },
                "maxRotationsPerPersonnel": 5
                }
            '''
        json_data = json.loads(json_input)
        
        return json_data
    
    
    def create_source_data(self):
        
        data= self.get_json_data()
        station_names= self.shift_list['İstasyon'].unique().tolist()
        station_names= [name for name in station_names if pd.notna(name) and name != 'BAG5' and name != 'BKR6' and name != 'ESY4' and name != 'KÇK6' and name != 'SLV2' and name != 'ZTB3']
        
        for station_name in station_names:
            df_assignments = self.shift_list[self.shift_list['İstasyon'] == station_name].copy()
            
            new_station = {
                'id': '',
                'region': '',
                'importance': '',
                'assignedPersonnel': [],
                'maxRotationCount': 5
            }
            
            new_station['id'] = station_name

            # Get region as string
            region_series = self.shift_list[self.shift_list['İstasyon'] == station_name]['region']
            
            if region_series.empty:
                logging.warning(f"Region for station {station_name} not found.")
            
            new_station['region'] = region_series.iloc[0] if not region_series.empty else ""

            # Get importance as float (fix here!)
            importance_series = self.scoring[self.scoring['Ekip No'] == station_name]['total_score_z'].astype('float32')
            if importance_series.empty:
                logging.warning(f"Importance for station {station_name} not found. Skipping assignment.")
                continue
            
            new_station['importance'] = float(importance_series.iloc[0]) if not importance_series.empty else 0.0
            if not isinstance(new_station['importance'], (int, float)):
                logging.error(f"Importance for station {station_name} is not a number: {new_station['importance']}")
                new_station['importance'] = 0.0
            
            logging.info(f"Processing station: {station_name}, Region: {new_station['region']}, Importance: {new_station['importance']}")
            
            added_worker_ids= []
            
            for i in range(len(df_assignments)):
                worker_id= df_assignments.iloc[i]['Kimlik No']
                
                new_personnel = {
                    'id': '',
                    'name': '',
                    'roles': [''],
                    'assignedFrom': '',
                    'homeStationId': '',
                    'negativeStations': [],
                    'preferredStations': [],
                    'rotationCount': 0
                }
                
                if worker_id  not in added_worker_ids:
                    added_worker_ids.append(df_assignments.iloc[i]['Kimlik No'])
                    new_personnel['id'] = str(worker_id)
                    new_personnel['name'] = str(df_assignments.iloc[i]['İsim Soyisim'])
                    new_personnel['roles'][0] = str(df_assignments.iloc[i]['roles'])
                    new_personnel['homeStationId'] = str(df_assignments.iloc[i]['İstasyon'])
                    new_personnel['assignedFrom']= str(df_assignments.iloc[i]['İstasyon'])
                else:
                    logging.warning(f"Worker id {worker_id} is already assigned in another station")
                    pass
                    
                new_station['assignedPersonnel'].append(new_personnel)
            
            data['stations'].append(new_station)
        return data
    
def main():
    
    creator = DataCreator(shift_list, scoring, df_signs)
    creator.staff_shift_file_cleaning()
    logging.info("Shift list cleaned successfully.")
    creator.clean_signs()
    logging.info("Signs cleaned successfully.")
    creator.scoring['total_score_z']= creator.scoring_type()
    source_data = creator.create_source_data()
    logging.info("Source data created successfully.")
    
    with open(rf'C:\Users\mkaya\OneDrive\Masaüstü\{SOURCE_DATA_NAME}', 'w', encoding='utf-8') as f:
        json.dump(source_data,f,ensure_ascii=False, indent=4)
    logging.info(f"Source data saved as {SOURCE_DATA_NAME} successfully.")

if __name__ == "__main__":
    
    shift_list = pd.read_excel(rf"C:\Users\mkaya\Downloads\Personel-Nöbet-Listesi (32).xls", header=None)
    df_signs = pd.read_excel(r"C:\Users\mkaya\Downloads\Personel-Imza-Defteri (9).xls", header=None)
    scoring_file_name = DataCreator(None, None, None).get_scoring_file_name()
    logging.info(f"Scoring file name: {scoring_file_name}")
    
    scoring = pd.read_excel(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\overall\{scoring_file_name}")
    
    main()
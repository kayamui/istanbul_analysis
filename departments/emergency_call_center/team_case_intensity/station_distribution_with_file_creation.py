import pandas as pd
import numpy as np

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from copy import deepcopy

import json

import datetime as dt

import logging

SOURCE_DATA_NAME = 'data.json'
STATION_MAX_ROTATION_COUNT = 100
MAX_ROTATIONS_COUNT_PER_PERSONNEL = 100
DEFAULT_IMPORTANCE = 1

class DataCreator:
    
    def __init__(self, shift_list, scoring, df_signs, driver_medic):
        
        self.shift_list = shift_list
        self.scoring = scoring
        self.df_signs= df_signs
        self.driver_medic= driver_medic
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
        self.shift_list['İsim Soyisim']= (self.shift_list['İsim'].astype(str).str.strip() + ' ' + self.shift_list['Soyisim'].astype(str).str.strip()).str.strip()
        self.shift_list= self.shift_list[(self.shift_list['Başlangıç Tarihi'].notna()) & ((pd.to_datetime(self.shift_list['Bitiş Tarihi'], format= 'mixed') - pd.to_datetime(self.shift_list['Başlangıç Tarihi'], format='mixed')) > pd.Timedelta(hours=8))]

        cleaned = self.shift_list['İstasyon'].apply(self.clean_team_codes)
        self.shift_list['İstasyon'] = cleaned.apply(lambda x: x[0] if isinstance(x, tuple) else pd.NA)
        self.shift_list['region'] = cleaned.apply(lambda x: x[1] if isinstance(x, tuple) else pd.NA)
        
        self.shift_list= self.shift_list[self.shift_list['İstasyon'].notna()]
        self.shift_list= self.shift_list[pd.to_datetime(self.shift_list['Başlangıç Tarihi'], format='mixed').dt.hour < 11]
        
        self.shift_list['Kimlik No']= self.shift_list['Kimlik No'].astype('int64', errors= 'ignore')
        self.shift_list= pd.merge(self.shift_list, self.driver_medic, left_on='Kimlik No',right_on='TC KİMLİK NO', how= 'left')
        
        self.shift_list['roles']= self.shift_list.apply(self.assign_roles, axis=1)
        
        self.shift_list= self.shift_list[self.shift_list['İsim Soyisim'].isin(self.df_signs['Adı Soyadı'].unique())]
        return self.shift_list
    
    def clean_driver_medic(self):
        self.driver_medic['AD SOYAD']= self.driver_medic['AD SOYAD'].astype(str).str.strip()
        self.driver_medic['TC KİMLİK NO']= self.driver_medic['TC KİMLİK NO'].astype('int64')

        return self.driver_medic
    
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
    
    def assign_roles(self,row):
        """
        Assigns roles based on the 'Görev' column in the shift list.
        Returns a DataFrame with roles assigned.
        """

        if row["Görev"] == "Sürücü":
            logging.info(f"Personel Adı: {row['İsim Soyisim']}, aktif görevde olduğu istasyon: {row['İstasyon']}, Sürücü rolü")
            return ["driver"]
        
        elif pd.notna(row["ASTE"]) and (row['Görev']=="Ekip Sorumlusu" or row['Görev']=="Yardımcı Sağlık Personeli"):
            logging.info(f"Personel Adı: {row['İsim Soyisim']}, aktif görevde olduğu istasyon: {row['İstasyon']}. Personelin görevi: {row['Görev']}, aste alma zamanı: {row['ASTE']}")
            return ["medic", "driver"]
        else:
            logging.info(f"Personel Adı: {row['İsim Soyisim']}, aktif görevde olduğu istasyon: {row['İstasyon']}. Sağlıkçının görevi {row['Görev']}")
            return ["medic"]
    
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
        station_names= [name for name in self.shift_list['İstasyon'].unique().tolist() if pd.notna(name) and name != 'BAG5' and name != 'BKR6' and name != 'ESY4' and name != 'KÇK6' and name != 'SLV2' and name != 'ZTB3']
        strategic_stations=["ÇTL1", "ÇTL2","ÇTL3","ÇTL4","ÇTL5"]
        
        for station_name in station_names:
            df_assignments = self.shift_list[self.shift_list['İstasyon'] == station_name].copy()
            
            new_station = {}
            
            new_station['id'] = station_name

            # Get region as string
            region_series = self.shift_list[self.shift_list['İstasyon'] == station_name]['region']
            
            if region_series.empty:
                logging.warning(f"Region for station {station_name} not found.")
            
            new_station['region'] = region_series.iloc[0] if not region_series.empty else ""

            # Get importance as float (fix here!)
            importance_series = self.scoring[self.scoring['Ekip No'] == station_name]['total_score_z'].astype('float32')
            
            new_station['importance'] = float(importance_series.iloc[0]) if not importance_series.empty else 0.0
            new_station['assignedPersonnel'] = []
            new_station['maxRotationCount'] = 5
            
            new_station['similar_stations'] = similarity_results[station_name] if station_name in similarity_results else []
            new_station['strategic'] = station_name in strategic_stations
            
            if new_station['strategic']:
                logging.info(f"Strategic station found: {station_name}, setting importance to 100")
                new_station['importance'] = 100
                
            logging.info(f"Processing station: {station_name}, Region: {new_station['region']}, Importance: {new_station['importance']}, Similar Stations: {new_station['similar_stations']}")
            
            added_worker_ids= []
            
            for i in range(len(df_assignments)):
                worker_id= df_assignments.iloc[i]['Kimlik No']
                
                new_personnel = {
                    'roles': [],
                }
                
                if worker_id  not in added_worker_ids:
                    added_worker_ids.append(df_assignments.iloc[i]['Kimlik No'])
                    new_personnel['id'] = str(worker_id)
                    new_personnel['name'] = str(df_assignments.iloc[i]['İsim Soyisim'])
                    new_personnel['roles']= df_assignments.iloc[i]['roles']
                    new_personnel['homeStationId'] = str(df_assignments.iloc[i]['İstasyon'])
                    new_personnel['negativeStations'] = []
                    new_personnel['preferredStations'] = []
                    new_personnel['assignedFrom']= str(df_assignments.iloc[i]['İstasyon'])
                else:
                    logging.warning(f"Worker id {worker_id} is already assigned in another station")
                    pass
                    
                new_station['assignedPersonnel'].append(new_personnel)
            
            data['stations'].append(new_station)
        return data

@dataclass
class Personnel:
    id: str
    name: str
    roles: List[str]
    home_station_id: str
    negative_stations: List[str]
    assigned_from: Optional[str] = None
    preferred_stations: List[str] = field(default_factory=list)
    rotation_count: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Personnel':
        return cls(
            id=data['id'],
            name=data['name'],
            roles=data['roles'],
            assigned_from=data.get('assignedFrom'),
            home_station_id=data['homeStationId'],
            negative_stations=data.get('negativeStations', []),
            preferred_stations=data.get('preferredStations', []),
            rotation_count=data.get('rotationCount', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'roles': self.roles,
            'assignedFrom': self.assigned_from,
            'homeStationId': self.home_station_id,
            'negativeStations': self.negative_stations,
            'preferredStations': self.preferred_stations,
            'rotationCount': self.rotation_count
        }

    def can_work_as(self, role: str) -> bool:
        return role in self.roles

    def can_work_at(self, station_id: str) -> bool:
        return station_id not in self.negative_stations

    def copy_with(self, assigned_from: Optional[str] = None, rotation_count: Optional[int] = None) -> 'Personnel':
        new_personnel = deepcopy(self)
        if assigned_from is not None:
            new_personnel.assigned_from = assigned_from
        if rotation_count is not None:
            new_personnel.rotation_count = rotation_count
        return new_personnel

@dataclass
class SimilarityResult:
    similar_ekip_no: str
    similarity_score: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimilarityResult':
        return cls(
            similar_ekip_no= data['similar_ekip_no'],
            similarity_score= data['similarity_score']
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'similar_ekip_no': self.similar_ekip_no,
            'similarity_score': self.similarity_score
        }

@dataclass
class Station:
    id: str
    region: str
    assigned_personnel: List[Personnel]
    importance: float = DEFAULT_IMPORTANCE
    max_rotation_count: int = STATION_MAX_ROTATION_COUNT
    similar_stations: List[SimilarityResult] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Station':
        return cls(
            id=data['id'],
            region=data['region'],
            importance=data.get('importance', DEFAULT_IMPORTANCE),
            max_rotation_count=data.get('maxRotationCount', STATION_MAX_ROTATION_COUNT),
            assigned_personnel=[Personnel.from_dict(p) for p in data['assignedPersonnel']],
            similar_stations=[SimilarityResult.from_dict(s) for s in data.get('similar_stations', [])]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'region': self.region,
            'importance': self.importance,
            'maxRotationCount': self.max_rotation_count,
            'assignedPersonnel': [p.to_dict() for p in self.assigned_personnel],
            'similar_stations': [s.to_dict() for s in self.similar_stations]
        }

    @property
    def medic_count(self) -> int:
        return len([p for p in self.assigned_personnel if p.can_work_as('medic')])

    @property
    def driver_count(self) -> int:
        return len([p for p in self.assigned_personnel if p.can_work_as('driver')])

    @property
    def is_fully_staffed(self) -> bool:
        return self.medic_count >= 2 and self.driver_count >= 1

    @property
    def has_excess_medics(self) -> bool:
        return self.medic_count > 2

    @property
    def has_excess_drivers(self) -> bool:
        return self.driver_count > 1

    def get_missing_roles(self) -> List[str]:
        missing = []
        if self.medic_count < 2:
            missing.append('medic')
        if self.driver_count < 1:
            missing.append('driver')
        return missing

    def get_excess_roles(self) -> List[str]:
        excess = []
        if self.has_excess_medics:
            excess.append('medic')
        if self.has_excess_drivers:
            excess.append('driver')
        return excess


@dataclass
class StationDistributionResult:
    open_stations: List[Station]
    closed_stations: List[Station]
    excess_stations: Dict[str, Dict[str, int]]
    personnel_moved: int
    logs: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'openStations': [s.to_dict() for s in self.open_stations],
            'closedStations': [s.to_dict() for s in self.closed_stations],
            'excessStations': self.excess_stations,
            'personnelMoved': self.personnel_moved,
            'logs': self.logs
        }


class StationDistributor:
    def __init__(self, stations: List[Station], neighboring_regions: Dict[str, List[str]], 
        max_rotations_per_personnel: int = MAX_ROTATIONS_COUNT_PER_PERSONNEL):
        self.stations = stations
        self.neighboring_regions = neighboring_regions
        self.max_rotations_per_personnel = max_rotations_per_personnel
        self.logs: List[str] = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StationDistributor':
        return cls(
            stations=[Station.from_dict(s) for s in data['stations']],
            neighboring_regions=data['neighboringRegions'],
            max_rotations_per_personnel=data.get('maxRotationsPerPersonnel', MAX_ROTATIONS_COUNT_PER_PERSONNEL)
        )

    def get_rotation_count_for_station(self, station: Station) -> int:
        return len([p for p in station.assigned_personnel if p.assigned_from is not None and p.assigned_from != station.id])

    def distribute_personnel(self) -> StationDistributionResult:
        # Sort stations by importance (highest first)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info('İstasyonlar önem derecesine göre sıralanıyor...')
        if not self.stations:
            logging.warning('İstasyon listesi boş, dağıtım yapılamayacak.')
            return StationDistributionResult([], [], {}, 0, [])
        #check if importance is numeric
        for s in self.stations:
            if not isinstance(s.importance, (int, float)):
                raise ValueError(f'İstasyonların  {s} önem dereceleri sayısal olmalıdır.')
        
        try:
            logging.info(f'İşlem başlatılıyor, toplam {len(self.stations)} istasyon var.')
            self.stations.sort(key=lambda s: s.importance, reverse=True)
        except TypeError as e:
            logging.error(f'İstasyonlar sıralanırken hata oluştu: {e} ')
            raise
        
        personnel_moved = 0

        # Identify stations with shortage and excess
        stations_with_shortage = [
            s for s in self.stations 
            if not s.is_fully_staffed
        ]        
        stations_with_excess = [s for s in self.stations if s.has_excess_medics or s.has_excess_drivers]
        
        shortage_ids = {s.id for s in stations_with_shortage}
        boost_history= dict()
        for st in stations_with_shortage:
            for sim in st.similar_stations:
                if sim.similar_ekip_no in shortage_ids:
                    if sim.similar_ekip_no not in boost_history:
                        boost_history[sim.similar_ekip_no]= []
                    boost = abs(st.importance) * sim.similarity_score
                    
                    if boost > 0.1:
                        boost_history[sim.similar_ekip_no].append(boost)
                    else:
                        continue
                    
                    st.importance += boost
                    self.logs.append(
                        f"{st.id} importance += {boost:.2f} "
                        f"(because it’s similar to {sim.similar_ekip_no})"
                    )
            stations_with_shortage.sort(key=lambda s: s.importance, reverse=True)

        # Dynamic distribution for shortage stations
        while stations_with_shortage:
            shortage_station = stations_with_shortage[0]

            # Is station still short-staffed?
            if shortage_station.is_fully_staffed:
                stations_with_shortage.pop(0)
                continue

            # Check rotation limit
            current_rotations = self.get_rotation_count_for_station(shortage_station)
            remaining_rotations = shortage_station.max_rotation_count - current_rotations
            if remaining_rotations <= 0:
                self.logs.append(f'{shortage_station.id} rotasyon limitine ulaştı ({shortage_station.max_rotation_count}).')
                stations_with_shortage.pop(0)
                continue

            # Find personnel for missing roles
            missing_roles = shortage_station.get_missing_roles()
            station_progress = False

            for role in missing_roles:
                if remaining_rotations <= 0:
                    self.logs.append(f'{shortage_station.id} için rotasyon limiti doldu.')
                    break

                moved_person = self.find_personnel_for_role(role, shortage_station.id, shortage_station.region, stations_with_excess)

                # If no excess personnel, search from any station (including shortage stations, excluding fully staffed)
                if moved_person is None:
                    moved_person = self.find_personnel_from_any_station(role, shortage_station.id, shortage_station.region)

                if moved_person is None:
                    continue

                # Find original station of personnel
                origin_station = None
                for s in self.stations:
                    if any(p.id == moved_person.id for p in s.assigned_personnel):
                        origin_station = s
                        break

                if origin_station is None:
                    raise Exception(f'Orijinal istasyon bulunamadı: {moved_person.id}')

                # Move personnel
                origin_station.assigned_personnel = [p for p in origin_station.assigned_personnel if p.id != moved_person.id]
                updated_person = moved_person.copy_with(
                    assigned_from=origin_station.id,
                    rotation_count=moved_person.rotation_count + 1
                )
                shortage_station.assigned_personnel.append(updated_person)

                personnel_moved += 1
                remaining_rotations -= 1
                station_progress = True
                #self.logs.append(f'{updated_person.name} ({role}) {origin_station.id} -> {shortage_station.id}')

                # Check source station personnel count
                if len(origin_station.assigned_personnel) == 1:
                    self.logs.append(f'{origin_station.id} istasyonunda sadece 1 personel kaldı, istasyon kapatılıyor.')
                    
                    # Distribute remaining personnel to other stations
                    remaining_person = origin_station.assigned_personnel[0]
                    new_station = self.distribute_remaining_personnel(remaining_person, origin_station.id, origin_station.region)
                    if new_station is not None:
                        origin_station.assigned_personnel.clear()
                        updated_remaining_person = remaining_person.copy_with(
                            assigned_from=origin_station.id,
                            rotation_count=remaining_person.rotation_count + 1
                        )
                        new_station.assigned_personnel.append(updated_remaining_person)
                        personnel_moved += 1
                        self.logs.append(f'{remaining_person.name} ({", ".join(remaining_person.roles)}) {origin_station.id} -> {new_station.id}')

                # Update lists
                stations_with_excess = [s for s in self.stations if s.has_excess_medics or s.has_excess_drivers]
                stations_with_shortage = [s for s in self.stations if not s.is_fully_staffed and len(s.assigned_personnel) > 1]
                for s in stations_with_shortage:
                    if s.id in boost_history:
                        boosts = boost_history[s.id]
                        previous_importance = s.importance
                        if boosts:
                            s.importance -= sum(boosts)
                            self.logs.append(f"{s.id} {previous_importance:.2f} -= {sum(boosts):.2f}  => {s.importance:.2f} (boost history: {boosts})")
                        else:
                            self.logs.append(f"{s.id} importance remains unchanged (no boosts)")
                
                boost_history.clear()
                
                # Recalculate importance for shortage stations
                for st in stations_with_shortage:
                    for sim in st.similar_stations:
                        if sim.similar_ekip_no in shortage_ids:
                            if sim.similar_ekip_no not in boost_history:
                                boost_history[sim.similar_ekip_no]= []
                            boost = abs(st.importance) * sim.similarity_score
                            
                            if boost > 0.1:
                                boost_history[sim.similar_ekip_no].append(boost)
                            else:
                                continue
                            
                            st.importance += boost
                            self.logs.append(
                                f"{st.id} importance += {boost:.2f} "
                                f"(because it’s similar to {sim.similar_ekip_no})"
                            )
                # Sort again by importance
                stations_with_shortage.sort(key=lambda s: s.importance, reverse=True)

            #If no progress for this station, remove from list
            if not station_progress:
                stations_with_shortage.pop(0)

        # Identify stations with excess personnel
        excess_stations = {}
        for station in self.stations:
            excess_roles = station.get_excess_roles()
            if excess_roles:
                excess_details = {}
                if station.has_excess_medics:
                    excess_details['medic'] = station.medic_count - 2
                if station.has_excess_drivers:
                    excess_details['driver'] = station.driver_count - 1
                excess_stations[station.id] = excess_details
                self.logs.append(f'{station.id} istasyonunda fazla personel: {", ".join([f"{v} {k}" for k, v in excess_details.items()])}')
        
        # Prepare results
        open_stations = [s for s in self.stations if s.is_fully_staffed]
        closed_stations = [s for s in self.stations if not s.is_fully_staffed]
        logging.info(f'Kapanan istasyonlar: {closed_stations}')

        return StationDistributionResult(
            open_stations=open_stations,
            closed_stations=closed_stations,
            excess_stations=excess_stations,
            personnel_moved=personnel_moved,
            logs=self.logs
        )

    def find_personnel_for_role(self, role: str, target_station_id: str, target_region: str, excess_stations: List[Station]) -> Optional[Personnel]:
        # 1. Same region
        same_region_personnel = self._find_in_region(role, target_station_id, target_region, excess_stations)
        if same_region_personnel is not None:
            return same_region_personnel

        # 2. Neighboring regions
        neighbor_personnel = self._find_in_neighbor_regions(role, target_station_id, target_region, excess_stations)
        if neighbor_personnel is not None:
            return neighbor_personnel

        # 3. Other regions
        return self._find_in_any_region(role, target_station_id, excess_stations)

    def find_personnel_from_any_station(self, role: str, target_station_id: str, target_region: str) -> Optional[Personnel]:
        # 1. Same region
        same_region_personnel = self._find_in_region_from_any_station(role, target_station_id, target_region)
        if same_region_personnel is not None:
            return same_region_personnel

        # 2. Neighboring regions
        neighbor_personnel = self._find_in_neighbor_regions_from_any_station(role, target_station_id, target_region)
        if neighbor_personnel is not None:
            return neighbor_personnel

        # 3. Other regions
        return self._find_in_any_region_from_any_station(role, target_station_id)

    def distribute_remaining_personnel(self, person: Personnel, origin_station_id: str, origin_region: str) -> Optional[Station]:
        # 1. Same region
        same_region_station = self._find_station_in_region(person, origin_station_id, origin_region)
        if same_region_station is not None:
            return same_region_station

        # 2. Neighboring regions
        neighbor_region_station = self._find_station_in_neighbor_regions(person, origin_station_id, origin_region)
        if neighbor_region_station is not None:
            return neighbor_region_station

        # 3. Other regions
        return self._find_station_in_any_region(person, origin_station_id)

    def _find_station_in_region(self, person: Personnel, origin_station_id: str, region: str) -> Optional[Station]:
        for role in person.roles:
            shortage_stations = [s for s in self.stations 
                               if s.region == region and not s.is_fully_staffed and s.id != origin_station_id 
                               and role in s.get_missing_roles()]
            shortage_stations.sort(key=lambda s: s.importance, reverse=True)
            
            # Start from most important stations
            for station in shortage_stations:
                current_rotations = self.get_rotation_count_for_station(station)
                if current_rotations >= station.max_rotation_count:
                    continue
                if not person.can_work_at(station.id) or person.rotation_count >= self.max_rotations_per_personnel:
                    continue
                return station
        return None

    def _find_station_in_neighbor_regions(self, person: Personnel, origin_station_id: str, origin_region: str) -> Optional[Station]:
        neighbors = self.neighboring_regions.get(origin_region, [])
        for neighbor in neighbors:
            station = self._find_station_in_region(person, origin_station_id, neighbor)
            if station is not None:
                return station
        return None

    def _find_station_in_any_region(self, person: Personnel, origin_station_id: str) -> Optional[Station]:
        for role in person.roles:
            shortage_stations = [s for s in self.stations 
                               if not s.is_fully_staffed and s.id != origin_station_id 
                               and role in s.get_missing_roles()]
            shortage_stations.sort(key=lambda s: s.importance, reverse=True)
            
            for station in shortage_stations:
                current_rotations = self.get_rotation_count_for_station(station)
                if current_rotations >= station.max_rotation_count:
                    continue
                if not person.can_work_at(station.id) or person.rotation_count >= self.max_rotations_per_personnel:
                    continue
                return station
        return None

    def _find_in_region(self, role: str, target_station_id: str, region: str, excess_stations: List[Station]) -> Optional[Personnel]:
        region_stations = [s for s in excess_stations if s.region == region]
        for station in region_stations:
            personnel = self._find_suitable_personnel(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_in_neighbor_regions(self, role: str, target_station_id: str, target_region: str, excess_stations: List[Station]) -> Optional[Personnel]:
        neighbors = self.neighboring_regions.get(target_region, [])
        for neighbor in neighbors:
            personnel = self._find_in_region(role, target_station_id, neighbor, excess_stations)
            if personnel is not None:
                return personnel
        return None

    def _find_in_any_region(self, role: str, target_station_id: str, excess_stations: List[Station]) -> Optional[Personnel]:
        for station in excess_stations:
            personnel = self._find_suitable_personnel(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_in_region_from_any_station(self, role: str, target_station_id: str, region: str) -> Optional[Personnel]:
        region_stations = [s for s in self.stations 
                          if s.region == region and s.id != target_station_id 
                          and not (s.is_fully_staffed and not s.has_excess_medics and not s.has_excess_drivers)]
        # Start from less important stations
        region_stations.sort(key=lambda s: s.importance)
        
        for station in region_stations:
            personnel = self._find_suitable_personnel_from_any_station(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_in_neighbor_regions_from_any_station(self, role: str, target_station_id: str, target_region: str) -> Optional[Personnel]:
        neighbors = self.neighboring_regions.get(target_region, [])
        for neighbor in neighbors:
            personnel = self._find_in_region_from_any_station(role, target_station_id, neighbor)
            if personnel is not None:
                return personnel
        return None

    def _find_in_any_region_from_any_station(self, role: str, target_station_id: str) -> Optional[Personnel]:
        other_stations = [s for s in self.stations 
                         if s.id != target_station_id 
                         and not (s.is_fully_staffed and not s.has_excess_medics and not s.has_excess_drivers)]
        # Start from less important stations
        other_stations.sort(key=lambda s: s.importance)
        
        for station in other_stations:
            personnel = self._find_suitable_personnel_from_any_station(station, role, target_station_id)
            if personnel is not None:
                return personnel
        return None

    def _find_suitable_personnel(self, station: Station, role: str, target_station_id: str) -> Optional[Personnel]:
        if role not in station.get_excess_roles():
            return None

        candidates = [p for p in station.assigned_personnel 
                     if p.can_work_as(role) and p.can_work_at(target_station_id) 
                     and p.rotation_count < self.max_rotations_per_personnel]

        if not candidates:
            return None

        # Prioritize those in rotation
        rotating = [p for p in candidates if p.assigned_from is not None and p.assigned_from != station.id]
        suitable = rotating if rotating else candidates

        # Select the one with least rotations
        suitable.sort(key=lambda p: p.rotation_count)
        least_rotated = [p for p in suitable if p.rotation_count == suitable[0].rotation_count]

        # Prioritize preferred station
        for p in least_rotated:
            if target_station_id in p.preferred_stations:
                return p
        return least_rotated[0]

    def _find_suitable_personnel_from_any_station(self, station: Station, role: str, target_station_id: str) -> Optional[Personnel]:
        # Station must have at least 1 personnel with the required role
        candidates = [p for p in station.assigned_personnel 
                     if p.can_work_as(role) and p.can_work_at(target_station_id) 
                     and p.rotation_count < self.max_rotations_per_personnel]

        if not candidates:
            return None

        # Prioritize those in rotation
        rotating = [p for p in candidates if p.assigned_from is not None and p.assigned_from != station.id]
        suitable = rotating if rotating else candidates

        # Select the one with least rotations
        suitable.sort(key=lambda p: p.rotation_count)
        least_rotated = [p for p in suitable if p.rotation_count == suitable[0].rotation_count]

        # Prioritize preferred station
        for p in least_rotated:
            if target_station_id in p.preferred_stations:
                return p
        return least_rotated[0]


def main():
    
    creator = DataCreator(shift_list, scoring, df_signs, driver_medic)
    creator.clean_driver_medic()
    logging.info("Driver/Medic file cleaning completed.")
    
    creator.clean_signs()
    logging.info("Signs cleaned successfully.")
    creator.staff_shift_file_cleaning()
    logging.info("Shift list cleaned successfully.")

    creator.scoring['station_expendable']= creator.scoring_type()
    data = creator.create_source_data()
    logging.info("Source data created successfully.")
    
    with open(rf'C:\Users\mkaya\OneDrive\Masaüstü\{SOURCE_DATA_NAME}', 'w', encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False, indent=4)
    logging.info(f"Source data saved as {SOURCE_DATA_NAME} successfully.")
    
    
    distributor = StationDistributor.from_dict(data)
    result = distributor.distribute_personnel()

    print(f'Açık İstasyonlar: {len(result.open_stations)}')
    print(f'Kapalı İstasyonlar: {len(result.closed_stations)}')
    print(f'Taşınan Personel: {result.personnel_moved}')
    print('\nİşlem Logları:')
    open_station_names = [s.id for s in result.open_stations]
    closed_station_names = [s.id for s in result.closed_stations]
    logs = result.logs
    
    for s in result.open_stations:
        for personnel in s.assigned_personnel:
            if personnel.assigned_from!= s.id:
                logs.append(f'{personnel.name} ({", ".join(personnel.roles)}) {personnel.assigned_from} -> {s.id}')
    logs= logs[::-1]  # Reverse logs to show latest first
    max_len = max(len(open_station_names), len(closed_station_names), len(logs))

    def pad(lst):
        return lst + [''] * (max_len - len(lst))

    result_excel = pd.DataFrame({
        'Açılan İstasyonlar': pad(open_station_names),
        'İşlem Logları': pad(logs),
        'Kapalı İstasyonlar': pad(closed_station_names)
    })

    result_excel.to_excel('C:/Users/mkaya/Downloads/result.xlsx', index=False)
    
    for log in result.logs:
        print(f'- {log}')

if __name__ == "__main__":
    
    shift_list = pd.read_excel(rf"C:\Users\mkaya\Downloads\Personel-Nöbet-Listesi (50).xls", header=None)
    df_signs = pd.read_excel(r"C:\Users\mkaya\Downloads\Personel-Imza-Defteri (21).xls", header=None)
    driver_medic= pd.read_excel(r"C:\Users\mkaya\Downloads\ASGE ALAN PERSONEL.xlsx")
    
    with open(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\team_similarities\similarity_results.json", 'r', encoding='utf-8') as f:
        similarity_results = json.load(f)
    
    scoring_file_name = DataCreator(None, None, None, None).get_scoring_file_name()
    logging.info(f"Scoring file name: {scoring_file_name}")
    
    scoring = pd.read_excel(rf"C:\Users\mkaya\OneDrive\Masaüstü\istanbul112_hidden\data\case_reports\europe\parquet_files\team_case_intensities\overall\{scoring_file_name}")
    
    main()
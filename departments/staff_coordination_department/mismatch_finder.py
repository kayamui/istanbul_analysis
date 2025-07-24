import pandas as pd
import numpy as np

from docx import Document

import os

import logging
logging.basicConfig(level=logging.INFO)

current_dir="C:/Users/mkaya/Downloads/mismatch_finder" #os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

SHIFT_LIST_FOLDER= os.path.join(current_dir,'Personel Nöbet Listesi')
LEFT_SHIFT_DOCX_FOLDER= os.path.join(current_dir,'Nöbeti Terkeden Personel Dosyası')
DIDNT_SHOWUP_DOCX_FOLDER= os.path.join(current_dir,'Nöbete Gelmeyen Personel Dosyası')


class DataCreator:
    def __init__(self,left_shift_docx_file,didnt_showup_docx_file):
        
        self.left_shift_docx_file= left_shift_docx_file
        self.didnt_showup_docx_file= didnt_showup_docx_file
        
        logging.info("Tables from left_shift docx file are being extracted...")
        self.left_shift_tables= self.extract_tables_from_docx(self.left_shift_docx_file)
        logging.info("Tables from didnt_showup docx file are being extracted...")
        self.didnt_showup_tables= self.extract_tables_from_docx(self.didnt_showup_docx_file)

        self.left_shift_table= self.left_shift_tables[1]
        self.didnt_showup_table= self.didnt_showup_tables[1]
        
        logging.info("Dataframes are being created...")
        self.left_shift_df= self.create_dataframe(self.left_shift_table)
        self.didnt_showup_df= self.create_dataframe(self.didnt_showup_table)
        
        logging.info("Cleaning dataframes...")
        self.left_shift_df= self.clean_misssing_shift_docs(self.left_shift_df)
        self.didnt_showup_df= self.clean_misssing_shift_docs(self.didnt_showup_df)
        
    def __call__(self, *args, **kwds):
        return self.left_shift_df, self.didnt_showup_df

    def extract_tables_from_docx(self,docx_file):
        doc = Document(docx_file)
        all_tables_data = []

        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_data.append(row_data)
            all_tables_data.append(table_data)

        return all_tables_data

    def create_dataframe(self,table):
        df= pd.DataFrame(columns= table[0])
        for row in table[1:]:
            df.loc[len(df)]= row
        df= df[df[df.columns[1]].apply(lambda x: x != '')]

        return df
    
    def clean_misssing_shift_docs(self,df):
        try:
            df['İSTASYON']= df['İSTASYON'].apply(lambda x: x.split('-')[0] +  str(int(x.split('-')[1])) if x.split('-')[1].isnumeric() and len(x.split('-'))>1 else x)
            df['İSTASYON']= df['İSTASYON'].apply(lambda x: "FTH05" if x.strip()=='FTH5' else x)
            df['İSİM']= df['İSİM'].astype(str).str.strip()
            df['SAAT']= df['SAAT'].apply(lambda x: x[0:-1] if not x[-1].isnumeric() else x)
        except ValueError as e:
            raise ValueError(f"Something went wrong: {e}")
        return df
            
class MismatchFinder():
    
    def __init__(self,left_shift_df,didnt_showup_df, shift_list_path):
        self.left_shift_df= left_shift_df
        self.didnt_showup_df= didnt_showup_df
        
        self.shift_list= self.staff_shift_file_cleaning(shift_list_path)
    
    def __call__(self, *args, **kwds):
        self.find_didnt_showup_mismathces()
        self.find_left_shift_mismathces()
        
        return self.didnt_showup_mismatches, self.left_shift_mismatches
    
    def staff_shift_file_cleaning(self):

        # WARNING: READ YOUR EXCEL FILE WITH header=None , F.e = pd.read_excel("self.shift_list.xlsx", header=None)
        self.shift_list= pd.read_excel(self.shift_list_path, header=None)

        # Identify station rows: col1 has value, cols 2–4 are empty
        station_mask = self.shift_list[1].notna() & self.shift_list[[2, 3, 4]].isna().all(axis=1)
        self.shift_list["RawStation"] = self.shift_list[1].where(station_mask)

        # Forward fill station names
        self.shift_list["İstasyon"] = self.shift_list["RawStation"].ffill()
        self.shift_list.columns= self.shift_list.loc[self.shift_list[self.shift_list[1] == 'İsim'].index[0]]
        self.shift_list= self.shift_list[[col for col in self.shift_list.columns if pd.notna(col)]]
        self.shift_list.rename(columns={self.shift_list.columns[-1]: 'İstasyon'}, inplace=True)
        self.shift_list= self.shift_list[(self.shift_list['Kimlik No'].notna()) & (self.shift_list['Kimlik No'] != 'Kimlik No')]
        
        distinct_codes = { 'BAYRAMP': 'BYR', 'BEYOĞLU': 'BEY', 'BEŞİKTAŞ': 'BEŞ', 'EYÜP': 'EYP', 'FATİH': 'FTH',
        'GAZİOSMANPAŞA': 'GOP', 'GÜNGÖREN': 'GNG', 'KAĞITHANE': 'KĞT', 'SARIYER': 'SRY', 'SLTGAZİ': 'STG', 'ŞİŞLİ': 'ŞİŞ', 'Z.BURNU': 'ZTB',
        'ARNKÖY': 'ARN', 'AVCILAR':'AVC', 'B.EVLER':'BHC', 'B.ÇEKMECE':'BÇK', 'BAKIRKÖY':'BKR', 'BAĞCILAR':'BAG',
        'BEYDÜZÜ':'BDZ', 'BŞKŞEHİR':'BŞK', 'ESENLER':'ESN', 'ESENYURT':'ESY', 'K.ÇEKMECE':'KÇK', 'SİLİVRİ':'SLV', 'ÇATALCA':'ÇTL'
        }
        self.shift_list['İstasyon']= self.shift_list['İstasyon'].apply(lambda x:distinct_codes[ x.split(' ')[0]] +x.split(' ')[1]  if x.split(' ')[0]  in distinct_codes.keys() else pd.NA )
        self.shift_list= self.shift_list[self.shift_list['İstasyon'].notna()]
        self.shift_list['İSİM']= (self.shift_list['İsim'] + ' ' + self.shift_list['Soyisim']).str.strip()

        return self.shift_list
    
    def convert_to_datetime(self,date):
        return pd.to_datetime(date, format='mixed')
    
    def find_hour(self):
        self.left_shift_df['hour']= self.left_shift_df['SAAT'].apply(lambda x: int(x.split(':')[0]))
        self.left_shift_df['minute']= self.left_shift_df['SAAT'].apply(lambda x: int(x.split(':')[1]))
        
        return self.left_shift_df
    
    def find_didnt_showup_mismathces(self):
        didnt_showup_mismatches= pd.merge(self.didnt_showup_df, self.shift_list, how='right', left_on=['İSTASYON', 'İSİM'], right_on=['İstasyon', 'İSİM'])
        didnt_showup_mismatches= didnt_showup_mismatches[didnt_showup_mismatches['İSİM'].isin(self.didnt_showup_df['İSİM'].to_list())]
        didnt_showup_mismatches['İSTASYON'].fillna(didnt_showup_mismatches['İstasyon'], inplace=True)
        
        if len(didnt_showup_mismatches) != 0:
            logging.warning("Nöbete Gelmeyen Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar Bulundu!")
            return didnt_showup_mismatches
        else:
            logging.info("Nöbete Gelmeyen Personel Listesi İle Personel Nöbet Listesi Arasında Uyuşmazlık Bulunamadı.")
            return pd.DataFrame()
    
    def find_left_shift_mismathces(self):
        left_shift_mismathces= self.find_hour()
        left_shift_mismatches= pd.merge(self.left_shift_df, self.shift_list, how='right', left_on=['İSİM', 'İSTASYON'], right_on=['İSİM', 'İstasyon'])
        left_shift_mismatches= left_shift_mismatches[left_shift_mismatches['İSİM'].isin(self.left_shift_df['İSİM'].to_list())]
        left_shift_mismatches['Bitiş Tarihi']= left_shift_mismatches['Bitiş Tarihi'].apply(self.convert_to_datetime)
        left_shift_mismatches[(left_shift_mismatches['Bitiş Tarihi'].dt.hour != left_shift_mismatches['hour']) | (left_shift_mismatches['Bitiş Tarihi'].dt.minute != left_shift_mismatches['minute'])]

        if len(left_shift_mismatches) != 0:
            logging.warning("Nöbeti Terkeden Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar Bulundu!")
            return left_shift_mismatches
        else:
            logging.info("Nöbeti Terkeden Personel Dosyası ile Personel Nöbet Listesi Arasında Uyuşmazlık Bulunamadı.")
            return pd.DataFrame()
    
    
def main():
    
    didnt_showup_mismatches.to_excel(os.path.join(current_dir,'didnt_showup_mismatches.xlsx'), index=False)
    left_shift_mismatches.to_excel(os.path.join(current_dir,'left_shift_mismatches.xlsx', index=False))
    
if __name__ == "__main__":
    
    shift_list_path= os.path.join(SHIFT_LIST_FOLDER, os.listdir(SHIFT_LIST_FOLDER)[0])
    left_shift_path= os.path.join(LEFT_SHIFT_DOCX_FOLDER, os.listdir(LEFT_SHIFT_DOCX_FOLDER)[0])
    didnt_showup_path= os.path.join(DIDNT_SHOWUP_DOCX_FOLDER, os.listdir(DIDNT_SHOWUP_DOCX_FOLDER)[0])
    
    creator= DataCreator(left_shift_path, didnt_showup_path)
    left_shift_df, didnt_showup_df= creator()

    mismatch_finder= MismatchFinder(left_shift_df, didnt_showup_df, shift_list_path)
    didnt_showup_mismatches, left_shift_mismatches= mismatch_finder()
    
    main()
# %%
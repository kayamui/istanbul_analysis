import pandas as pd
import numpy as np

from docx import Document

from difflib import SequenceMatcher

import os

import logging
logging.basicConfig(level=logging.INFO)

from tabulate import tabulate

import warnings
warnings.filterwarnings("ignore")

current_dir= os.path.dirname(os.path.abspath(__file__)) #"C:/Users/mkaya/Downloads/mismatch_finder"
os.chdir(current_dir)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

results_folder = os.path.join(current_dir, "Sonuclar")
os.makedirs(results_folder, exist_ok=True)

SHIFT_LIST_FOLDER= os.path.join(current_dir,'Personel Nöbet Listesi')
LEFT_SHIFT_DOCX_FOLDER= os.path.join(current_dir,'Nöbeti Terkeden Personel Dosyası')
DIDNT_SHOWUP_DOCX_FOLDER= os.path.join(current_dir,'Nöbete Gelmeyen Personel Dosyası')

STAFF_LIST_FOLDER= os.path.join(current_dir,'Personel Listesi')

class DataCreator:
    def __init__(self,left_shift_docx_file,didnt_showup_docx_file, staff_list_path):

        self.left_shift_docx_file= left_shift_docx_file
        self.didnt_showup_docx_file= didnt_showup_docx_file

        self.staff_list= pd.read_excel(staff_list_path)
        self.staff_list['name_sur']= (self.staff_list['Adı'] + ' ' + self.staff_list['Soyadı']).str.strip()

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

        self.name_correction()

    def __call__(self, *args, **kwds):
        return self.left_shift_df, self.didnt_showup_df
    def similar(self,a, b):
        return SequenceMatcher(None, a, b).ratio()

    def name_correction(self):
        not_registered_names= pd.concat([self.didnt_showup_df[~self.didnt_showup_df['İSİM'].isin(self.staff_list['name_sur'].to_list())], self.left_shift_df[~self.left_shift_df['İSİM'].isin(self.staff_list['name_sur'].to_list())]])
        name_dict= {}

        manual_names= []

        for name in not_registered_names['İSİM'].to_list():
            ratio= 0
            for staff_name in self.staff_list['name_sur'].to_list():
                if self.similar(name, staff_name) > ratio:
                    ratio= self.similar(name, staff_name)
                    name_dict[name]= staff_name
        dummy_index= 1
        for name in name_dict.keys():
            print(f"{dummy_index}: {name} -> {name_dict[name]}")
            ask= str(input("İsim personel listesine göre bu şekilde düzeltilecektir, onaylıyor musunuz?[e/h]: "))
            if ask.lower() == 'e':
                self.didnt_showup_df.loc[self.didnt_showup_df['İSİM'] == name, 'İSİM'] = name_dict[name]
                self.left_shift_df.loc[self.left_shift_df['İSİM'] == name, 'İSİM'] = name_dict[name]
                dummy_index += 1
            else:
                new_name= str(input("Lütfen personelin ismini personel listesinde yazan şekilde giriniz: "))
                new_name= new_name.replace("i","İ").replace("ı","I").replace("ö","Ö").replace("ü","Ü").replace("ş","Ş").replace("ğ","Ğ").upper().strip()

                if new_name not in self.staff_list['name_sur'].to_list():
                    print('=='*75)
                    logging.warning("Yazılan Personel Adı Nöbet Listesinde Bulunamadı, Personel İsmini Manuel Olarak Kontrol Ediniz!")
                    print('=='*75)
                    manual_names.append(name)
                    continue

                self.didnt_showup_df.loc[self.didnt_showup_df['İSİM'] == name, 'İSİM'] = new_name
                self.left_shift_df.loc[self.left_shift_df['İSİM'] == name, 'İSİM'] = new_name
                dummy_index += 1
        print('**'*75)
        print(f"Personel isimleri düzeltildi. Manuel Kontrol Edilmesi Gereken Personeller: {manual_names}")
        print('**'*75)

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
        self.didnt_showup_mismatches = self.find_didnt_showup_mismathces()
        self.left_shift_mismatches = self.find_left_shift_mismathces()

        return self.didnt_showup_mismatches, self.left_shift_mismatches

    def staff_shift_file_cleaning(self, shift_list_path):

        # WARNING: READ YOUR EXCEL FILE WITH header=None , F.e = pd.read_excel("self.shift_list.xlsx", header=None)
        self.shift_list= pd.read_excel(shift_list_path, header=None)

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
            show_df= didnt_showup_mismatches[['Kimlik No','İsim','Soyisim', 'Telefon','İstasyon','Başlangıç Tarihi', 'Bitiş Tarihi']]
            logging.warning("Nöbete Gelmeyen Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar Bulundu!")
            print('*'*len("WARNING:root:Nöbete Gelmeyen Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar Bulundu!"))
            print("NÖBETE GELMEYEN PERSONEL DOSYASINDA BULUNAN UYUŞMAZLIKLAR")
            print('='*len("NÖBETE GELMEYEN PERSONEL DOSYASINDA BULUNAN UYUŞMAZLIKLAR"))
            print(tabulate(show_df, headers='keys', tablefmt='github', showindex=False))
            print('='*len("NÖBETE GELMEYEN PERSONEL DOSYASINDA BULUNAN UYUŞMAZLIKLAR"))

            return didnt_showup_mismatches
        else:
            logging.info("Nöbete Gelmeyen Personel Listesi İle Personel Nöbet Listesi Arasında Uyuşmazlık Bulunamadı.")
            return pd.DataFrame()

    def find_left_shift_mismathces(self):
        left_shift_mismathces= self.find_hour()
        left_shift_mismatches= pd.merge(self.left_shift_df, self.shift_list, how='right', left_on=['İSİM', 'İSTASYON'], right_on=['İSİM', 'İstasyon'])
        left_shift_mismatches= left_shift_mismatches[left_shift_mismatches['İSİM'].isin(self.left_shift_df['İSİM'].to_list())]
        left_shift_mismatches['Bitiş Tarihi']= left_shift_mismatches['Bitiş Tarihi'].apply(self.convert_to_datetime)

        left_shift_mismatches['shift_hour']= left_shift_mismatches['Bitiş Tarihi'].dt.hour
        left_shift_mismatches['shift_hour']= left_shift_mismatches['shift_hour'].astype('int64')
        left_shift_mismatches['shift_minute']= left_shift_mismatches['Bitiş Tarihi'].dt.minute
        left_shift_mismatches['shift_minute']= left_shift_mismatches['shift_minute'].astype('int64')

        left_shift_mismatches=left_shift_mismatches[(left_shift_mismatches['shift_hour'] != left_shift_mismatches['hour']) | (left_shift_mismatches['shift_minute'] != left_shift_mismatches['minute'])]

        if len(left_shift_mismatches) != 0:
            show_df= left_shift_mismatches[['Kimlik No','İsim','Soyisim', 'SAAT','Telefon','İstasyon','Başlangıç Tarihi', 'Bitiş Tarihi']].rename(columns= {'SAAT':'Nöbeti Terketme Saati'})
            logging.warning("Nöbeti Terkeden Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar Bulundu!")
            print('='*len("NOBETİ TERKEDEN PERSONEL DOSYASINDA BULUNAN UYUŞMAZLIKLAR"))
            print("NOBETİ TERKEDEN PERSONEL DOSYASINDA BULUNAN UYUŞMAZLIKLAR")
            print('='*len("NOBETİ TERKEDEN PERSONEL DOSYASINDA BULUNAN UYUŞMAZLIKLAR"))
            print(tabulate(show_df, headers='keys', tablefmt='github',showindex=False))
            return left_shift_mismatches
        else:
            logging.info("Nöbeti Terkeden Personel Dosyası ile Personel Nöbet Listesi Arasında Uyuşmazlık Bulunamadı.")
            return pd.DataFrame()

def main():

    didnt_showup_mismatches.to_excel(os.path.join(results_folder,'Nöbete Gelmeyen Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar.xlsx'), index=False)
    left_shift_mismatches.to_excel(os.path.join(results_folder,'Nöbeti Terkeden Personel Dosyası İle Personel Nöbet Listesi Arasında Uyuşmazlıklar.xlsx'), index=False)

    print('*' * len("Excel dosyaları başarıyla kaydedildi."))
    print("Excel dosyaları başarıyla kaydedildi.")

if __name__ == "__main__":
    try:
        shift_list_path= os.path.join(SHIFT_LIST_FOLDER, os.listdir(SHIFT_LIST_FOLDER)[0])
        left_shift_path= os.path.join(LEFT_SHIFT_DOCX_FOLDER, os.listdir(LEFT_SHIFT_DOCX_FOLDER)[0])
        didnt_showup_path= os.path.join(DIDNT_SHOWUP_DOCX_FOLDER, os.listdir(DIDNT_SHOWUP_DOCX_FOLDER)[0])
        staff_list_path= os.path.join(STAFF_LIST_FOLDER, os.listdir(STAFF_LIST_FOLDER)[0])

        creator= DataCreator(left_shift_path, didnt_showup_path,staff_list_path)
        left_shift_df, didnt_showup_df= creator()

        mismatch_finder= MismatchFinder(left_shift_df, didnt_showup_df, shift_list_path)
        didnt_showup_mismatches, left_shift_mismatches= mismatch_finder()

        main()
    except Exception as e:
        print("="*60)
        print("Beklenmeyen bir hata oluştu:")
        print(str(e))
        print("Lütfen sistem yöneticinizle iletişime geçin.")
        print("="*60)
        os.system("pause")
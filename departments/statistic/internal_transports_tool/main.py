import pandas as pd
import numpy as np
import datetime as dt
import os
from glob import glob
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Progress Window GUI
class ProgressWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nakil Defteri Düzenleyicisi")
        self.root.geometry("400x120")
        self.root.resizable(False, False)
        self.label = tk.Label(self.root, text="Başlatılıyor...", font=("Arial", 12))
        self.label.pack(pady=30)
        self.root.update()

    def update_status(self, message):
        self.label.config(text=message)
        self.root.update()

    def close(self):
        self.root.destroy()

def show_error(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Hata", message)
    root.destroy()

def show_success(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("İşlem Tamamlandı", message)
    root.destroy()

def main():
    gui = ProgressWindow()

    try:
        BASE_DIR = get_base_dir()
        input_folder = os.path.join(BASE_DIR, 'input')
        data_folder = os.path.join(BASE_DIR, 'data')
        output_folder = os.path.join(BASE_DIR, 'output')

        chief_folder = os.path.join(input_folder, 'sef_cizelgesi')
        internal_transports_folder = os.path.join(input_folder, 'nakil_defteri')


        # Step 1: Reading Excel
        gui.update_status("Excel Dosyası Okunuyor...")
        chief_files = sorted(glob(os.path.join(chief_folder, '*.xls*')), key=os.path.getmtime, reverse=True)
        if not chief_files:
            raise FileNotFoundError("Şef Çizelgesi bulunamadı!")
        
        df_chief_days= pd.DataFrame()
        for chief_file in chief_files:
            chief_file_loaded= pd.read_excel(chief_file)
            for i in range(len(chief_file_loaded)):
                if any(chief_file_loaded.iloc[i].isin(['TARİH'])):
                    chief_file_loaded.columns= chief_file_loaded.iloc[i]
                    chief_file_loaded= chief_file_loaded[i+1:]
                    df_chief_days= pd.concat([df_chief_days, chief_file_loaded])
                    break
        

        internal_transports_files= sorted(glob(os.path.join(internal_transports_folder, '*.xls*')), key=os.path.getmtime, reverse=True)
        if not internal_transports_files:
            raise FileNotFoundError("Nakil Defteri bulunamadı!")
        df_raw= pd.read_excel(internal_transports_files[0])

        df_clinic= pd.read_excel(os.path.join(data_folder, 'clinic_keyword.xlsx'))
        df_hospital= pd.read_excel(os.path.join(data_folder, 'hospital_keyword.xlsx'))
        df_presidency= pd.read_excel(os.path.join(data_folder, 'presidency_keyword.xlsx'))
        team_dict= pd.read_excel(os.path.join(data_folder, 'team_type.xlsx'))
        
        clinic_keyword= dict(zip(df_clinic['clinic'], df_clinic['corrected_clinic']))
        hospital_keyword= dict(zip(df_hospital['hospital'], df_hospital['corrected_hospital']))
        presidency_keyword= dict(zip(df_presidency['hospital'], df_presidency['presidency']))
        team_keyword= dict(zip(team_dict['team_name'], team_dict['team_type']))

        # Step 2: Processing
        gui.update_status("Dosya Dönüştürülüyor...")

        df_raw['Oluşturma Tarihi']= pd.to_datetime(df_raw['Oluşturma Tarihi'], format='%d-%m-%Y %H:%M:%S')
        month= df_raw.iloc[0]['Oluşturma Tarihi'].month
        month_dict= {1:'OCAK', 2:'ŞUBAT', 3:'MART', 4:'NİSAN', 5:'MAYIS', 6:'HAZİRAN', 7:'TEMMUZ', 8:'AĞUSTOS', 9:'EYLÜL', 10:'EKİM', 11:'KASIM', 12:'ARALIK'}
        df_raw['AY']= month_dict[month]
        df_raw['Oluşturma']= df_raw['Oluşturma Tarihi'].dt.strftime('%d-%m-%Y')
        df_raw['Tarihi']= df_raw['Oluşturma Tarihi'].dt.strftime('%H:%M:%S')
        df_raw['Şef Tarihi']= df_raw['Oluşturma Tarihi'].apply(lambda x: x.date() - dt.timedelta(days=1) if 0 <= x.hour < 8 else x.date())
        

        df_chief_days= df_chief_days[['TARİH', 'İSİM']]
        df_chief_days['TARİH']= pd.to_datetime(df_chief_days['TARİH'], format='%d-%m-%Y')
        df_raw['Şef Tarihi']= pd.to_datetime(df_raw['Şef Tarihi'], format='%d-%m-%Y')
        df_raw= pd.merge(df_raw, df_chief_days, left_on='Şef Tarihi', right_on='TARİH', how='left')
        df_raw.rename(columns={'İSİM':'Şef Günleri'}, inplace=True)
        df_raw.drop(columns=['TARİH'], inplace=True)

        df_raw['Düzenlenmiş Nakil Talep Eden Hastane']= df_raw['Nakil Talep Eden Hastane'].map(hospital_keyword, na_action=None)
        df_raw['Düzenlenmiş Kabul Eden Klinik']= df_raw['Kabul Eden Klinik'].map(clinic_keyword, na_action=None).fillna('NAKİL İPTALİ')
        df_raw['Düzenlenmş Kabul Eden Hastane']= df_raw['Kabul Eden Hastane'].map(hospital_keyword, na_action=None).fillna('NAKİL İPTALİ')
        df_raw['Nakil Talep Eden Başkanlık']= df_raw['Düzenlenmiş Nakil Talep Eden Hastane'].map(presidency_keyword, na_action=None).fillna('BAĞLI OLDUĞU BAŞKANLIK BULUNMAYAN')
        df_raw['Kabul Eden Hastane Başkanlık']= df_raw['Düzenlenmş Kabul Eden Hastane'].map(presidency_keyword, na_action=None).fillna('BAĞLI OLDUĞU BAŞKANLIK BULUNMAYAN')
        df_raw['Düzenlenmiş Covid-19 Durumu']= pd.NA
        df_raw.loc[df_raw[(df_raw['Covid-19 Durumu'] == 'Risksiz') | (df_raw['Covid-19 Durumu'] == 'HSYS Servis Hatası')].index, 'Düzenlenmiş Covid-19 Durumu']= 'COVİD DIŞI'


        df_raw['team']= df_raw['Taşıyan Ekip / Veriliş Saati'].apply(lambda x: x.split('-')[0].strip() if '-' in str(x) else x)
        df_raw['Ekip Türü']= df_raw['team'].map(team_keyword, na_action=None)

        df_raw.drop(columns=['team'], inplace=True)
        df_raw.drop(columns='Oluşturma Tarihi', inplace=True)


        df_raw.insert(0, 'AY', df_raw.pop('AY'))
        df_raw.insert(2, 'Oluşturma', df_raw.pop('Oluşturma'))
        df_raw.insert(3, 'Tarihi', df_raw.pop('Tarihi'))
        df_raw.insert(4, 'Şef Tarihi', df_raw.pop('Şef Tarihi'))
        df_raw.insert(5, 'Şef Günleri', df_raw.pop('Şef Günleri'))
        df_raw.insert(13, 'Nakil Talep Eden Başkanlık', df_raw.pop('Nakil Talep Eden Başkanlık'))
        df_raw.insert(15, 'Düzenlenmiş Nakil Talep Eden Hastane', df_raw.pop('Düzenlenmiş Nakil Talep Eden Hastane'))
        df_raw.insert(33, 'Kabul Eden Hastane Başkanlık', df_raw.pop('Kabul Eden Hastane Başkanlık'))
        df_raw.insert(35, 'Düzenlenmş Kabul Eden Hastane', df_raw.pop('Düzenlenmş Kabul Eden Hastane'))
        df_raw.insert(37, 'Düzenlenmiş Kabul Eden Klinik', df_raw.pop('Düzenlenmiş Kabul Eden Klinik'))
        df_raw.insert(42, 'Ekip Türü', df_raw.pop('Ekip Türü'))
        df_raw.insert(44, 'Düzenlenmiş Covid-19 Durumu', df_raw.pop('Düzenlenmiş Covid-19 Durumu'))


        df_uskudar= df_raw[df_raw['Nakil Talep Eden Hastane'].astype(str).str.contains('ÜSKÜDAR ÜNİVERSİTESİ') | df_raw['Kabul Eden Hastane'].astype(str).str.contains('ÜSKÜDAR ÜNİVERSİTESİ')]
        df_raw= df_raw[~(df_raw['Nakil Talep Eden Hastane'].astype(str).str.contains('ÜSKÜDAR ÜNİVERSİTESİ') | df_raw['Kabul Eden Hastane'].astype(str).str.contains('ÜSKÜDAR ÜNİVERSİTESİ'))]
        df_sehven_mukerrer= df_raw[df_raw['Iptal Nedeni'].isin(['Sehven Gönderim', 'Mükerrer Talep'])]
        df_raw= df_raw[~(df_raw['Iptal Nedeni'].isin(['Sehven Gönderim', 'Mükerrer Talep']))]

        df_sehven_mukerrer_uskudar= pd.concat([df_sehven_mukerrer, df_uskudar])


        header_cols= [('AY', 0),
        ('Oluşturma', 2),
        ('Tarihi', 3),
        ('Şef Tarihi', 4),
        ('Şef Günleri', 5),
        ('Nakil Talep Eden Başkanlık', 13),
        ('Düzenlenmiş Nakil Talep Eden Hastane', 15),
        ('Kabul Eden Hastane Başkanlık', 33),
        ('Düzenlenmş Kabul Eden Hastane', 35),
        ('Düzenlenmiş Kabul Eden Klinik', 37),
        ('Ekip Türü', 42),
        ('Düzenlenmiş Covid-19 Durumu', 44)]
        header_cols= [col[0] for col in header_cols]


        month= df_raw.iloc[0]['AY']
        year= df_raw.iloc[0]['Şef Tarihi'].year


        header_index = [df_raw.columns.get_loc(col) for col in header_cols]
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f'{month} {year} NAKİL DEFTERİ.xlsx')

        # Step 3: Writing output
        gui.update_status("Dönüştürülen Dosya Yazılıyor...")

        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        df_raw.to_excel(writer, sheet_name=f"DEFTER {len(df_raw)}", startrow=1, index=False,header=False)
        df_sehven_mukerrer_uskudar.to_excel(writer, sheet_name=f"SEHVEN-MÜKERRER-ÜSK.Ü-{len(df_sehven_mukerrer_uskudar)}", startrow=1, index=False,header=False)
        # Get the xlsxwriter workbook and worksheet objects.
        workbook = writer.book
        worksheet = writer.sheets[f"DEFTER {len(df_raw)}"]

        # Add a header format.
        header_format = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": "#D7E4BC",
                "border": 1,
            }
        )

        header_format_2= workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color":'#ADD8E6',
                "border": 1,
            }
        )

        # Write the column headers with the defined format.
        for col_num, value in enumerate(df_raw.columns.values):
            if col_num in header_index:
                worksheet.write(0, col_num, value, header_format)
            else:
                worksheet.write(0, col_num, value, header_format_2)

        worksheet=writer.sheets[f"SEHVEN-MÜKERRER-ÜSK.Ü-{len(df_sehven_mukerrer_uskudar)}"]
        for col_num, value in enumerate(df_sehven_mukerrer_uskudar.columns.values):
            if col_num in header_index:
                worksheet.write(0, col_num, value, header_format)
            else:
                worksheet.write(0, col_num, value, header_format_2)

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()

        gui.close()
        show_success(f"{output_file}\n\nbaşarıyla oluşturuldu.")

    except Exception as e:
        gui.close()
        show_error(f"Hata oluştu:\n\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()

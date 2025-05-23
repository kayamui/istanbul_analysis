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
        self.root.title("AVR Report Tool")
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

        # Step 1: Reading Excel
        gui.update_status("Excel Dosyası Okunuyor...")
        input_files = sorted(glob(os.path.join(input_folder, '*.xls*')), key=os.path.getmtime, reverse=True)
        if not input_files:
            raise FileNotFoundError("Girdi klasöründe .xls veya .xlsx uzantılı dosya bulunamadı.")
        df = pd.read_excel(input_files[0])

        # Step 2: Processing
        gui.update_status("Dosya Dönüştürülüyor...")

        df['Tarih'] = pd.to_datetime(df['İhbar/Çağrı Tarihi'] + ' ' + df['İhbar/Çağrı  Saati'], format='%d-%m-%Y %H:%M:%S')
        df['MANUEL ŞEF TARİHİ'] = df['Tarih'].apply(lambda x: (x.date() - dt.timedelta(days=1)) if 0 <= x.hour < 8 else x.date())
        chef_loc = df.columns.get_loc('İhbar/Çağrı Tarihi') - 1
        df.insert(chef_loc + 1, 'MANUEL ŞEF TARİHİ', df.pop('MANUEL ŞEF TARİHİ'))

        month_dict = {
            1: 'OCAK', 2: 'ŞUBAT', 3: 'MART', 4: 'NİSAN', 5: 'MAYIS', 6: 'HAZİRAN',
            7: 'TEMMUZ', 8: 'AĞUSTOS', 9: 'EYLÜL', 10: 'EKİM', 11: 'KASIM', 12: 'ARALIK'
        }

        df['month'] = df['Tarih'].dt.month
        df['AY'] = df['month'].map(month_dict)
        df.drop(columns='month', inplace=True)
        df.insert(0, 'AY', df.pop('AY'))

        hosp_df = pd.read_excel(os.path.join(data_folder, 'hospital_dict.xlsx'))
        hosp_dict = {k: v for k, v in zip(hosp_df['Nakledilen Hastane'], hosp_df['MANUEL DÜZENLEME Nakledilen Hastane']) if pd.notnull(v)}

        for col in ['Nakledilen Hastane', 'Sevk Eden Hastane', 'Sevk Edilen Hastane']:
            new_col = f'MANUEL DÜZENLEME {col}'
            df[new_col] = df[col].map(hosp_dict, na_action='ignore')
            df[new_col].fillna(df[col], inplace=True)
            df.insert(df.columns.get_loc(col) + 1, new_col, df.pop(new_col))

        icd_df = pd.read_excel(os.path.join(data_folder, 'icd_keyword.xlsx'))
        icd_dict = dict(zip(icd_df["ICD10 1'İNCİ SEVİYE GRUP ADI"], icd_df["MANUEL ICD DÜZENLEME"]))
        df['MANUEL ICD DÜZENLEME'] = df["ICD10 1'İNCİ SEVİYE GRUP ADI"].map(icd_dict, na_action='ignore')
        df.loc[df["ICD10 1'İNCİ SEVİYE GRUP ADI"].notna() & df["MANUEL ICD DÜZENLEME"].isna(), "MANUEL ICD DÜZENLEME"] = 'ICD ÇALIŞILMAMIŞ'
        df['MANUEL ICD DÜZENLEME'].fillna('TÜRÜ BELİRTİLMEMİŞ', inplace=True)
        icd_loc = df.columns.get_loc("ICD10 1'İNCİ SEVİYE GRUP ADI") + 1
        df.insert(icd_loc, 'MANUEL ICD DÜZENLEME', df.pop('MANUEL ICD DÜZENLEME'))

        df.drop(columns='Tarih', inplace=True)

        month = df['AY'].iloc[0]
        month_number = [k for k, v in month_dict.items() if v == month][0]
        year = df["MANUEL ŞEF TARİHİ"].apply(lambda x: x.year).mode()[0]

        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f'{month_number}-{month} {year} AVR ASOS TANI DÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')

        header_index = [
            df.columns.get_loc("AY"),
            df.columns.get_loc('MANUEL ŞEF TARİHİ'),
            df.columns.get_loc('MANUEL DÜZENLEME Nakledilen Hastane'),
            df.columns.get_loc('MANUEL DÜZENLEME Sevk Eden Hastane'),
            df.columns.get_loc('MANUEL DÜZENLEME Sevk Edilen Hastane'),
            df.columns.get_loc('MANUEL ICD DÜZENLEME'),
        ]

        # Step 3: Writing output
        gui.update_status("Dönüştürülen Dosya Yazılıyor...")

        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        sheet_name = f"{month}-{year}"
        df.to_excel(writer, sheet_name=sheet_name, startrow=1, index=False, header=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format_green = workbook.add_format({"bold": True, "text_wrap": True, "valign": "top", "fg_color": "#D7E4BC", "border": 1})
        header_format_blue = workbook.add_format({"bold": True, "text_wrap": True, "valign": "top", "fg_color": "#ADD8E6", "border": 1})

        for col_num, value in enumerate(df.columns.values):
            fmt = header_format_green if col_num in header_index else header_format_blue
            worksheet.write(0, col_num, value, fmt)

        writer.close()

        gui.close()
        show_success(f"{output_file}\n\nbaşarıyla oluşturuldu.")

    except Exception as e:
        gui.close()
        show_error(f"Hata oluştu:\n\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()

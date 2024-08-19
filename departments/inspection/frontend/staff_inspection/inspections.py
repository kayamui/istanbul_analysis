import pandas as pd
import numpy as np
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

def process_data(sheet_path, dataframes, concatenated_df, save_path):
    if sheet_path == 'all data':
        for i in dataframes.keys():
            df_temp = dataframes[i]
            df_temp.columns = df_temp.iloc[0]
            df_temp.drop(df_temp.index[0], inplace=True)
            df_temp.columns = ['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR', 'KONU BASLIGI', 'YAPILAN ISLEM']
            df_temp['SAYI'] = 1
            concatenated_df = pd.concat([concatenated_df, df_temp])
        concatenated_df['HAKKINDA TUTULAN KISI'] = concatenated_df['HAKKINDA TUTULAN KISI'].str.split('-')
        df_exploded = concatenated_df.explode('HAKKINDA TUTULAN KISI').reset_index(drop=True)
        df_exploded['HAKKINDA TUTULAN KISI'] = df_exploded['HAKKINDA TUTULAN KISI'].apply(lambda x: x.strip())

        df_exploded.groupby(['HAKKINDA TUTULAN KISI', 'KONU BASLIGI']).agg({'SAYI': 'sum'}).sort_values(by='SAYI', ascending=False).reset_index().to_excel(f'{save_path}/inceleme_tum_aylar.xlsx')
        df_exploded.groupby('KONU BASLIGI').agg({'SAYI': 'sum'}).sort_values(by='SAYI', ascending=False).to_excel(f'{save_path}/inceleme_tum_aylar_konu_basligi.xlsx')
    else:
        try:
            df_temp = dataframes[sheet_path]
            df_temp.columns = df_temp.iloc[0]
            df_temp.drop(df_temp.index[0], inplace=True)
            df_temp.columns = ['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR', 'KONU BASLIGI', 'YAPILAN ISLEM']
            df_temp['SAYI'] = 1
            concatenated_df = pd.concat([concatenated_df, df_temp])
            concatenated_df['HAKKINDA TUTULAN KISI'] = concatenated_df['HAKKINDA TUTULAN KISI'].str.split('-')
            df_exploded = concatenated_df.explode('HAKKINDA TUTULAN KISI').reset_index(drop=True)
            df_exploded['HAKKINDA TUTULAN KISI'] = df_exploded['HAKKINDA TUTULAN KISI'].apply(lambda x: x.strip())

            df_exploded.groupby(['HAKKINDA TUTULAN KISI', 'KONU BASLIGI']).agg({'SAYI': 'sum'}).sort_values(by='SAYI', ascending=False).reset_index().to_excel(f'{save_path}/inceleme_{sheet_path}.xlsx')
            df_exploded.groupby('KONU BASLIGI').agg({'SAYI': 'sum'}).sort_values(by='SAYI', ascending=False).to_excel(f'{save_path}/inceleme_{sheet_path}_konu_basligi.xlsx')

        except KeyError:
            messagebox.showerror("Error", "Lütfen Geçerli Bir Ay Giriniz!")

def inspections():
    concatenated_df = pd.DataFrame(columns=['SIRA', 'INC KODU', 'SONUC GELDI', 'TUTANAK BARKOD NO', 'OLUR BARKOD NO', 'GOREVLENDIRILEN INCELEMECI', 'TESLIM TARIHI', 'TAMAMLANMA TARIHI', 'INCELEMECININ GOREV YERI', 'EK', 'GENEL NOTLAR', 'HAKKINDA TUTULAN KISI', 'EKIP ADI', 'ACIKLAMALAR', 'KONU BASLIGI', 'YAPILAN ISLEM'])

    root = tk.Tk()
    root.title("Personel İnceleme */AVR112 AR-GE")

    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            excel_file_entry.delete(0, tk.END)
            excel_file_entry.insert(0, file_path)
            try:
                excel_file = pd.ExcelFile(file_path)
                month_menu['values'] = ['All Data'] + [sheet_name for sheet_name in excel_file.sheet_names]
            except Exception as e:
                messagebox.showerror("File Error", f"Dosya okunamadı: {e}")

    def choose_save_location():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            save_location_entry.delete(0, tk.END)
            save_location_entry.insert(0, folder_selected)
    
    def analyze_data():
        excel_path = excel_file_entry.get()
        save_path = save_location_entry.get()
        
        if not excel_path:
            messagebox.showwarning("Input Error", "Lütfen Excel Dosyasının Konumunu Giriniz!")
            return
        if not save_path:
            messagebox.showwarning("Input Error", "Lütfen Kayıt Konumunu Seçiniz!")
            return

        try:
            excel_file = pd.ExcelFile(excel_path)
            dataframes = {sheet_name.lower(): excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}
        except Exception as e:
            messagebox.showerror("File Error", f"Dosya okunamadı: {e}")
            return
        
        sheet_path = month_menu.get().lower()
        process_data(sheet_path, dataframes, concatenated_df, save_path)
        messagebox.showinfo("Success", "Analiz Tamamlandı!")
    
    frame = tk.Frame(root)
    frame.pack(pady=20, padx=20)

    excel_file_label = tk.Label(frame, text="Excel Dosyasının Konumu:")
    excel_file_label.grid(row=0, column=0, pady=5)

    excel_file_entry = tk.Entry(frame, width=50)
    excel_file_entry.grid(row=0, column=1, pady=5)

    browse_button = tk.Button(frame, text="Gözat", command=load_file)
    browse_button.grid(row=0, column=2, pady=5, padx=5)

    sheet_label = tk.Label(frame, text="Analiz Etmek İstediğiniz Ay:")
    sheet_label.grid(row=1, column=0, pady=5)

    month_menu = Combobox(frame, state="readonly")
    month_menu.grid(row=1, column=1, pady=5)
    month_menu.set("All Data")

    save_location_label = tk.Label(frame, text="Kayıt Konumunu Seçiniz:")
    save_location_label.grid(row=2, column=0, pady=5)

    save_location_entry = tk.Entry(frame, width=50)
    save_location_entry.grid(row=2, column=1, pady=5)

    save_button = tk.Button(frame, text="Gözat", command=choose_save_location)
    save_button.grid(row=2, column=2, pady=5, padx=5)

    analyze_button = tk.Button(frame, text="Analiz Et", command=analyze_data)
    analyze_button.grid(row=3, columnspan=3, pady=10)

    root.mainloop()

inspections()

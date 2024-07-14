import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import openpyxl
import xlsxwriter

class GPSDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("AR-GE AVRUPA 112 GPS DATA İŞLEYİCİ")
        
        self.label = tk.Label(root, text="Lütfen İşlenecek Dosyayı Seçiniz:")
        self.label.pack(pady=10)

        self.browse_button = tk.Button(root, text="Gözat", command=self.browse_file)
        self.browse_button.pack(pady=10)

        self.process_button = tk.Button(root, text="Başlat", command=self.process_file)
        self.process_button.pack(pady=10)
        self.process_button.config(state=tk.DISABLED)

        self.file_path = ""

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if self.file_path:
            self.process_button.config(state=tk.NORMAL)
            messagebox.showinfo("Dosya Seçildi", f"Seçilen Dosya: {self.file_path}")

    def process_file(self):
        if not self.file_path:
            messagebox.showwarning("Dosya Bulunamadı", "Lütfen Öncelikle Bir Dosya Seçiniz.")
            return
                
        try:
            excel_file = pd.ExcelFile(self.file_path)
            dataframes = {sheet_name: excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}

            for sheet_name, df in dataframes.items():
                df.columns = ['İstasyon Adı', 'Ekip No', 'Ambulans Plaka', 'KKM Protokol', 'Vaka Veriliş Tarihi', 'Vaka Veriliş Saati', 'GPS Hareket Saati', 'Fark', 'Bölge']
                df['Vaka Veriliş Saati'] = pd.to_datetime(df['Vaka Veriliş Saati'], format='%H:%M:%S', errors='coerce').dt.time
                df['GPS Hareket Saati'] = pd.to_datetime(df['GPS Hareket Saati'], format='%H:%M:%S', errors='coerce').dt.time
                
                # Calculate the time difference before extracting the time component
                df['Fark'] = (
                    pd.to_datetime(df['GPS Hareket Saati'], format='%H:%M:%S', errors='coerce') -
                    pd.to_datetime(df['Vaka Veriliş Saati'], format='%H:%M:%S', errors='coerce')
                )
                df['Fark'] = df['Fark'].dt.total_seconds().apply(lambda x: pd.to_datetime(x, unit='s').strftime('%H:%M:%S'))


            with pd.ExcelWriter(f"{self.file_path} GPS Verisi İşlendi.xlsx") as writer:

                # Write each dataframe to a separate sheet in the Excel file.
                for sheet_name, dataframe in dataframes.items():
                    dataframes[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)

            # Save the Excel file.
            writer.close()


            messagebox.showinfo("Başarılı", "Dosya Başarıyla Kaydedildi..")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya İşlenirken Bir hata Meydana Geldi:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSDataProcessor(root)
    root.mainloop()

import pandas as pd
import numpy as np
import warnings
import os
import datetime as dt
import sys
import hashlib
import winreg
import tkinter as tk
from tkinter import messagebox, simpledialog

warnings.filterwarnings('ignore')

# Constants
LOCK_PERIOD_DAYS = 180  # 6 months
MAX_ATTEMPTS = 3  # Max unlock attempts

class LockManager:
    def __init__(self):
        self.secret_key = "O Romeo, Romeo! wherefore art thou Romeo?"  # Fixed secret key

        # Ensure machine_guid.txt is saved in the same directory as the script
        self.program_dir = os.path.dirname(os.path.abspath(__file__))  
        self.guid_file = os.path.join(self.program_dir, "machine_guid.txt")  

        self.machine_guid = self.get_or_create_machine_guid()  # Ensure GUID file exists

    def get_machine_guid(self):
        """Retrieve the unique Machine GUID from the Windows registry."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ) as key:
                return winreg.QueryValueEx(key, "MachineGuid")[0]
        except Exception as e:
            print(f"Failed to retrieve Machine GUID: {e}")
            return "UnknownMachine"

    def get_or_create_machine_guid(self):
        """Ensure the machine_guid.txt file is created in the same directory as the program."""
        if os.path.exists(self.guid_file):
            with open(self.guid_file, "r") as file:
                return file.read().strip()

        # Generate and store Machine GUID
        machine_guid = self.get_machine_guid()
        with open(self.guid_file, "w") as file:
            file.write(machine_guid)

        messagebox.showinfo("Machine GUID Created", 
                            f"A file 'machine_guid.txt' has been created in:\n{self.program_dir}\n"
                            "Please send this file to the administrator for an unlock code.")
        
        return machine_guid

    def generate_unlock_code(self):
        """Generate an unlock code that changes every 5 minutes and is unique per computer."""
        current_time = dt.datetime.now()
        rounded_minutes = (current_time.minute // 5) * 5  # Round to nearest 5-minute mark
        time_string = f"{current_time.year}-{current_time.month}-{current_time.day} {current_time.hour}:{rounded_minutes:02d}"

        unlock_string = time_string + self.secret_key + self.machine_guid
        return hashlib.sha256(unlock_string.encode()).hexdigest()[:8]  # Shortened hash

    def prompt_unlock_code(self):
        """Ask the user for an unlock code and validate it."""
        while True:
            unlock_code = simpledialog.askstring("Unlock Required", "Please enter the unlock code provided by the administrator:")

            if unlock_code:
                if unlock_code == self.generate_unlock_code():
                    messagebox.showinfo("Success", "Program unlocked successfully!")
                    return True  # Unlock successful
                else:
                    messagebox.showerror("Invalid Code", "Incorrect unlock code. Please try again.")
            else:
                messagebox.showinfo("Exiting", "No unlock code entered. Exiting program.")
                sys.exit()

class UnlockPrompt:
    def __init__(self, lock_manager):
        self.lock_manager = lock_manager

    def prompt_unlock_code(self):
        """Ask the user for an unlock code."""
        while True:
            unlock_code = simpledialog.askstring("Unlock Required", "Please enter the unlock code:")
            if unlock_code:
                self.lock_manager.unlock(unlock_code)
                if not self.lock_manager.is_locked():
                    return True
                else:
                    messagebox.showerror("Invalid Code", "Incorrect unlock code. Try again.")
            else:
                messagebox.showinfo("Exiting", "No unlock code entered. Exiting program.")
                sys.exit()

class App:
    def __init__(self, root):
        self.root = root
        self.lock_manager = LockManager()

        # **Check if locked and prompt unlock BEFORE running anything**
        if self.lock_manager.is_locked():
            unlock_prompt = UnlockPrompt(self.lock_manager)
            unlock_prompt.prompt_unlock_code()

        self.show_splash_screen()

    def show_splash_screen(self):
        """Display a splash screen for 5 seconds."""
        self.splash_screen = tk.Toplevel(self.root)
        self.splash_screen.overrideredirect(True)
        self.splash_screen.geometry("800x400+300+200")
        self.splash_screen.configure(bg='#f0f4f7')

        tk.Label(self.splash_screen, text="HBYS VAKA ANALİZİ", font=("Helvetica", 24, "bold"), fg="#333", bg="#f0f4f7").pack(pady=80)
        tk.Label(self.splash_screen, text="İstanbul 112\nAll Copyrights Reserved", font=("Helvetica", 10, "italic"), fg="#555", bg="#f0f4f7", wraplength=750, justify="center").pack(side="bottom", pady=(0, 40))
        tk.Label(self.splash_screen, text="Avrupa 112", font=("Helvetica", 12), fg="#333", bg="#f0f4f7").place(x=20, y=360)
        tk.Label(self.splash_screen, text="Muhammed Kaya", font=("Helvetica", 12), fg="#333", bg="#f0f4f7").place(x=650, y=360)

        self.splash_screen.after(5000, self.end_splash_screen)

    def end_splash_screen(self):
        """Close splash and show main window."""
        self.splash_screen.destroy()
        self.run_main_program()

    def run_main_program(self):
        """Generate HBYS reports."""
        current_dir = os.path.abspath(os.getcwd())
        files = [f for f in os.listdir(current_dir) if 'Genel Vaka Araştırma' in f and f.endswith('.xls')]

        if not files:
            messagebox.showerror("Error", "No 'Genel Vaka Araştırma' file found!")
            sys.exit()

        df_eylul = pd.read_excel(os.path.join(current_dir, files[0]))

        # Process the data
        df_eylul['Onaylı'] = df_eylul['Doktor Onay Durum'].astype(str).str.contains('Onay Süreci Tamamlanmış ve PDF Oluşmuş').astype(int)
        df_eylul.loc[df_eylul['Onaylı']==1, 'Onaylı']= 'Evet'
        df_eylul.loc[df_eylul['Onaylı']==0, 'Onaylı']= 'Hayır'
        df_eylul['value']= 1
        df_eylul['Tabletten Gönderilme Tarih Saat']= df_eylul['Tabletten Gönderilme Tarihi\n'] + ' ' + df_eylul['Tabletten Gönderilme Saati\n']
        df_eylul['Doktor Onay Tarih Saat']= df_eylul['Doktor Onay Tarihi'] + ' ' + df_eylul['Doktor Onay Saati\n']

        df_notablet= df_eylul[df_eylul['Tabletten Gönderilme Tarih Saat'].isna()]
        df_tablet= df_eylul[df_eylul['Tabletten Gönderilme Tarih Saat'].notna()]
        df_notablet.fillna({'Tabletten Gönderilme Tarih Saat':1}, inplace=True)
        df_tablet['value']= 1
        df_onayli= df_eylul[df_eylul['Doktor Onay Tarih Saat'].notna()]

        df_onayli['Doktor Onay Tarih Saat']= pd.to_datetime(df_onayli['Doktor Onay Tarih Saat'], format='%d-%m-%Y %H:%M:%S')
        df_onayli['Tabletten Gönderilme Tarih Saat']= pd.to_datetime(df_onayli['Tabletten Gönderilme Tarih Saat'], format='%d-%m-%Y %H:%M:%S')
        df_onayli['onay_farki'] = (df_onayli['Doktor Onay Tarih Saat'] - df_onayli['Tabletten Gönderilme Tarih Saat']).dt.total_seconds()
        df_onayli['Hastaneye Varış Tarih Saat']= df_onayli['Hastaneye Varış Tarihi'] + ' ' + df_onayli['Hastaneye Varış Saati\n']
        df_onayli['Hastaneden Ayrılış Tarih Saat']= df_onayli['Hastaneden Ayrılış Tarihi'] + ' ' + df_onayli['Hastaneden Ayrılış Saati']
        df_onayli['Hastaneye Varış Tarih Saat']= pd.to_datetime(df_onayli['Hastaneye Varış Tarih Saat'], format='%d-%m-%Y %H:%M:%S')
        df_onayli['Hastaneden Ayrılış Tarih Saat']= pd.to_datetime(df_onayli['Hastaneden Ayrılış Tarih Saat'], format='%d-%m-%Y %H:%M:%S')
        df_onayli['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi']= (df_onayli['Hastaneden Ayrılış Tarih Saat'] - df_onayli['Tabletten Gönderilme Tarih Saat']).dt.total_seconds()
        df_onayli['Tabletten Gönderilme - Hastaneye Varış Tarihi']= (pd.to_datetime(df_onayli['Tabletten Gönderilme Tarih Saat'].astype(str)) - pd.to_datetime(df_onayli['Hastaneye Varış Tarih Saat'].astype(str))).dt.total_seconds()
        df_onayli['Hastanede Bulunma Süresi']= ( df_onayli['Hastaneden Ayrılış Tarih Saat'] - df_onayli['Hastaneye Varış Tarih Saat']).dt.total_seconds()
        df_onayli['Hastanede Bulunma Süresi']= df_onayli['Hastanede Bulunma Süresi'].fillna(0)
        df_onayli['Tabletten Gönderilme - Hastaneye Varış Tarihi'].fillna(0, inplace=True)
        df_onayli['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi'].fillna(0, inplace=True)

        df_hast_var= df_onayli.fillna(0)
        df_hast_var= df_hast_var[df_hast_var['Hastaneye Varış Tarih Saat']!=0]

        # Function to format time differences
        def format_timedelta(seconds):
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

        # Function to generate HBYS ekip tablosu
        def hbys_ekip_tablosu():

            tabletten_gönderilmeyen= df_notablet.groupby(['Ekip No']).agg({'Tabletten Gönderilme Tarih Saat':'sum'}).reset_index()
            tabletten_gönderilmeyen.rename(columns={'Tabletten Gönderilme Tarih Saat': 'Tabletten Gönderilmedi'},inplace=True)
            tabletten_gönderilen= df_tablet.groupby(['Ekip No']).agg({'value':'sum'}).reset_index()
            tabletten_gönderilen.rename(columns={'value':'Tabletten Gönderilen'},inplace=True)
            onayli_sayisi= df_eylul.groupby(['Ekip No', 'Onaylı']).agg({'value':'sum'}).reset_index()
            onayli= onayli_sayisi[onayli_sayisi['Onaylı']=='Evet']
            onayli.drop(columns='Onaylı', inplace=True)
            onaysiz= onayli_sayisi[onayli_sayisi['Onaylı']=='Hayır']
            onaysiz.drop(columns='Onaylı', inplace=True)
            onayli.rename(columns={'value':'Onaylı'},inplace=True)
            onaysiz.rename(columns={'value':'Onaysız'},inplace=True)
            toplam_vaka= df_eylul.groupby('Ekip No').agg({'value':'sum'})
            toplam_vaka.rename(columns={'value':'Toplam Vaka'},inplace=True)
            onay_farki= df_onayli.groupby('Ekip No').agg({'onay_farki':'mean'}).reset_index()


            onay_farki['onay_farki'].fillna(0, inplace=True)
            onay_farki['onay_farki']= onay_farki['onay_farki'].apply(format_timedelta)
            onay_farki.rename(columns={'onay_farki':'Doktor Onaylama Süresi'},inplace=True)

            hast_ayr_tab= df_onayli.groupby('Ekip No').agg({'Hastaneden Ayrılış - Tabletten Gönderilme Tarihi':'mean'}).reset_index()
            tab_gor_hast_var= df_hast_var.groupby('Ekip No').agg({'Tabletten Gönderilme - Hastaneye Varış Tarihi':'mean'}).reset_index()
            hast_bulunma= df_onayli.groupby('Ekip No').agg({'Hastanede Bulunma Süresi':'mean'}).reset_index()
            df_onayli['Hastanede Bulunma Süresi']= df_onayli['Hastanede Bulunma Süresi'].apply(format_timedelta)

            hast_ayr_tab['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi']= hast_ayr_tab['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi'].apply(format_timedelta)
            tab_gor_hast_var['Tabletten Gönderilme - Hastaneye Varış Tarihi']= tab_gor_hast_var['Tabletten Gönderilme - Hastaneye Varış Tarihi'].apply(format_timedelta)
            hast_bulunma['Hastanede Bulunma Süresi']= hast_bulunma['Hastanede Bulunma Süresi'].apply(format_timedelta)

            merged_df = tabletten_gönderilen.merge(tabletten_gönderilmeyen, on='Ekip No', how='outer')
            merged_df = merged_df.merge(onayli, on='Ekip No', how='outer')
            merged_df = merged_df.merge(onaysiz, on='Ekip No', how='outer')
            merged_df = merged_df.merge(toplam_vaka, on='Ekip No', how='outer')
            merged_df = merged_df.merge(onay_farki, on='Ekip No', how='outer')
            merged_df = merged_df.merge(hast_ayr_tab, on='Ekip No', how='outer')
            merged_df = merged_df.merge(tab_gor_hast_var, on='Ekip No', how='outer')
            merged_df = merged_df.merge(hast_bulunma, on='Ekip No', how='outer')
            merged_df.fillna(0, inplace=True)

            merged_df['Onaylı Oranı']= round(merged_df['Onaylı']/merged_df['Toplam Vaka'] * 100, 2)
            merged_df['Onaysız Oranı']= 100- merged_df['Onaylı Oranı']
            merged_df.sort_values(by='Onaysız Oranı', ascending=False, inplace=True)

            return merged_df

        # Function to generate HBYS hastane tablosu
        def hbys_hastane_tablosu():
            tabletten_gönderilmeyen= df_notablet.groupby(['Nakledilen Hastane']).agg({'Tabletten Gönderilme Tarih Saat':'sum'}).reset_index()
            tabletten_gönderilmeyen.rename(columns={'Tabletten Gönderilme Tarih Saat': 'Tabletten Gönderilmedi'},inplace=True)
            tabletten_gönderilen= df_tablet.groupby(['Nakledilen Hastane']).agg({'value':'sum'}).reset_index()
            tabletten_gönderilen.rename(columns={'value':'Tabletten Gönderilen'},inplace=True)
            onayli_sayisi= df_tablet.groupby(['Nakledilen Hastane', 'Onaylı']).agg({'value':'sum'}).reset_index()
            onayli= onayli_sayisi[onayli_sayisi['Onaylı']=='Evet']
            onayli.drop(columns='Onaylı', inplace=True)
            onaysiz= onayli_sayisi[onayli_sayisi['Onaylı']=='Hayır']
            onaysiz.drop(columns='Onaylı', inplace=True)
            onayli.rename(columns={'value':'Onaylı'},inplace=True)
            onaysiz.rename(columns={'value':'Onaysız'},inplace=True)
            #toplam_vaka= df_tablet.groupby('Nakledilen Hastane').agg({'value':'sum'})
            #toplam_vaka.rename(columns={'value':'Toplam Vaka'},inplace=True)
            onay_farki= df_onayli.groupby('Nakledilen Hastane').agg({'onay_farki':'mean'}).reset_index()
            onay_farki['onay_farki'].fillna(0, inplace=True)
            onay_farki['onay_farki']= onay_farki['onay_farki'].apply(format_timedelta)
            onay_farki.rename(columns={'onay_farki':'Doktor Onaylama Süresi'},inplace=True)


            merged_df = tabletten_gönderilen.merge(tabletten_gönderilmeyen, on='Nakledilen Hastane', how='outer')
            merged_df = merged_df.merge(onayli, on='Nakledilen Hastane', how='outer')
            merged_df = merged_df.merge(onaysiz, on='Nakledilen Hastane', how='outer')
            merged_df['Tabletten Gönderilen'].fillna(0,inplace=True)
            merged_df['Tabletten Gönderilmedi'].fillna(0,inplace=True)
            merged_df['Tabletten Gönderilen']= merged_df['Tabletten Gönderilen'].astype('int32')
            merged_df['Tabletten Gönderilmedi']= merged_df['Tabletten Gönderilmedi'].astype('int32')
            merged_df['Toplam Vaka']= merged_df['Tabletten Gönderilen'] + merged_df['Tabletten Gönderilmedi']
            merged_df = merged_df.merge(onay_farki, on='Nakledilen Hastane', how='outer')
            merged_df.fillna(0, inplace=True)
            merged_df['Onaylı Oranı']= round(merged_df['Onaylı']/merged_df['Tabletten Gönderilen'] * 100, 2)
            merged_df['Onaysız Oranı']= 100- merged_df['Onaylı Oranı']
            merged_df.sort_values(by='Onaysız Oranı', ascending=False, inplace=True)
            merged_df.rename(columns= {'Onaysız':'Tabletten Gönderilen Onaysız'}, inplace=True)

            return merged_df
    
        # Save reports
        df_ekip_hbys = hbys_ekip_tablosu()
        df_hastane_hbys = hbys_hastane_tablosu()

        df_ekip_hbys.to_excel(os.path.join(current_dir, 'HBYS_Ekip_Tablosu.xlsx'), index=False)
        df_hastane_hbys.to_excel(os.path.join(current_dir, 'HBYS_Hastane_Tablosu.xlsx'), index=False)

        messagebox.showinfo("Success", "Rapor Başarıyla Oluşturuldu!")

# Start the program
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window until unlocked

    lock_manager = LockManager()
    
    if not lock_manager.prompt_unlock_code():
        sys.exit()

    # If unlocked, show the main program
    root.deiconify()
    messagebox.showinfo("Welcome", "The program is now unlocked and running!")

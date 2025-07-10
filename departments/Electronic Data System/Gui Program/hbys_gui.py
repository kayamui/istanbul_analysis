import pandas as pd
import numpy as np
import plotly.express as px
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
MAX_FAILED_ATTEMPTS = 5  # Lock forever after 5 failed attempts
REGISTRY_PATH = r"Software\MyApp\LockStatus"
SECRET_KEY = "O Romeo, Romeo! wherefore art thou Romeo?"  # Used for hashing

class LockManager:
    def __init__(self):

        # Get the directory where the script is running
        self.program_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  
        self.guid_file = os.path.join(self.program_dir, "registration.txt")  

        self.machine_guid = self.get_machine_guid()
        self.store_machine_guid_in_registry()
        self.create_machine_guid= self.get_or_create_machine_guid()

    def get_machine_guid(self):
        """Retrieve the unique Machine GUID from the Windows registry."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ) as key:
                return winreg.QueryValueEx(key, "MachineGuid")[0]
        except Exception as e:
            print(f"Failed to retrieve Machine GUID: {e}")
            return "UnknownMachine"
        
    def get_or_create_machine_guid(self):
        """Ensure the machine_guid.txt file exists and contains the Machine GUID."""
        if os.path.exists(self.guid_file):
            with open(self.guid_file, "r") as file:
                return file.read().strip()

        # Generate and store Machine GUID
        registration_code = self.get_machine_guid()
        with open(self.guid_file, "w") as file:
            file.write(registration_code)

        messagebox.showinfo("Registration Code Created", 
                            f"A file 'registration.txt' has been created in:\n{self.program_dir}\n"
                            "Please send this file to the muhammedkaya65@gmail.com for an unlock code.")
        
        return registration_code
    
    def store_machine_guid_in_registry(self):
        """Store Machine GUID in Windows Registry to prevent modifications."""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH) as key:
                winreg.SetValueEx(key, 'MachineGUID', 0, winreg.REG_SZ, self.machine_guid)
        except Exception as e:
            print(f"Failed to store Machine GUID in registry: {e}")

    def hash_value(self, value):
        """Generate a SHA256 hash for a given value."""
        return hashlib.sha256((value + SECRET_KEY).encode()).hexdigest()

    def get_registry_value(self, name):
        """Retrieve a registry value and verify its integrity."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH, 0, winreg.KEY_READ) as key:
                stored_value, _ = winreg.QueryValueEx(key, name)
                stored_hash, _ = winreg.QueryValueEx(key, name + "_hash")
                
                # Verify the integrity of the stored value
                if self.hash_value(stored_value) != stored_hash:
                    messagebox.showerror("Security Alert", "Registry tampering detected. The program is permanently locked.")
                    self.permanently_lock()
                
                return stored_value
        except FileNotFoundError:
            return None

    def set_registry_value(self, name, value):
        """Store a value in the registry with a hash to prevent tampering."""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
                winreg.SetValueEx(key, name + "_hash", 0, winreg.REG_SZ, self.hash_value(str(value)))
        except Exception as e:
            print(f"Failed to store {name} in registry: {e}")

    def get_last_unlock_date(self):
        """Retrieve the last unlock date from the registry."""
        last_unlock_str = self.get_registry_value('LastUnlockDate')
        if last_unlock_str:
            try:
                return dt.datetime.strptime(last_unlock_str, "%Y-%m-%d")
            except ValueError:
                return None
        return None

    def store_unlock_date(self):
        """Save the current date as the last unlock date in the registry."""
        self.set_registry_value('LastUnlockDate', dt.datetime.now().strftime("%Y-%m-%d"))
        self.set_registry_value('FailedAttempts', 0)  # Reset failed attempts on successful unlock

    def get_failed_attempts(self):
        """Retrieve the number of failed attempts from the registry."""
        failed_attempts = self.get_registry_value('FailedAttempts')
        return int(failed_attempts) if failed_attempts is not None else 0

    def increment_failed_attempts(self):
        """Increment failed attempts in the registry and check for tampering."""
        failed_attempts = self.get_failed_attempts() + 1
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            self.permanently_lock()
        else:
            self.set_registry_value('FailedAttempts', failed_attempts)

    def permanently_lock(self):
        """Permanently lock the program by setting a flag in the registry."""
        messagebox.showerror("Permanently Locked", "Too many failed attempts. The program is permanently locked.")
        self.set_registry_value('PermanentlyLocked', 'True')
        sys.exit()

    def is_permanently_locked(self):
        """Check if the program is permanently locked due to excessive failed attempts."""
        return self.get_registry_value('PermanentlyLocked') == 'True'

    def is_unlocked_recently(self):
        """Check if the program was unlocked within the last 6 months."""
        last_unlock_date = self.get_last_unlock_date()
        return last_unlock_date and (dt.datetime.now() - last_unlock_date).days <= LOCK_PERIOD_DAYS

    def generate_unlock_code(self):
        """Generate an unlock code that changes every 5 minutes and is unique per computer."""
        current_time = dt.datetime.now()
        rounded_minutes = (current_time.minute // 5) * 5  # Round to nearest 5-minute mark
        time_string = f"{current_time.year}-{current_time.month}-{current_time.day} {current_time.hour}:{rounded_minutes:02d}"

        unlock_string = time_string + SECRET_KEY + self.machine_guid
        return hashlib.sha256(unlock_string.encode()).hexdigest()[:8]  # Shortened hash

    def prompt_unlock_code(self):
        """Ask the user for an unlock code and validate it."""
        if self.is_permanently_locked():
            messagebox.showerror("Permanently Locked", "The program has been permanently locked due to too many failed attempts.")
            sys.exit()

        if self.is_unlocked_recently():
            return True  # No need to ask for the unlock code

        while True:
            unlock_code = simpledialog.askstring("Unlock Required", "Please enter the unlock code provided by the administrator:")

            if unlock_code:
                if unlock_code == self.generate_unlock_code():
                    self.store_unlock_date()  # Store unlock date for 6-month validity
                    messagebox.showinfo("Success", "Program unlocked successfully!")
                    return True  # Unlock successful
                else:
                    self.increment_failed_attempts()
                    remaining_attempts = MAX_FAILED_ATTEMPTS - self.get_failed_attempts()
                    if self.is_permanently_locked():
                        messagebox.showerror("Permanently Locked", "The program is now permanently locked due to too many failed attempts.")
                        sys.exit()
                    else:
                        messagebox.showerror("Invalid Code", f"Incorrect unlock code. {remaining_attempts} attempts remaining.")
            else:
                messagebox.showinfo("Exiting", "No unlock code entered. Exiting program.")
                sys.exit()

    def is_locked(self):
        """Check if the program is locked."""
        return not self.is_unlocked_recently()


class App:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Ensure complete exit on close
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
        """Close splash and start the main program."""
        self.splash_screen.destroy()
        self.run_main_program()

    def run_main_program(self):
        """Generate HBYS reports."""

        current_dir = os.path.abspath(os.getcwd())

        files = [f for f in os.listdir(current_dir) if 'Genel Vaka Araştırma' in f ]

        if not files:
            messagebox.showerror("Error", "No 'Genel Vaka Araştırma' file found!")
            sys.exit()

        now = str(dt.datetime.now().date())

        # CREATE A NEW DIRECTORY
        directory_name = f"{now} HBYS Analizi"
        directory_path = current_dir + '\\' + directory_name + '\\'

        # Use os.path.exists() to check if directory exists
        if not os.path.exists(directory_name):  
            os.makedirs(current_dir + '\\' + directory_name)
            messagebox.showinfo(f'Directory',f'{directory_name} created successfully.')
        else:
            messagebox.showinfo(f'Directory',f'{directory_name} already exists.')



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
            onayli.rename(columns={'value':'Toplam Onaylı'},inplace=True)
            onaysiz.rename(columns={'value':'Toplam Onaysız'},inplace=True)
            toplam_vaka= df_eylul.groupby('Ekip No').agg({'value':'sum'})
            toplam_vaka.rename(columns={'value':'Toplam Vaka'},inplace=True)
            onay_farki= df_onayli.groupby('Ekip No').agg({'onay_farki':'mean'}).reset_index()


            onay_farki['onay_farki'].fillna(0, inplace=True)
            onay_farki.rename(columns={'onay_farki':'Doktor Onaylama Süresi'},inplace=True)

            hast_ayr_tab= df_onayli.groupby('Ekip No').agg({'Hastaneden Ayrılış - Tabletten Gönderilme Tarihi':'mean'}).reset_index()
            tab_gor_hast_var= df_hast_var.groupby('Ekip No').agg({'Tabletten Gönderilme - Hastaneye Varış Tarihi':'mean'}).reset_index()
            hast_bulunma= df_onayli.groupby('Ekip No').agg({'Hastanede Bulunma Süresi':'mean'}).reset_index()

            merged_df = tabletten_gönderilen.merge(tabletten_gönderilmeyen, on='Ekip No', how='outer')
            merged_df = merged_df.merge(onayli, on='Ekip No', how='outer')
            merged_df = merged_df.merge(onaysiz, on='Ekip No', how='outer')
            merged_df['Tabletten Gönderilen Onaysız']= merged_df['Tabletten Gönderilen'] - merged_df['Toplam Onaylı']
            merged_df = merged_df.merge(toplam_vaka, on='Ekip No', how='outer')
            merged_df = merged_df.merge(onay_farki, on='Ekip No', how='outer')
            merged_df = merged_df.merge(hast_ayr_tab, on='Ekip No', how='outer')
            merged_df = merged_df.merge(tab_gor_hast_var, on='Ekip No', how='outer')
            merged_df = merged_df.merge(hast_bulunma, on='Ekip No', how='outer')
            merged_df.fillna(0, inplace=True)
            merged_df.set_index('Ekip No', inplace=True)
            merged_df.loc['Toplam']= [merged_df['Tabletten Gönderilen'].sum(), 
                                    merged_df['Tabletten Gönderilmedi'].sum(), 
                                    merged_df['Toplam Onaylı'].sum(), 
                                    merged_df['Toplam Onaysız'].sum(), 
                                    merged_df['Tabletten Gönderilen Onaysız'].sum(),
                                    merged_df['Toplam Vaka'].sum(),
                                    # Convert the 'Doktor Onaylama Süresi'
                                    merged_df['Doktor Onaylama Süresi'].mean(), 
                                    # Convert the 'Hastaneden Ayrılış - Tabletten Gönderilme Tarihi' 
                                    merged_df['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi'].mean(), 
                                    # Convert the 'Tabletten Gönderilme - Hastaneye Varış Tarihi' 
                                    merged_df['Tabletten Gönderilme - Hastaneye Varış Tarihi'].mean(),
                                    # Convert the 'Hastanede Bulunma Süresi'
                                    merged_df['Hastanede Bulunma Süresi'].mean()
                                    ]
            
            
            merged_df['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi']= merged_df['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi'].apply(format_timedelta)
            merged_df['Tabletten Gönderilme - Hastaneye Varış Tarihi']= merged_df['Tabletten Gönderilme - Hastaneye Varış Tarihi'].apply(format_timedelta)
            merged_df['Hastanede Bulunma Süresi']= merged_df['Hastanede Bulunma Süresi'].apply(format_timedelta)
            merged_df['Doktor Onaylama Süresi']= merged_df['Doktor Onaylama Süresi'].apply(format_timedelta)

            merged_df['Onaylı Oranı']= round(merged_df['Toplam Onaylı']/merged_df['Tabletten Gönderilen'] * 100, 2)
            merged_df['Onaysız Oranı']= 100- merged_df['Onaylı Oranı']
            merged_df.reset_index(inplace=True)

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
            onay_farki= df_onayli.groupby('Nakledilen Hastane').agg({'onay_farki':'mean'}).reset_index()
            onay_farki['onay_farki'].fillna(0, inplace=True)
            #onay_farki['onay_farki']= onay_farki['onay_farki'].apply(format_timedelta)
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
            merged_df.set_index('Nakledilen Hastane', inplace=True)
            merged_df.loc['Toplam']= [merged_df['Tabletten Gönderilen'].sum(), 
                                    merged_df['Tabletten Gönderilmedi'].sum(), 
                                    merged_df['Onaylı'].sum(), 
                                    merged_df['Onaysız'].sum(), 
                                    merged_df['Toplam Vaka'].sum(),
                                    merged_df['Doktor Onaylama Süresi'].mean()]
            merged_df['Doktor Onaylama Süresi']= merged_df['Doktor Onaylama Süresi'].apply(format_timedelta)
            merged_df['Onaylı Oranı']= round(merged_df['Onaylı']/merged_df['Tabletten Gönderilen'] * 100, 2)
            merged_df['Onaysız Oranı']= 100- merged_df['Onaylı Oranı']
            merged_df.rename(columns= {'Onaysız':'Tabletten Gönderilen Onaysız'}, inplace=True)
            merged_df.reset_index(inplace=True)

            return merged_df
    
        # Save reports
        df_ekip_hbys = hbys_ekip_tablosu()
        df_hastane_hbys = hbys_hastane_tablosu()

        df_ekip_hbys.to_excel(os.path.join(directory_path, f'{now} HBYS_Ekip_Tablosu.xlsx'), index=False)
        df_hastane_hbys.to_excel(os.path.join(directory_path, f'{now} HBYS_Hastane_Tablosu.xlsx'), index=False)


        df_hastane_hbys_filtered= df_hastane_hbys[df_hastane_hbys['Nakledilen Hastane'] != '-']

        def get_minutes(row):
            splitted_row = row.split(':')
            try:
                if int(splitted_row[0]) < 0:
                    minutes = round((int(splitted_row[0])) * 60 + (-1* int(splitted_row[1])) + (-1 * int(splitted_row[2]) / 60), 2)
                else:
                    minutes = round(int(splitted_row[0]) * 60 + int(splitted_row[1]) + int(splitted_row[2]) / 60, 2)
                return minutes
            except:
                return row

        df_hastane_hbys_minutes_filtered= df_hastane_hbys.copy()
        df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi']= df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi'].astype(str)
        df_hastane_hbys_minutes_filtered= df_hastane_hbys_minutes_filtered[df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi'] != '0']
        df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi Dk']= df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi'].apply(get_minutes)
        df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi Dk'] = df_hastane_hbys_minutes_filtered['Doktor Onaylama Süresi Dk'].astype(float)
        
        df_ekip_hbys_filtered= df_ekip_hbys[df_ekip_hbys['Tabletten Gönderilen']!= 0] 
        df_ekip_hbys_filtered['Hastanede Bulunma Süresi Dk']= df_ekip_hbys_filtered['Hastanede Bulunma Süresi'].astype(str).apply(get_minutes)
        df_ekip_hbys_filtered['Toplam Vaka']= df_ekip_hbys_filtered['Toplam Vaka'].astype(int)
        df_ekip_hbys_filtered['Hastanede Bulunma Süresi Dk']= df_ekip_hbys_filtered['Hastanede Bulunma Süresi Dk'].astype(float)
        df_ekip_hbys_filtered['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi Dk']= df_ekip_hbys_filtered['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi'].astype(str).apply(get_minutes)
        df_ekip_hbys_filtered['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi Dk']= df_ekip_hbys_filtered['Hastaneden Ayrılış - Tabletten Gönderilme Tarihi Dk'].astype(float)

        
        messagebox.showinfo("Success", "Rapor Başarıyla Oluşturuldu!")

    def on_close(self):
        """Ensure the program fully exits when closed."""
        self.root.quit()  # Stop Tkinter main loop
        self.root.destroy()  # Destroy the window
        sys.exit()  # Ensure full exit

# Start the program
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially

    # Initialize LockManager and check for unlock
    lock_manager = LockManager()

    if lock_manager.is_locked():
        if not lock_manager.prompt_unlock_code():
            sys.exit()  # If unlocking fails, exit

    # If unlocked, start the GUI
    root.deiconify()
    app = App(root)
    root.mainloop()
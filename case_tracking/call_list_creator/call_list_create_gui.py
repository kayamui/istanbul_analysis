# THE GUI CODE
import pandas as pd
import warnings
import os
import datetime as dt
import sys
import hashlib
import winreg
import tkinter as tk
from tkinter import messagebox, simpledialog
import ctypes


warnings.filterwarnings('ignore')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


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

        tk.Label(self.splash_screen, text="ÇAĞRI OLUŞTURUCU", font=("Helvetica", 24, "bold"), fg="#333", bg="#f0f4f7").pack(pady=80)
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

        messagebox.showinfo('Dosyaları Bulundur', 'İhbar İşlemleri, Personel Nöbet Listesi,eu_team_code')
        
        current_dir =os.path.abspath(os.getcwd()) #os.path.abspath(os.getcwd())  #os.path.abspath(os.getcwd())  #'C:/Users/mkaya/Onedrive/Belgeler/GitHub/istanbul_analysis/case_tracking/call_list_creator/'

        shift_list_file= [x for x in os.listdir(current_dir) if 'Personel-Nöbet-Listesi' in x]
        
        cases_file= [t for t in os.listdir(current_dir) if 'İhbar işlemleri' in t]


        if not shift_list_file:
            messagebox.showerror("Hata", "Personel Nöbet Listesi dosyasını yükleyin!")
            sys.exit()

        if not cases_file:
            messagebox.showerror("Hata", "İhbar işlemleri dosyasını yükleyin!")
            sys.exit()

        now = str(dt.datetime.now().date())

        # CREATE A NEW DIRECTORY
        directory_name = f"{now} Arama Listesi"
        directory_path = current_dir + '/' + directory_name + '/'

        # Use os.path.exists() to check if directory exists
        if not os.path.exists(current_dir+directory_name):
            os.makedirs(current_dir + '/' + directory_name)
        else:
            pass


        shift_list= pd.read_excel(os.path.join(current_dir, shift_list_file[0])) #pd.read_excel(os.path.join(current_dir, shift_list_file[0])) #pd.read_excel('C:/Users/mkaya/Onedrive/Belgeler/GitHub/istanbul_analysis/case_tracking/call_list_creator/Personel-Nöbet-Listesi (15).xls')
        #pd.read_excel(os.path.join(current_dir, keyword_team_code_file[0])) #pd.read_excel('C:/Users/mkaya/Onedrive/Belgeler/GitHub/istanbul_analysis/case_tracking/call_list_creator/eu_team_code.xlsx')
        #keyword_team_dict=dict(zip(keyword_team_code['112ONLINE'].astype(str).str.strip(), keyword_team_code['ASOS'].astype(str).str.strip()))
        df_cases= pd.read_excel(os.path.join(current_dir, cases_file[0])) #pd.read_excel(os.path.join(current_dir, cases_file[0])) #pd.read_excel('C:/Users/mkaya/Onedrive/Belgeler/GitHub/istanbul_analysis/case_tracking/call_list_creator/İhbar işlemleri (81).xls')

        def team_code_update():
            team_code_update_file = [u for u in os.listdir(current_dir) if 'İmza Atan Personel' in u]
            keyword_team_code_file= [y for y in os.listdir(current_dir) if 'eu_team_code' in y]

            if team_code_update_file:
                # Read the new team code update file
                team_code_update_df = pd.read_excel(os.path.join(current_dir, team_code_update_file[0]))
                team_code_update_df= team_code_update_df[['Ekip Adı', 'Ekip Kodu']]
                
                # Create the updated dictionary
                updated_dict = dict(
                    zip(
                        team_code_update_df['Ekip Adı'].astype(str).str.strip(),
                        team_code_update_df['Ekip Kodu'].astype(str).str.strip()
                    )
                )

                # Avoid duplicates with the same key-value pairs
                cleaned_dict = {}
                for k, v in updated_dict.items():
                    if k not in cleaned_dict or cleaned_dict[k] != v:
                        cleaned_dict[k] = v

                # Save the updated file with new column names
                team_code_update_df.rename(columns={'Ekip Kodu': 'ASOS', 'Ekip Adı': '112ONLINE'}, inplace=True)
                team_code_update_df.to_excel(current_dir + '\\' +'eu_team_code.xlsx', index=False)

                messagebox.showinfo('Güncelleme', 'Ekip Kodları Güncellendi!')
                return cleaned_dict
            else:
                if keyword_team_code_file:
                    keyword_team_code= pd.read_excel(os.path.join(current_dir, keyword_team_code_file[0]))

                    # Fallback to original keyword_team_code
                    fallback_dict = dict(
                        zip(
                            keyword_team_code['112ONLINE'].astype(str).str.strip(),
                            keyword_team_code['ASOS'].astype(str).str.strip()
                        )
                    )

                    return fallback_dict
                else:
                    messagebox.showerror("Hata", "İmza Atan Personel Raporu dosyasını yükleyin!")
                    sys.exit()

            messagebox.showerror("Hata", "İmza Atan Personel Raporu dosyasını yükleyin!")
            sys.exit()
            
        keyword_team_dict= team_code_update()
        

        def get_team_code_match(row):
            try:
                return keyword_team_dict[row]
            except:
                return 'row'

        def shift_list_cleaning(shift_list):
            distinct_index = []
            station_name = []

            # Loop through the DataFrame to detect changes
            for i in range(1, len(shift_list)-1):
                current_val = shift_list.iloc[i]['Unnamed: 1']
                previous_val = shift_list.iloc[i-1]['Unnamed: 1']
                after_val = shift_list.iloc[i+1]['Unnamed: 1']

                if pd.notna(current_val) and pd.isna(previous_val) and pd.isna(after_val):
                    distinct_index.append(i)
                    station_name.append(current_val)

            # Add an artificial "end" index to help with slicing
            distinct_index.append(len(shift_list))

            # Assign station names to the relevant rows
            for i in range(len(station_name)):
                shift_list.loc[distinct_index[i]:distinct_index[i+1]-1, 'Unnamed: 15'] = station_name[i]

            shift_list.columns= shift_list.iloc[6]
            shift_list.drop([0,1,2,3,4,5,6], inplace=True)

            shift_list.rename(columns={shift_list.columns[15]:'Ekip No'}, inplace=True)
            shift_list= shift_list[(shift_list['İsim']!= 'İsim') & shift_list['İsim'].notna()]
            shift_list= shift_list.loc[:, shift_list.columns.notna()]
            shift_list['Ekip No']= shift_list['Ekip No'].astype(str).str.strip()

            shift_list['Ekip No']= shift_list['Ekip No'].astype(str).str.strip().apply(get_team_code_match)
            shift_list= shift_list[shift_list['Görev'].isin(['Ekip Sorumlusu','Yardımcı Sağlık Personeli','Sürücü'])]
            sort_list= ['Ekip Sorumlusu','Yardımcı Sağlık Personeli','Sürücü']
            shift_list['Görev']= pd.Categorical(shift_list['Görev'], categories=sort_list, ordered=True)
            shift_list['İsim Soyisim'] = shift_list['İsim'] + ' ' + shift_list['Soyisim']
            shift_list.drop(columns=['İsim', 'Soyisim'], inplace=True)
            shift_list['İsim Soyisim']= shift_list['İsim Soyisim'] + ' - ' + shift_list['Görev'].astype(str)
            #shift_list.drop(columns=['Görev'], inplace=True)

            shift_list['İsim Soyisim']= shift_list['İsim Soyisim'] + ' - ' +shift_list['Telefon'] 
            shift_list.drop(columns=['Telefon'], inplace=True)

            shift_list= shift_list[shift_list['Ekip No'] != 'row']
            shift_list.insert(1, 'İsim Soyisim',shift_list.pop('İsim Soyisim'))

            shift_list.reset_index(drop=True, inplace=True)

            return shift_list

        shift_list= shift_list_cleaning(shift_list)

        def call_filter(df_cases, keyword_team_dict):
            #Left only necessary columns

            df_cases.drop(columns = ['KKM Seri No', 'Adres', 'Vaka Yeri Açıklaması'], inplace = True)
            df_cases.rename(columns={'Ekip Kodu': 'Ekip No'}, inplace=True)

            df_cases['Ekip No']= df_cases['Ekip No'].astype(str).str.strip()
            df_cases= df_cases[df_cases['Ekip No'].isin(keyword_team_dict.values())]
            
            df_cases['KKM Protokol']= df_cases['KKM Protokol'].astype(int)

            df_cases['Tarih']= pd.to_datetime(df_cases['Tarih'], format='%d-%m-%Y %H:%M')
            df_cases = df_cases[['KKM Protokol', 'Ekip No', 'Tarih', 'Durum']]       

            return df_cases
        
        merged_df= call_filter(df_cases, keyword_team_dict)  

        def filter_data(merged_df):
            option = messagebox.askquestion(
                "Filter Option",
                "Tek bir nöbet gününü mü çıkarmak istiyorsunuz?"
                )
            if option == 'yes':
                filtered_df= pd.DataFrame()
                try:
                    year = int(simpledialog.askstring("Input", "Yıl:", parent=root))
                    month = int(simpledialog.askstring("Input", "Ay:", parent=root))
                    day = int(simpledialog.askstring("Input", "Gün:", parent=root))
                    hour = int(simpledialog.askstring("Input", "Saat:", parent=root))

                    start_date = dt.datetime(year, month, day, hour)
                    end_date = start_date + dt.timedelta(days=1)

                    filtered_df = pd.concat([filtered_df, merged_df[(merged_df['Tarih'] >= start_date) & (merged_df['Tarih'] < end_date)]], ignore_index=True)

                    for i in range(1, 9):
                        try:
                            start_date += dt.timedelta(days=4)
                            end_date = start_date + dt.timedelta(days=1)

                            temp_df = merged_df[
                                (merged_df['Tarih'] >= start_date) & (merged_df['Tarih'] < end_date)
                            ]
                            filtered_df = pd.concat([filtered_df, temp_df], ignore_index=True)
                        except Exception as e:
                            messagebox.showerror("Error", "Invalid input: {e}")
                            return None

                    return filtered_df
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid input: {e}")
                    return None
            else:
                return merged_df

        
        df_unmatched= filter_data(merged_df)
        
        def match_call_list(df_unmatched,shift_list):
            unmatch_merged= pd.merge(df_unmatched, shift_list, on=['Ekip No'], how = 'outer')
            
            unmatch_merged['Başlangıç Tarihi']= pd.to_datetime(unmatch_merged['Başlangıç Tarihi'], format='%d-%m-%Y %H:%M')
            unmatch_merged['Bitiş Tarihi']= pd.to_datetime(unmatch_merged['Bitiş Tarihi'], format='%d-%m-%Y %H:%M')
            unmatch_merged['Tarih']= pd.to_datetime(unmatch_merged['Tarih'], format='%d-%m-%Y %H:%M')
            unmatch_merged['is_date_between']= unmatch_merged.apply(lambda x: x['Başlangıç Tarihi'] <= x['Tarih'] <= x['Bitiş Tarihi'], axis=1)
            unmatch_merged= unmatch_merged[unmatch_merged['is_date_between']==True]
            unmatch_merged.sort_values(by='Görev', inplace=True)
            
            # Fix: Handle NaN values before joining
            def safe_join(series):
                # Convert to string and filter out NaN values
                valid_values = series.dropna().astype(str)
                return ','.join(valid_values)
            
            unmatch_merged= unmatch_merged.groupby(['KKM Protokol', 'Ekip No', 'Tarih', 'Durum']).agg({'İsim Soyisim': safe_join}).reset_index()
            unmatch_merged['KKM Protokol']= unmatch_merged['KKM Protokol'].astype(int)

            unmatch_merged['İsim Soyisim']= unmatch_merged['İsim Soyisim'].str.split(',')
            names_split= unmatch_merged['İsim Soyisim'].apply(pd.Series)
            name= 'isim'
            names_split.columns= [f'{name}{i+1}' for i in range(names_split.shape[1])]
            unmatch_merged= pd.concat([unmatch_merged, names_split], axis=1)
            unmatch_merged.drop(columns=['İsim Soyisim'], inplace=True)
            unmatch_merged.sort_values(by='isim1', ascending=True,inplace=True)
            unmatch_merged.reset_index(drop=True, inplace=True)
            
            return unmatch_merged
        
        df= match_call_list(df_unmatched,shift_list)
        df.to_excel(directory_path + f'{now} Arama Listesi.xlsx')
        success_message= messagebox.showinfo('Kayıt', 'Arama Listesi Oluşturuldu!')
        return success_message
        

    def on_close(self):
        """Ensure the program fully exits when closed."""
        self.root.quit()  # Stop Tkinter main loop
        self.root.destroy()  # Destroy the window
        sys.exit()  # Ensure full exit

# Start the program
if __name__ == "__main__":
    root = tk.Tk()
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    icon_path = resource_path("app_icon.ico") #C:/Users/mkaya/Onedrive/Belgeler/GitHub/istanbul_analysis/case_tracking/call_list_creator/
    root.iconbitmap(icon_path)

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
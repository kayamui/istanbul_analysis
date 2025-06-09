# SECONDARY TRANSPORTS STATISTICS
import pandas as pd
import os
import datetime as dt
import ctypes

import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, simpledialog
from tkinter import ttk

import threading

import pandas as pd
import numpy as np
import shutil
import hashlib  # To handle unlock code generation via hashing
from tkinter import messagebox  # To display error/info dialogs in the GUI
from cryptography.fernet import Fernet
import sys
import subprocess
import time
import atexit
import winreg
import openpyxl
from openpyxl.styles import PatternFill

import queue

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


class AmbulanceApp:

    def __init__(self, root):
        # Assign the root window to self.root
        self.root = root

        # Initialize LockManager
        self.lock_manager = LockManager()

        # Set up the window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle the window close event

        self.root.withdraw()  # Hide the main window during the splash screen
        self.show_splash_screen()
        self.root.after(5000, self.end_splash_screen)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
            self.root.destroy()  # Ensure the app is fully closed

    def show_splash_screen(self):
        # Create splash screen window
        self.splash_screen = tk.Toplevel(self.root)
        self.splash_screen.overrideredirect(True)  # Borderless window
        self.splash_screen.geometry("800x400+300+200")  # Set window size and position
        self.splash_screen.configure(bg='#f0f4f7')  # Light background color

        # Centered title "Vaka Yoğunluk Grafikeri"
        self.title_label = tk.Label(self.splash_screen, text="Mükerrer Nakil Çalışması", font=("Helvetica", 24, "bold"), fg="#333", bg="#f0f4f7")
        self.title_label.pack(pady=80)

        # Dedication message fitted above the bottom text
        self.dedication_message = (
            "İstanbul İl Ambulans Servisi"
        )
        self.dedication_label = tk.Label(self.splash_screen, text=self.dedication_message, font=("Helvetica", 10, "italic"), fg="#555", bg="#f0f4f7", wraplength=750, justify="center")
        self.dedication_label.pack(side="bottom", pady=(0, 40))  # Add padding to prevent overlap with bottom texts

        # Bottom left: "Avrupa 112" in minimal and light font
        self.left_label = tk.Label(self.splash_screen, text="Muhammed KAYA", font=("Helvetica", 12), fg="#333", bg="#f0f4f7")
        self.left_label.place(x=20, y=360)

        # Bottom right: "Muhammed Kaya" in a bolder font
        self.right_label = tk.Label(self.splash_screen, text="Avrupa 112", font=("Helvetica", 12), fg="#333", bg="#f0f4f7")
        self.right_label.place(x=650, y=360)

        # Destroy the splash screen after 5 seconds
        self.splash_screen.after(5000, self.end_splash_screen)

    def end_splash_screen(self):
        # Destroy the splash screen and show the main window
        self.splash_screen.destroy()
        self.root.deiconify()  # Show the main window after splash screen
        self.create_widgets()  # Call create_widgets only once here


    def create_widgets(self):
        # Set the window title
        self.root.title("Avrupa 112 - Muhammed Kaya")

        # Set the window size to be larger
        self.root.geometry("900x600")  # Adjust the size as needed

        # Configure a new style for rounded buttons
        style = ttk.Style()
        style.theme_use("clam")  # Use the 'clam' theme for modern look
        style.configure("Rounded.TButton", font=("Helvetica", 10), padding=10, relief="flat", borderwidth=1, width=20, anchor="center")
        style.map("Rounded.TButton", background=[("active", "#b3cde0")])  # Color change on hover

        # Initialize a list to hold the paths of loaded files and their regions
        self.loaded_files = []

        # Status label (placed first to ensure it's available before being referenced)
        self.status_label = tk.Label(self.root, text="Durum: Veri bekleniyor...", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        # Ensure only one instance of each widget is created
        if not hasattr(self, 'load_files_button'):
            # Load Multiple Files button with same size and smaller text
            self.load_files_button = ttk.Button(self.root, text="Dosyaları Yükle", command=self.load_multiple_files, style="Rounded.TButton")
            self.load_files_button.pack(pady=10)

        if not hasattr(self, 'delete_file_button'):
            # Delete Selected File button with same size and smaller text
            self.delete_file_button = ttk.Button(self.root, text="Dosyayı Sil", command=self.delete_selected_file, style="Rounded.TButton")
            self.delete_file_button.pack(pady=10)

        if not hasattr(self, 'save_path_button'):
            # Choose Save Path button with same size and smaller text
            self.save_path_button = ttk.Button(self.root, text="Kaydetme Konumu", command=self.choose_save_path, style="Rounded.TButton")
            self.save_path_button.pack(pady=10)

        if not hasattr(self, 'generate_graphs_button'):
            # Generate Graphs button with same size and smaller text
            self.generate_graphs_button = ttk.Button(self.root, text="Başla", state=tk.DISABLED, command=self.start_generate_graphs_thread, style="Rounded.TButton")
            self.generate_graphs_button.pack(pady=10)

        if not hasattr(self, 'file_listbox'):
            # File listbox to display selected files (allows user to see uploaded files)
            self.file_listbox = Listbox(self.root, width=80, height=8, font=("Helvetica", 10))
            self.file_listbox.pack(pady=10)

        if not hasattr(self, 'progress'):
            # Progress bar
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="indeterminate")
            self.progress.pack(pady=10)


    def load_multiple_files(self):
        """Allow user to select multiple files and load them into the program, with region selection for each."""
        files = filedialog.askopenfilenames(title="Dosya Seç", filetypes=[("All Files", "*.*")])

        if not files:
            messagebox.showerror("Error", "No files selected.")
            return

        if files:
            total_files = len(files)
            self.progress["value"] = 0
            self.progress["maximum"] = total_files

            self.status_label.config(text="Loading files...")

            try:
                for index, file in enumerate(files):
                    self.status_label.config(text=f"Loading {index+1} of {total_files} files...")

                    # Prompt the user to select the region for each file
                    region = self.choose_region_dialog(file)

                    # Add file and region to the loaded_files list
                    self.loaded_files.append((file, region))

                    # Update the Listbox to show the file and region
                    self.file_listbox.insert(tk.END, f"{file.split('/')[-1]} ({region})")

                self.status_label.config(text="Files loaded successfully!")
                self.check_data_loaded()  # Check if the "Generate Graphs" button should be enabled

            except Exception as e:
                self.status_label.config(text="Error occurred during file loading.")
                messagebox.showerror("Error", f"Failed to load files: {e}")

            finally:
                self.progress.stop()


    def choose_region_dialog(self, file):
        """Open a dialog box with a dropdown menu for selecting Emergency(Sahadan Hastaneye Defter) or Internal Trasnports (Nakil Defter)."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Defter Tipi Seç {file.split('/')[-1]}")
        dialog.geometry("300x100")

        # Label for instructions
        label = ttk.Label(dialog, text="Bu dosya için defter tipi seç:", font=("Helvetica", 10))
        label.pack(pady=10)

        # Dropdown menu
        region_var = tk.StringVar(dialog)
        region_var.set("Sahadan Hastaneye Defter")  # Default value

        region_dropdown = ttk.OptionMenu(dialog, region_var, "Sahadan Hastaneye Defter", "Sahadan Hastaneye Defter", "Nakil Defter")
        region_dropdown.pack(pady=10)

        # Button to confirm selection
        def confirm_selection():
            dialog.destroy()

        confirm_button = ttk.Button(dialog, text="Confirm", command=confirm_selection)
        confirm_button.pack(pady=5)

        # Wait for the user to close the dialog
        dialog.grab_set()
        self.root.wait_window(dialog)

        return region_var.get()

    

    def delete_selected_file(self):
        """Delete the selected file from the listbox and the loaded_files list."""
        selected_file_index = self.file_listbox.curselection()

        if selected_file_index:
            selected_file = self.file_listbox.get(selected_file_index)
            # Remove from the loaded_files list
            for file, region in self.loaded_files:
                if f"{file.split('/')[-1]} ({region})" == selected_file:
                    self.loaded_files.remove((file, region))
                    break

            # Remove from the listbox
            self.file_listbox.delete(selected_file_index)
        else:
            messagebox.showwarning("Uyarı", "Silinecek dosya seçilmedi!")

    

    # Threads for loading and generating
    def start_load_europe_thread(self):
        """Start a separate thread to load Europe data."""
        self.progress.start()
        thread = threading.Thread(target=self.load_europe_data)
        thread.start()

    def start_load_asia_thread(self):
        """Start a separate thread to load Asia data."""
        self.progress.start()
        thread = threading.Thread(target=self.load_asia_data)
        thread.start()

    def start_generate_graphs_thread(self):
        """Start a separate thread to generate graphs."""
        self.progress.start()
        thread = threading.Thread(target=self.generate_graphs)
        thread.daemon = True  # Ensures thread will close when the main app closes
        thread.start()

    # Threads for loading and generating
    def start_load_europe_thread(self):
        """Start a separate thread to load Europe data."""
        self.progress.start()
        thread = threading.Thread(target=self.load_europe_data)
        thread.start()

    def start_load_asia_thread(self):
        """Start a separate thread to load Asia data."""
        self.progress.start()
        thread = threading.Thread(target=self.load_asia_data)
        thread.start()

    def start_generate_graphs_thread(self):
        """Start a separate thread to generate graphs."""
        self.progress.start()
        thread = threading.Thread(target=self.generate_graphs)
        thread.start()

    # File loading functions with progress handling
    def load_europe_data(self):
        europe_file = filedialog.askopenfilename(title="Sahadan Hastaneye Defter Seç", filetypes=[("All Files", "*.*")])

        if not europe_file:
            messagebox.showerror("Hata", "Lütfen Geçerli Bir Dosya Seç!")
            self.progress.stop()
            return

        try:
            self.df_europe = self.load_and_process_data(europe_file, 'Sahadan Hastaneye Defter')  # Fill this function
            self.status_label.config(text="Durum: Sahadan Hastaneye Defter Başarıyla Yüklendi!")

            # Show the selected Europe file in the listbox
            self.file_listbox.insert(tk.END, f"Sahadan Hastaneye Defter: {europe_file.split('/')[-1]}")

            self.check_data_loaded()
        except Exception as e:
            messagebox.showerror("Hata", f"Sahadan Hastaneye Defter yüklenemedi: {e}")
            self.status_label.config(text="Durum: Sahadan Hastaneye Defter yüklenemedi")
        finally:
            self.progress.stop()

    def load_asia_data(self):
        asia_file = filedialog.askopenfilename(title="Nakil Defter Seç", filetypes=[("All Files", "*.*")])

        if not asia_file:
            messagebox.showerror("Hata", "Lütfen Geçerli Bir Dosya Seç!")
            self.progress.stop()
            return

        try:
            self.df_asia = self.load_and_process_data(asia_file, 'Nakil Defter')  # Fill this function
            self.status_label.config(text="Durum: Nakil Defter Başarıyla Yüklendi!")

            # Show the selected Asia file in the listbox
            self.file_listbox.insert(tk.END, f"Nakil Defter: {asia_file.split('/')[-1]}")

            self.check_data_loaded()
        except Exception as e:
            messagebox.showerror("Hata", f"Nakil Defter yüklenemedi: {e}")
            self.status_label.config(text="Durum: Nakil Defter yüklenemedi")
        finally:
            self.progress.stop()
            
    def load_and_process_data(self, file_path, region):
        """This function loads and processes the data from the specified Excel file."""
        df = pd.read_excel(file_path)
        df['workbook'] = region  # Set region as 'Sahadan Hastaneye Defter' or 'Nakil Defter'

        return df

    def check_data_loaded(self):
        """Enable the Generate Graphs button if at least one file is loaded."""
        if self.loaded_files:
            self.generate_graphs_button.config(state=tk.NORMAL)


    def ask_string_main_thread(self, prompt_text):
        q = queue.Queue()

        def ask():
            result = simpledialog.askstring("Input", prompt_text, parent=self.root)
            q.put(result)

        self.root.after(0, ask)
        return q.get()  # Blocks the thread until input is given

    def generate_graphs(self):
        """Generate graphs for the loaded data with progress tracking and error handling."""
        if not self.save_path:
            messagebox.showerror("Error", "Please select a save path.")
            return
        
        if not os.path.isdir(self.save_path):
            messagebox.showerror("Error", "Invalid save path.")
            return        

        def update_progress():
            """Update the progress bar in the main thread."""
            self.progress["value"] += 1
            self.progress.update()

        def run_graph_generation():
            self.progress["value"] = 0
            self.progress.config(mode="determinate")  # Reset and switch to determinate mode
            try:
                if self.loaded_files:
                    total_files = len(self.loaded_files)
                    self.progress.config(mode='determinate')  # Switch to determinate mode
                    self.progress["value"] = 0  # Reset the progress bar
                    self.progress["maximum"] = total_files
                    self.status_label.config(text="Dosya oluşturuluyor...")

                    all_dfs = []

                    for index, (file, region) in enumerate(self.loaded_files):
                        try:
                            self.root.after(0, lambda: self.status_label.config(text="Mükerrer Nakil Çalışması Başlıyor..."))
                            df = self.load_and_process_data(file, region)
                            all_dfs.append(df)

                            # Update progress bar in the main thread
                            self.root.after(0, update_progress)

                        except FileNotFoundError as e:
                            messagebox.showerror("Error", f"File not found: {e}")
                            return  # Exit if a file is not found

                        except PermissionError as e:
                            messagebox.showerror("Permission Error", f"Permission denied when accessing file: {e}")
                            return  # Exit if permission is denied

                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred while processing {file}: {e}")
                            return  # Exit if any other error occurs
                        
                    df_internal_transports= pd.DataFrame()
                    df_reports= pd.DataFrame()
                    for file in all_dfs:
                        if file.iloc[0]['workbook']=='Sahadan Hastaneye Defter':
                            df_reports = pd.concat([df_reports, file])
                        else:
                            df_internal_transports= pd.concat([df_internal_transports, file])
                    
                    if df_internal_transports.empty:
                        return messagebox.showerror("Error", "No valid data available to generate file.")
                    
                    if df_reports.empty:
                        return messagebox.showerror("Error", "No valid data available to generate file.")


                    df_placed= df_internal_transports[df_internal_transports['Durum'] == 'Yer Ayarlandı'].copy()
                    df_reports.drop_duplicates(inplace=True)
                    df_placed.drop_duplicates(inplace=True)
                    df_reports['is_baby']= False
                    df_placed['is_baby']= False

                    df_reports.reset_index(inplace=True)
                    df_placed.reset_index(inplace=True)

                    df_reports.rename(columns= {'ICD10 TANI\nADI':'ICD10 TANI ADI'}, inplace=True)
                    reports_columns= ['İhbar/Çağrı Tarihi', 'İhbar/Çağrı  Saati', 'Hasta Adı', 'Hasta Soyadı', 'Vaka Veriliş\nTarihi','Vaka Veriliş\nSaati','MANUEL DÜZENLEME Nakledilen Hastane',  'ICD10 TANI KODU', 'ICD10 TANI ADI']
                    placed_columns= ['Hasta Ad', 'Hasta Soyad','Talep Tarihi','Düzenlenmiş Nakil Talep Eden Hastane', 'Yer Bulunma Tarihi']
                    
                    reports_missing_columns= [col for col in reports_columns if col not in df_reports.columns]
                    placed_missing_columns= [col for col in placed_columns if col not in df_placed.columns]
                    
                    non_existent_cols= []
                    for col in reports_missing_columns:
                        prompt_text = f"Sahadan Hastaneye Defter'de bulunamayan kolon: {col}, \nŞu an defterde mevcut olan kolon adı giriniz, kolon artık mevcut değilse boş bırakınız: "
                        new_col = str(self.ask_string_main_thread(prompt_text))

                        if not new_col:
                            reports_columns.remove(col)
                            non_existent_cols.append(col)
                            continue

                        df_reports.rename(columns={new_col:col}, inplace=True)

                    for col in placed_missing_columns:
                        prompt_text = f"Nakil Defterde Bulunamayan Kolon: {col},\nŞu an defterde mevcut olan kolon adı giriniz, kolon artık mevcut değilse boş bırakınız:"
                        new_col = str(self.ask_string_main_thread(prompt_text))
                        if not new_col:
                            placed_columns.remove(col)
                            non_existent_cols.append(col)
                            continue

                        df_placed.rename(columns={new_col:col}, inplace=True)

                    placed_baby_index= df_placed[df_placed['Hasta Ad'].astype(str).str.lower().astype(str).str.contains('bebek')].index
                    df_placed.loc[placed_baby_index, 'is_baby']= True

                    reports_baby_index= df_reports[df_reports['Hasta Adı'].astype(str).str.lower().astype(str).str.contains('bebek')].index
                    df_reports.loc[reports_baby_index, 'is_baby']= True

                    df_placed['Hasta Ad_upper']= df_placed['Hasta Ad'].astype(str).str.strip().astype(str).str.upper()
                    df_reports['Hasta Adı_upper']= df_reports['Hasta Adı'].astype(str).str.strip().astype(str).str.upper()



                    df_reports['Hasta Soyadı_upper']= df_reports['Hasta Soyadı'].astype(str).str.strip().astype(str).str.upper()
                    df_placed['Hasta Soyad_upper']= df_placed['Hasta Soyad'].astype(str).str.strip().astype(str).str.upper()

                    df_reports.loc[df_reports['is_baby']==True, 'Hasta Adı_upper']= 'BEBEK'
                    df_placed.loc[df_placed['is_baby']==True, 'Hasta Ad_upper']= 'BEBEK'

                    df_placed['Hasta Ad_upper']= df_placed['Hasta Ad_upper'].astype(str).str.strip().astype(str).str.replace('i','İ').astype(str).str.replace('ü','Ü').astype(str).str.replace('ç','Ç').astype(str).str.replace('ğ','Ğ').astype(str).str.replace('ş','Ş').astype(str).str.replace('ö','Ö').astype(str).str.upper().astype(str).str.replace('1', '').astype(str).str.replace('2', '').astype(str).str.strip()
                    df_reports['Hasta Adı_upper']= df_reports['Hasta Adı_upper'].astype(str).str.strip().astype(str).str.replace('i','İ').astype(str).str.replace('ü','Ü').astype(str).str.replace('ç','Ç').astype(str).str.replace('ğ','Ğ').astype(str).str.replace('ş','Ş').astype(str).str.replace('ö','Ö').astype(str).str.upper().astype(str).str.replace('1', '').astype(str).str.replace('2', '').astype(str).str.strip()
                    df_placed['Hasta Soyad_upper']= df_placed['Hasta Soyad_upper'].astype(str).str.strip().astype(str).str.replace('i','İ').astype(str).str.replace('ü','Ü').astype(str).str.replace('ç','Ç').astype(str).str.replace('ğ','Ğ').astype(str).str.replace('ş','Ş').astype(str).str.replace('ö','Ö').astype(str).str.upper().astype(str).str.strip()
                    df_reports['Hasta Soyadı_upper']= df_reports['Hasta Soyadı_upper'].astype(str).str.strip().astype(str).str.replace('i','İ').astype(str).str.replace('ü','Ü').astype(str).str.replace('ç','Ç').astype(str).str.replace('ğ','Ğ').astype(str).str.replace('ş','Ş').astype(str).str.replace('ö','Ö').astype(str).str.upper().astype(str).str.strip()
                    df_placed.rename(columns= {'Hasta Ad_upper':'Hasta Adı_upper', 'Hasta Soyad_upper':'Hasta Soyadı_upper'}, inplace= True)

                    df_reports['Nakledilen-Nakil Talep Eden Hastane']= df_reports['MANUEL DÜZENLEME Nakledilen Hastane']
                    df_placed['Nakledilen-Nakil Talep Eden Hastane']= df_placed['Düzenlenmiş Nakil Talep Eden Hastane']

                    df_reports['İhbar/Çağrı Tarihi İhbar/Çağrı  Saati'] = pd.to_datetime(
                        df_reports['İhbar/Çağrı Tarihi'] + ' ' + df_reports['İhbar/Çağrı  Saati'],
                        format='%d-%m-%Y %H:%M:%S', errors='coerce'
                    )

                    df_reports['Vaka Veriliş Tarih Saat']= pd.to_datetime(df_reports['Vaka Veriliş\nTarihi'] + ' '+ df_reports['Vaka Veriliş\nSaati'], format= '%d-%m-%Y %H:%M:%S', errors='coerce')

                    df_placed['Yer Bulunma Tarihi']= pd.to_datetime(df_placed['Yer Bulunma Tarihi'], format= '%d-%m-%Y %H:%M:%S', errors='coerce')
                    df_placed['Talep Tarihi']= pd.to_datetime(df_placed['Talep Tarihi'], format= '%d-%m-%Y %H:%M:%S', errors='coerce')

                    df_reports['Tarih']= df_reports['Vaka Veriliş Tarih Saat']
                    df_placed['Tarih']= df_placed['Talep Tarihi']

                    df_placed.drop(columns='index', inplace=True)
                    df_reports.drop(columns='index', inplace=True)

                    df_placed.reset_index(inplace=True)
                    df_reports.reset_index(inplace=True)

                    merged_df = pd.merge(df_placed.reset_index(), df_reports.reset_index(), on=['Hasta Adı_upper', 'Hasta Soyadı_upper', 'Nakledilen-Nakil Talep Eden Hastane'], how='inner')

                    merged_df['one_day']= (merged_df['Tarih_x'] - merged_df['Tarih_y']).between(dt.timedelta(days=0), dt.timedelta(days=1), inclusive='both')

                    merged_df= merged_df[merged_df['one_day']==True]

                    df_placed.loc[merged_df['index_x']]

                    df_reports.loc[merged_df['index_y']]

                    second_frame= pd.concat([df_placed.loc[merged_df['index_x']], df_reports.loc[merged_df['index_y']]])

                    second_frame.sort_values(by=['Hasta Adı_upper', 'Hasta Soyadı_upper', 'Nakledilen-Nakil Talep Eden Hastane', 'Tarih'], inplace=True)

                    second_frame.insert(0,'Hasta Adı_upper', second_frame.pop('Hasta Adı_upper'))
                    second_frame.insert(1,'Hasta Soyadı_upper', second_frame.pop('Hasta Soyadı_upper'))
                    second_frame.insert(2,'Nakledilen-Nakil Talep Eden Hastane', second_frame.pop('Nakledilen-Nakil Talep Eden Hastane'))
                    second_frame.insert(3,'Tarih', second_frame.pop('Tarih'))

                    second_frame['Hasta Ad Soyad_upper']= second_frame['Hasta Adı_upper'] + ' ' + second_frame['Hasta Soyadı_upper']

                    the_frame = pd.DataFrame()

                    for _, group in second_frame.groupby(['Hasta Ad Soyad_upper', 'Nakledilen-Nakil Talep Eden Hastane']):
                        group_one = group.sort_values(by='Tarih').copy()  # Ensure a copy is created


                        if len(group_one) > 1:
                            for loop in range(len(group_one)):

                                # Ensure that 'group' is not empty before checking iloc[0]
                                while len(group_one) > 1 and group_one.iloc[0]['workbook'] == 'Nakil Defter':
                                    group_one = group_one.iloc[1:].copy()  # Ensure copy to avoid warnings/issues

                                # Check if group_one has at least 2 elements before accessing iloc[1]
                                while len(group_one) > 1 and (group_one.iloc[0]['workbook'] == 'Sahadan Hastaneye Defter') and (group_one.iloc[1]['workbook'] == 'Sahadan Hastaneye Defter'):
                                    group_one = group_one.iloc[1:].copy()  # Ensure copy to avoid warnings/issues

                                while len(group_one) > 1 and (group_one.iloc[-1]['workbook'] == 'Nakil Defter') and (group_one.iloc[-2]['workbook'] == 'Nakil Defter'):
                                    group_one = group_one.iloc[:-1].copy()  # Ensure copy to avoid warnings/issues

                                while len(group_one) > 0 and group_one.iloc[-1]['workbook'] == 'Sahadan Hastaneye Defter':
                                    group_one = group_one.iloc[:-1].copy()  # Ensure copy to avoid warnings/issues

                                while len(group_one) > 1 and group_one.iloc[1]['Tarih'] - group_one.iloc[0]['Tarih'] > dt.timedelta(days=1):
                                    try:
                                        group_one = group_one.iloc[2:].copy()  # Ensure copy to avoid warnings/issues
                                    except:
                                        group_one = pd.DataFrame()
                                        break


                        # Corrected condition to check if all values are 'Sahadan Hastaneye Defter'
                        elif (group_one['workbook'] == 'Sahadan Hastaneye Defter').all():
                            group_one = pd.DataFrame()
                            continue
                        elif (group_one['workbook'] == 'Nakil Defter').all():
                            group_one = pd.DataFrame()
                            continue
                        elif len(group_one) < 2:
                            group_one = pd.DataFrame()
                            continue
                        else:
                            group_one = pd.DataFrame()

                        the_frame = pd.concat([the_frame, group_one])

                    the_frame.reset_index(inplace=True)
                    the_frame.drop(columns='index', inplace=True)
                    
                    if the_frame.empty:
                        messagebox.showerror("Uyarı", "Hiçbir Eşleşme Bulunamadı.")
                        return
                    
                    the_frame.rename(columns={'Hasta Adı_upper':'Hasta Adı', 'Hasta Soyadı_upper':'Hasta Soyadı', 'Hasta Ad Soyad_upper':'Hasta Adı Hasta Soyadı'}, inplace=True)
                        
                    the_frame.insert(2,'Hasta Adı Hasta Soyadı', the_frame.pop('Hasta Adı Hasta Soyadı'))

                    the_frame.drop(columns='index', inplace=True)

                    the_frame.reset_index(drop=True, inplace=True)

                    df_placed.drop(columns=['index','Hasta Adı_upper','Hasta Soyadı_upper', 'Nakledilen-Nakil Talep Eden Hastane', 'Tarih', 'is_baby'], inplace=True)

                    columns= ['İhbar/Çağrı Tarihi İhbar/Çağrı  Saati', 'Hasta Adı Hasta Soyadı',
                            'MANUEL DÜZENLEME Nakledilen Hastane', 'ICD10 TANI KODU',
                            'ICD10 TANI ADI'] + list(df_placed.columns[1:])
                    
                    for col in non_existent_cols:
                        try:
                            columns.remove(col)
                        except:
                            pass

                    the_frame= the_frame[columns]

                    the_frame['İhbar/Çağrı Tarihi İhbar/Çağrı  Saati'].fillna(the_frame['Talep Tarihi'], inplace=True)
                    the_frame['MANUEL DÜZENLEME Nakledilen Hastane'].fillna(method='ffill', inplace=True)

                    the_frame.drop_duplicates(keep='first',inplace=True)
                    the_frame.reset_index(drop=True, inplace=True)

                    home = the_frame[the_frame['Düzenlenmiş Kabul Eden Klinik']=='EVE NAKİL'].index
                    if len(home) > 0:
                        home_transports= []
                        for i in home:
                            home_transports.append(i-1)
                            home_transports.append(i)

                        df_home_transports= the_frame.iloc[home_transports]
                        the_frame.drop(home_transports, inplace=True)
                    else:
                        df_home_transports= pd.DataFrame()

                
                    def color_rows_by_talep_tarihi(df):
                        import pandas as pd

                        def highlight_rows(row):
                            if pd.notna(row['Talep Tarihi']):
                                return ['color: red'] * len(row)
                            return [''] * len(row)  # No style for other rows

                        styled_df = df.style.apply(highlight_rows, axis=1)
                        return styled_df


                    # Example usage (assuming 'df_placed' is your DataFrame):
                    styled_df_home_transports = color_rows_by_talep_tarihi(df_home_transports)
                    styled_the_frame= color_rows_by_talep_tarihi(the_frame)

                    with pd.ExcelWriter(self.save_path + '/'+ 'Nakil Defteri Mükerrer Çalışması.xlsx', engine='openpyxl') as writer:
                        styled_the_frame.to_excel(writer, sheet_name='mükerrer', index=False)
                        styled_df_home_transports.to_excel(writer, sheet_name='eve nakil', index=False)


                    self.status_label.config(text="Mükerrer Nakil Dosyası Oluşturuluyor...")
                    self.status_label.config(text="Dosya başarıyla oluşturuldu.")
                else:
                    messagebox.showerror("Error", "Dosya Bulunamadı.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate file: {e}")
                raise  # Consider re-raising for debugging purposes

            finally:
                self.progress.stop()
                self.generate_graphs_button.config(state=tk.NORMAL)  # Enable the button again
                self.status_label.config(text="Dosya Oluşturulması Tamamlandı.")

        thread = threading.Thread(target=run_graph_generation)
        thread.daemon = True
        thread.start()

    def choose_save_path(self):
        self.save_path = filedialog.askdirectory(title="Kaydetme Konumu Seç")
        if self.save_path:
            self.status_label.config(text=f"Durum: Kaydetme konumu seçildi: {self.save_path}")


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
    app = AmbulanceApp(root)
    root.mainloop()
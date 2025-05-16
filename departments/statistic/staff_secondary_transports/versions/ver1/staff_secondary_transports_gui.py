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
import seaborn as sns

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

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
        else:
            messagebox.showinfo("Registration Code Created",
                    f"A file 'registration.txt' has been created in:\n{self.program_dir}\n"
                    "Please send this file to the muhammedkaya65@gmail.com for an unlock code.")

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
        self.splash_screen.geometry("900x500+300+150")  # Larger, centered window
        self.splash_screen.configure(bg='#0e0e0e')  # Dark background for neon effect

        # Neon title
        self.title_label = tk.Label(
            self.splash_screen, 
            text="🚀 Saha İçi Mükerrer Acil Vaka Çalışması 🚀", 
            font=("Consolas", 28, "bold"), 
            fg="#00FFFB",  # Neon cyan
            bg="#0e0e0e"
        )
        self.title_label.pack(pady=60)

        # Subtitle
        self.subtitle_label = tk.Label(
            self.splash_screen, 
            text="İstanbul İl Ambulans Servisi - Avrupa 112", 
            font=("Consolas", 14, "italic"), 
            fg="#ADFF2F",  # Neon green
            bg="#0e0e0e"
        )
        self.subtitle_label.pack(pady=10)

        # Neon loading bar
        self.loading_bar_frame = tk.Frame(self.splash_screen, bg="#0e0e0e")
        self.loading_bar_frame.pack(pady=40)
        self.loading_bar = ttk.Progressbar(
            self.loading_bar_frame, 
            orient="horizontal", 
            length=400, 
            mode="indeterminate",
            style="Neon.Horizontal.TProgressbar"
        )
        self.loading_bar.pack()
        self.loading_bar.start()

        # Styling the neon progress bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Neon.Horizontal.TProgressbar",
            troughcolor="#1c1c1c",
            background="#00FFFB",
            thickness=15
        )

        # Footer text
        self.footer_label = tk.Label(
            self.splash_screen, 
            text="⚡ Muhammed Kaya ⚡", 
            font=("Consolas", 12), 
            fg="#FF1493",  # Neon pink
            bg="#0e0e0e"
        )
        self.footer_label.pack(side="bottom", pady=30)

        # Destroy the splash screen after 5 seconds
        self.splash_screen.after(5000, self.end_splash_screen)

    def end_splash_screen(self):
        # Destroy the splash screen and show the main window
        self.splash_screen.destroy()
        self.root.deiconify()  # Show the main window after splash screen
        self.create_widgets()  # Call create_widgets only once here


    def create_widgets(self):
        # Set the window title
        self.root.title("🚑 Avrupa 112")

        # Set the window size to be larger
        self.root.geometry("1000x700")
        self.root.configure(bg="#0e0e0e")  # Dark background for neon effect

        # Neon button styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Neon.TButton",
            font=("Consolas", 14, "bold"),
            padding=10,
            relief="flat",
            borderwidth=0,
            background="#00FFFB",
            foreground="#0e0e0e",
            anchor="center"
        )
        style.map(
            "Neon.TButton",
            background=[("active", "#ADFF2F"), ("pressed", "#FF1493")],
            foreground=[("active", "#0e0e0e"), ("pressed", "#ffffff")]
        )

        # Initialize a list to hold the paths of loaded files and their regions
        self.loaded_files = []

        # Status label
        self.status_label = tk.Label(self.root, text="Gerekli Belgeler: Genel Vaka Araştırma Raporu, İsim Listesi", font=("Consolas", 14), fg="#ADFF2F", bg="#0e0e0e")
        self.status_label.pack(pady=20)

        # Ensure only one instance of each widget is created
        if not hasattr(self, 'load_files_button'):
            # Load Multiple Files button with same size and smaller text
            self.load_files_button = ttk.Button(self.root, text="🗂 Dosyaları Yükle", command=self.load_multiple_files, style="Neon.TButton")
            self.load_files_button.pack(pady=15)

        if not hasattr(self, 'delete_file_button'):
            # Delete Selected File button with same size and smaller text
            self.delete_file_button = ttk.Button(self.root, text="🗑 Dosyayı Sil", command=self.delete_selected_file, style="Neon.TButton")
            self.delete_file_button.pack(pady=15)

        if not hasattr(self, 'save_path_button'):
            # Choose Save Path button with same size and smaller text
            self.save_path_button = ttk.Button(self.root, text="💾 Kaydetme Konumu", command=self.choose_save_path, style="Neon.TButton")
            self.save_path_button.pack(pady=15)

        if not hasattr(self, 'generate_graphs_button'):
            # Generate Graphs button with same size and smaller text
            self.generate_graphs_button = ttk.Button(self.root, text="🚀 Başla", state=tk.DISABLED, command=self.start_generate_graphs_thread, style="Neon.TButton")
            self.generate_graphs_button.pack(pady=15)

        if not hasattr(self, 'file_listbox'):
            # File listbox to display selected files (allows user to see uploaded files)
            self.file_listbox = tk.Listbox(self.root, width=80, height=10, font=("Consolas", 12), bg="#1c1c1c", fg="#00FFFB", selectbackground="#ADFF2F")
            self.file_listbox.pack(pady=20)

        if not hasattr(self, 'progress'):
            # Progress bar
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=600, mode="indeterminate", style="Neon.Horizontal.TProgressbar")
            self.progress.pack(pady=20)
            # Start progress bar animation
     
            self.progress.start()


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

                    # the user to select the region for each file
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
        """Open a dialog box with a dropdown menu for selecting Emergency(Sahadan Hastaneye Defter) or staff Names (İsim Listesi)."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Defter Tipi Seç {file.split('/')[-1]}")
        dialog.geometry("300x100")

        # Label for instructions
        label = ttk.Label(dialog, text="Bu dosya için defter tipi seç:", font=("Helvetica", 10))
        label.pack(pady=10)

        # Dropdown menu
        region_var = tk.StringVar(dialog)
        region_var.set("Sahadan Hastaneye Defter")  # Default value

        region_dropdown = ttk.OptionMenu(dialog, region_var, "Sahadan Hastaneye Defter", "Sahadan Hastaneye Defter", "İsim Listesi")
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
        asia_file = filedialog.askopenfilename(title="İsim Listesi Seç", filetypes=[("All Files", "*.*")])

        if not asia_file:
            messagebox.showerror("Hata", "Lütfen Geçerli Bir Dosya Seç!")
            self.progress.stop()
            return

        try:
            self.df_asia = self.load_and_process_data(asia_file, 'İsim Listesi')  # Fill this function
            self.status_label.config(text="Durum: İsim Listesi Başarıyla Yüklendi!")

            # Show the selected Asia file in the listbox
            self.file_listbox.insert(tk.END, f"İsim Listesi: {asia_file.split('/')[-1]}")

            self.check_data_loaded()
        except Exception as e:
            messagebox.showerror("Hata", f"İsim Listesi yüklenemedi: {e}")
            self.status_label.config(text="Durum: İsim Listesi yüklenemedi")
        finally:
            self.progress.stop()
            
    def load_and_process_data(self, file_path, region):
        """This function loads and processes the data from the specified Excel file."""
        df = pd.read_excel(file_path)
        df['workbook'] = region  # Set region as 'Sahadan Hastaneye Defter' or 'İsim Listesi'

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
                    

                    df= df_reports
                    df_staff_list= df_internal_transports

                    reports_columns= ['Vaka Veriliş\nTarihi','Vaka Veriliş\nSaati', 'Sonuç', 'Ekipteki Kişiler','Tc Kimlik No\n', 'ICD10 TANI\nADI','Triaj']
                    
                    option = messagebox.askquestion(
                        "Filter Option",
                        "İsim ve Soyisim sütunları birleşik mi?"
                        )
                    if option == 'yes':
                        staff_name_columns= ['İsim Soyisim']
                    else:  
                        staff_name_columns= ['İsim','Soyisim']
                    
                    reports_missing_columns= [col for col in reports_columns if col not in df_reports.columns]
                    staff_name_missing_columns= [col for col in staff_name_columns if col not in df_staff_list.columns]
                    
                    
                    for col in reports_missing_columns:
                        prompt_text = f"Sahadan Hastaneye Defter'de bulunamayan kolon: {col}, \nŞu an defterde mevcut olan kolon adı giriniz: "
                        new_col = str(self.ask_string_main_thread(prompt_text))

                        if not new_col:
                            return messagebox.showerror("Error", f'Eksik {col} sütununu tamamlayınız!')

                        df.rename(columns={new_col:col}, inplace=True)

                    for col in staff_name_missing_columns:
                        prompt_text = f"İsim Listeside Bulunamayan Kolon: {col},\nŞu an defterde mevcut olan kolon adı giriniz:"
                        new_col = str(self.ask_string_main_thread(prompt_text))

                        if not new_col:
                            return messagebox.showerror("Error", f'Eksik {col} sütununu tamamlayınız!')
                        
                        df_staff_list.rename(columns={new_col:col}, inplace=True)


                    if option == 'yes':
                        df_staff_list['İsim Soyisim']= df_staff_list['İsim Soyisim'].astype(str).str.strip()
                        df_staff_list= df_staff_list[df_staff_list['İsim Soyisim'] != 'nan']
                        df_staff_list= df_staff_list[df_staff_list['İsim Soyisim'] != 'İsim Soyisim']
                        staff_list=list(df_staff_list['İsim Soyisim'].unique())
                    else:
                        df_staff_list['İsim Soyisim']= (df_staff_list['İsim'] + ' ' + df_staff_list['Soyisim']).astype(str).str.strip()
                        staff_list=list( df_staff_list['İsim Soyisim'].unique())
                        staff_list.remove('nan')
                    df['Vaka Veriliş Tarih Saat']=pd.to_datetime(df['Vaka Veriliş\nTarihi'] + ' ' + df['Vaka Veriliş\nSaati'], format='%d-%m-%Y %H:%M:%S')
                    df= df[(df['Tc Kimlik No\n'].notna() )& (df['Tc Kimlik No\n'] != 'U0')]
                    df['Tc Kimlik No\n']= df['Tc Kimlik No\n'].astype(str).str.strip().astype(str).str.upper()
                    df.drop(columns=['Vaka Veriliş\nTarihi', 'Vaka Veriliş\nSaati'], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    df['Ekipteki Kişiler']= df['Ekipteki Kişiler'].astype(str).str.strip()
                    df['index']= df.index

                    # if Sonuç column mathces criteria, color row to the red

                    def color_rows_by_talep_tarihi(df):

                        def highlight_rows(row):
                            if row['Sonuç'] in ['Yerinde Müdahale', 'Nakil - Red','Diğer']:
                                return ['background-color: red'] * len(row)
                            return [''] * len(row)  # Return empty list for other rows
                            

                        styled_df = df.style.apply(highlight_rows, axis=1)
                        return styled_df



                    df_general_analysis= pd.DataFrame(columns=['İsim Soyisim',
                                           'Toplam Vaka Sayısı',
                                           'Toplam Yerinde Müdahale-Nakil Red-Diğer Sayısı',
                                           'Yerinde-Red-Diğer / Toplam Vaka Yüzdesi',
                                           '48 Saat Mükerrer Sayısı (Son hastaneye Nakil Dahil)',
                                           '24 Saat Mükerrer Sayısı (Son Hastaneye Nakil Dahil)',
                                           '48 Saat Mükerrer Sayısı (Son Hastaneye Nakil Hariç)',
                                           '24 Saat Mükerrer Sayısı (Son Hastaneye Nakil Hariç)',
                                           'Kırmızı Kodla Sonuçlanan (48 Saat)',
                                           'Sarı Kodla Sonuçlanan (48 Saat)',
                                           'Yeşil Kodla Sonuçlanan (48 Saat)',
                                           'Siyah Kodla Sonuçlanan (48 Saat)',
                                           '48 Saat Kardiyak Arrest veya Ölümle Sonuçlanan',
                                           '24 Saat Kardiyak Arrest veya Ölümle Sonuçlanan'
                                           ])
                    for doc in staff_list:
                        red_count= 0
                        yellow_count= 0
                        green_count= 0
                        black_count= 0
                        arrest_count= 0
                        total_case= 0
                        yerinde_red= 0
                        forty_eight_hours_count= 0
                        twenty_four_hours_count= 0
                        forty_eight_only_false= 0
                        twenty_four_only_false= 0
                        twenty_four_arrest_count= 0

                        df_doc= df[df['Ekipteki Kişiler'].astype(str).str.contains(doc)]
                        total_case= len(df_doc)
                        df_not_placed= df_doc[df_doc['Sonuç'].isin(['Yerinde Müdahale', 'Nakil - Red','Diğer'])].copy()
                        yerinde_red= len(df_not_placed)
                        try:
                            yerinde_total_percentage= round((yerinde_red/total_case)*100,2)
                        except:
                            yerinde_total_percentage= 0
                        df_placed= df[~df['Sonuç'].isin(['Yerinde Müdahale', 'Nakil - Red','Diğer'])].copy()
                        df_merged= pd.merge(df_placed, df_not_placed, on= 'Tc Kimlik No\n')
                        df_merged['Vaka Veriliş Tarih Saat_x']= pd.to_datetime(df_merged['Vaka Veriliş Tarih Saat_x'], format='%Y-m-%d %H:%M:%S')
                        df_merged['Vaka Veriliş Tarih Saat_y']= pd.to_datetime(df_merged['Vaka Veriliş Tarih Saat_y'], format='%Y-m-%d %H:%M:%S')
                        df_merged['is_scondary']= (df_merged['Vaka Veriliş Tarih Saat_x'] - df_merged['Vaka Veriliş Tarih Saat_y']).between(dt.timedelta(days=0), dt.timedelta(days=2), inclusive='both')
                        df_matched= df_merged[df_merged['is_scondary']== True]
                        forty_eight_only_false= len(df_merged[df_merged['is_scondary']== True])
                        twenty_four_matched= df_merged.copy()
                        twenty_four_matched['is_secondary']= (twenty_four_matched['Vaka Veriliş Tarih Saat_x'] - twenty_four_matched['Vaka Veriliş Tarih Saat_y']).between(dt.timedelta(days=0), dt.timedelta(days=1), inclusive='both')
                        twenty_four_matched= twenty_four_matched[twenty_four_matched['is_secondary']== True]
                        twenty_four_only_false= len(twenty_four_matched)
                        df_matched_final= pd.DataFrame()

                        for placed_index, not_placed_index in zip(df_matched['index_x'].to_list(), df_matched['index_y'].to_list()):
                            df_matched_final= pd.concat([df_matched_final, df.loc[[not_placed_index, placed_index]]])
                        forty_eight_hours_count= len(df_matched_final)
                        twenty_four_hours_count= len(twenty_four_matched)

                        df_matched_final_twenty_four= pd.DataFrame()
                        for placed_index, not_placed_index in zip(twenty_four_matched['index_x'].to_list(), twenty_four_matched['index_y'].to_list()):
                            df_matched_final_twenty_four= pd.concat([df_matched_final_twenty_four, df.loc[[not_placed_index, placed_index]]])
                        twenty_four_hours_count= len(df_matched_final_twenty_four)

                        if len(df_matched_final_twenty_four) > 1:
                            df_counts_3= df_matched_final_twenty_four[~df_matched_final_twenty_four['Sonuç'].isin(['Yerinde Müdahale', 'Nakil - Red','Diğer'])]
                            df_counts_3= df_matched_final_twenty_four[df_matched_final_twenty_four['ICD10 TANI\nADI'].astype(str).str.contains('ARREST|ÖLÜM')]
                        if len(df_counts_3)>0:
                            twenty_four_arrest_count= len(df_counts_3)
                        else:
                            twenty_four_arrest_count= 0
                        if len(df_matched_final) > 0:

                            df_counts= df_matched_final[df_matched_final['Sonuç'].isin(['Yerinde Müdahale', 'Nakil - Red','Diğer'])]

                            df_counts['count']= 1

                            df_counts_2= df_matched_final[~df_matched_final['Sonuç'].isin(['Yerinde Müdahale', 'Nakil - Red','Diğer'])]
                        for triage in df_counts_2['Triaj']:
                            if triage=='Kırmızı Kod':
                                red_count+=1
                            elif triage=='Sarı Kod':
                                yellow_count+=1
                            elif triage=='Yeşil Kod':
                                green_count+=1
                            elif triage=='Siyah Kod':
                                black_count+=1  
                        df_counts_2= df_counts_2[df_counts_2['ICD10 TANI\nADI'].astype(str).str.contains('ARREST|ÖLÜM')]
                        arrest_count= len(df_counts_2)
                        df_general_analysis.loc[len(df_general_analysis.index)] = [doc,total_case,yerinde_red,yerinde_total_percentage,forty_eight_hours_count,twenty_four_hours_count,forty_eight_only_false,twenty_four_only_false,red_count, yellow_count, green_count, black_count, arrest_count,twenty_four_arrest_count]
                        
                        if len(df_matched_final)>0:
                            df_matched_final.reset_index(drop=True, inplace=True)

                            styled_the_frame= color_rows_by_talep_tarihi(df_matched_final)
                            # Check for duplicate columns
                            if styled_the_frame.columns.duplicated().any():
                                print("Warning: DataFrame contains duplicate column names.")
                                styled_the_frame.columns = [f"{col}_{i}" if styled_the_frame.columns.tolist().count(col) > 1 else col 
                                                            for i, col in enumerate(styled_the_frame.columns)]

                            # Ensure unique row indices
                            

                            with pd.ExcelWriter(self.detailed_path + '/'+ f'{doc} 48-24 Saat Mükerrer Vaka.xlsx', engine='openpyxl') as writer:
                                # Ensure at least one visible sheet
                                styled_the_frame.to_excel(writer, sheet_name='mükerrer', index=False)
                                workbook = writer.book
                                for sheet in workbook.worksheets:
                                    sheet.sheet_state = 'visible'
                        else:
                            pass

                    
                    df_general_analysis.to_excel(self.main_path + '/Genel Analiz.xlsx', index=False)
                    
                    def generate_visualized_graphs(df_general_analysis):
                        #########################################
                        if len(df_general_analysis)>20:
                            plt.figure(figsize=(20, 10))
                        else:
                            plt.figure(figsize=(10, 5))

                        ax = sns.barplot(x='İsim Soyisim', y='48 Saat Mükerrer Sayısı (Son hastaneye Nakil Dahil)', data=df_general_analysis[df_general_analysis['48 Saat Mükerrer Sayısı (Son hastaneye Nakil Dahil)']> 0])
                        plt.xticks(rotation=90)
                        plt.xlabel("Doktor Adı")
                        plt.ylabel("48 Saat Mükerrer Sayısı")
                        plt.title("48 Saat Toplam Mükerrer Sayısı")
                        plt.tight_layout()

                        # Annotate bars with their values
                        for p in ax.patches:
                            ax.annotate(format(p.get_height(), '.0f'),
                                        (p.get_x() + p.get_width() / 2., p.get_height()),
                                        ha = 'center', va = 'center',
                                        xytext = (0, 9),
                                        textcoords = 'offset points')
                        plt.savefig(self.visio_path + '/48 Saat Toplam Mukerrer Sayisi.png')
                        ###################################################
                        if len(df_general_analysis)>20:
                            plt.figure(figsize=(20, 10))
                        else:
                            plt.figure(figsize=(10, 5))

                        # Melt the dataframe
                        df_melted = pd.melt(
                            df_general_analysis,
                            id_vars=['İsim Soyisim'],
                            value_vars=['Kırmızı Kodla Sonuçlanan (48 Saat)', 'Sarı Kodla Sonuçlanan (48 Saat)', 'Yeşil Kodla Sonuçlanan (48 Saat)', 'Siyah Kodla Sonuçlanan (48 Saat)'],
                            var_name='Triage Code',
                            value_name='Number of Cases'
                        )
                        df_melted = df_melted[df_melted['Number of Cases'] >0]
                        # Define a custom color palette
                        custom_palette = {
                            'Kırmızı Kodla Sonuçlanan (48 Saat)': 'red',
                            'Sarı Kodla Sonuçlanan (48 Saat)': 'yellow',
                            'Yeşil Kodla Sonuçlanan (48 Saat)': 'green',
                            'Siyah Kodla Sonuçlanan (48 Saat)': 'black'
                        }

                        # Create the barplot with the custom palette
                        sns.barplot(
                            x='İsim Soyisim',
                            y='Number of Cases',
                            hue='Triage Code',
                            data=df_melted,
                            palette=custom_palette  # Apply the custom color palette
                        )



                        plt.xticks(rotation=90)
                        plt.xlabel('Doktor Adı')
                        plt.ylabel('48 Saat Vaka Sayısı')
                        plt.title('Triaj Koduna Göre agilim')
                        plt.legend(title='Triaj Koduna Göre Mükerrer Sayıları (48 Saat)')
                        plt.tight_layout()
                        plt.savefig(self.visio_path + '/Triaj Koduna Gore Dagilim.png')
                        ####################################################################

                        if len(df_general_analysis)>20:
                            plt.figure(figsize=(20, 10))
                        else:
                            plt.figure(figsize=(10, 5))

                        ax = sns.barplot(x='İsim Soyisim', y='48 Saat Mükerrer Sayısı (Son hastaneye Nakil Dahil)',
                                        data=df_general_analysis[df_general_analysis['48 Saat Mükerrer Sayısı (Son hastaneye Nakil Dahil)'] != 0])

                        plt.xticks(rotation=90)
                        plt.xlabel("Doctor's Name")
                        plt.ylabel("Total Cases")
                        plt.title("48 Saat Kardiyak Arrest veya Ölümle Sonuçlanan")

                        # Set y-axis ticks to integers starting from 0
                        ax.yaxis.set_major_locator(ticker.MultipleLocator(1)) # Set ticks every 1 unit
                        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

                        plt.tight_layout()

                        # Annotate bars with their values
                        for p in ax.patches:
                            ax.annotate(format(p.get_height(), '.0f'),
                                        (p.get_x() + p.get_width() / 2., p.get_height()),
                                        ha = 'center', va = 'center',
                                        xytext = (0, 9),
                                        textcoords = 'offset points')
                        plt.savefig(self.visio_path + '/48 Saat Kardiyak Arrest veya Olumle Sonuclanan.png')
                    
                    generate_visualized_graphs(df_general_analysis)


                    self.status_label.config(text="Mükerrer Acil Vaka Çalışması Oluşturuluyor...")
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
            # Set the directory paths, then create the directories if they don't exist
            self.main_path= os.path.join(self.save_path, 'Mükerrer Nakil Çalışması')
            os.makedirs(self.main_path, exist_ok=True)
            self.detailed_path = os.path.join(self.main_path, 'Detaylı Grafikler')
            self.visio_path = os.path.join(self.main_path, 'Görsel Grafikler')
            
            os.makedirs(self.detailed_path, exist_ok=True)
            os.makedirs(self.visio_path, exist_ok=True)



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
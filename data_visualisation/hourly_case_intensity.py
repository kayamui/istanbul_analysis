import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
from tkinter import ttk
import threading
import pandas as pd
import numpy as np
import os
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

class AmbulanceApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the main window during the splash screen
        self.show_splash_screen()

    def show_splash_screen(self):
        # Create splash screen window
        self.splash_screen = tk.Toplevel(self.root)
        self.splash_screen.overrideredirect(True)  # Borderless window
        self.splash_screen.geometry("800x400+300+200")  # Set window size and position
        self.splash_screen.configure(bg='#f0f4f7')  # Light background color

        # Centered title "Vaka Yoğunluk Grafikeri"
        self.title_label = tk.Label(self.splash_screen, text="Vaka Yoğunluk Grafikeri", font=("Helvetica", 24, "bold"), fg="#333", bg="#f0f4f7")
        self.title_label.pack(pady=80)

        # Dedication message fitted above the bottom text
        self.dedication_message = (
            "Çok değerli hocalarım, Acil Şube Başkanımız Abdurrahman Kavuncu'ya, "
            "Başkan Yardımcımız Nurgül Çiğdem'e, Başhekimimiz Mehmet Necmeddin Sutaşır'a, "
            "değerli dostlarım ve Başhekim Yardımcımız Yunus Emre Eksert'e, "
            "ekip arkadaşım Orhan Dolgun'a katkıları ve destekleri için teşekkürlerimle..."
        )
        self.dedication_label = tk.Label(self.splash_screen, text=self.dedication_message, font=("Helvetica", 10, "italic"), fg="#555", bg="#f0f4f7", wraplength=750, justify="center")
        self.dedication_label.pack(side="bottom", pady=(0, 40))  # Add padding to prevent overlap with bottom texts

        # Bottom left: "Avrupa 112" in minimal and light font
        self.left_label = tk.Label(self.splash_screen, text="Avrupa 112", font=("Helvetica", 12), fg="#333", bg="#f0f4f7")
        self.left_label.place(x=20, y=360)

        # Bottom right: "Muhammed Kaya" in a bolder font
        self.right_label = tk.Label(self.splash_screen, text="Muhammed Kaya", font=("Helvetica", 12), fg="#333", bg="#f0f4f7")
        self.right_label.place(x=650, y=360)

        # Destroy the splash screen after 5 seconds
        self.splash_screen.after(5000, self.end_splash_screen)

    def end_splash_screen(self):
        # Destroy the splash screen and show the main window
        self.splash_screen.destroy()
        self.root.deiconify()  # Show the main window after splash screen
        self.create_widgets()


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

        # Load Multiple Files button with same size and smaller text
        self.load_files_button = ttk.Button(self.root, text="Dosyaları Yükle", command=self.load_multiple_files, style="Rounded.TButton")
        self.load_files_button.pack(pady=10)

        # Delete Selected File button with same size and smaller text
        self.delete_file_button = ttk.Button(self.root, text="Dosyayı Sil", command=self.delete_selected_file, style="Rounded.TButton")
        self.delete_file_button.pack(pady=10)

        # Choose Save Path button with same size and smaller text
        self.save_path_button = ttk.Button(self.root, text="Kaydetme Konumu", command=self.choose_save_path, style="Rounded.TButton")
        self.save_path_button.pack(pady=10)

        # Generate Graphs button with same size and smaller text
        self.generate_graphs_button = ttk.Button(self.root, text="Grafiklemeye Başla", state=tk.DISABLED, command=self.start_generate_graphs_thread, style="Rounded.TButton")
        self.generate_graphs_button.pack(pady=10)

        # File listbox to display selected files (allows user to see uploaded files)
        self.file_listbox = Listbox(self.root, width=80, height=8, font=("Helvetica", 10))
        self.file_listbox.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack(pady=10)


    def load_multiple_files(self):
        """Allow user to select multiple files and load them into the program, with region selection for each."""
        files = filedialog.askopenfilenames(title="Dosya Seç", filetypes=[("Excel Files", "*.xlsx")])

        if files:
            for file in files:
                if file not in [f[0] for f in self.loaded_files]:  # Avoid duplicates
                    # Open a dialog with a dropdown to select Europe (Avrupa) or Asia (Asya)
                    region = self.choose_region_dialog(file)
                    if region:  # If the user made a valid selection
                        self.loaded_files.append((file, region))
                        self.file_listbox.insert(tk.END, f"{file.split('/')[-1]} ({region})")  # Display file name and region
                    else:
                        messagebox.showwarning("Yanlış Seçim", "Lütfen uygun bölgeyi seç (Avrupa or Asya).")

            self.check_data_loaded()

    def choose_region_dialog(self, file):
        """Open a dialog box with a dropdown menu for selecting Europe (Avrupa) or Asia (Asya)."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Bölge Seç {file.split('/')[-1]}")
        dialog.geometry("300x100")

        # Label for instructions
        label = ttk.Label(dialog, text="Bu dosya için bölge seç:", font=("Helvetica", 10))
        label.pack(pady=10)

        # Dropdown menu
        region_var = tk.StringVar(dialog)
        region_var.set("Avrupa")  # Default value

        region_dropdown = ttk.OptionMenu(dialog, region_var, "Avrupa", "Avrupa", "Asya")
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
        thread.start()

    # File loading functions with progress handling
    def load_europe_data(self):
        europe_file = filedialog.askopenfilename(title="Avrupa Dosyasını Seç", filetypes=[("Excel Files", "*.xlsx")])

        if not europe_file:
            messagebox.showerror("Hata", "Lütfen Geçerli Bir Dosya Seç!")
            self.progress.stop()
            return

        try:
            self.df_europe = self.load_and_process_data(europe_file, 'AVRUPA')  # Fill this function
            self.status_label.config(text="Durum: Avrupa Dosyası Başarıyla Yüklendi!")

            # Show the selected Europe file in the listbox
            self.file_listbox.insert(tk.END, f"Avrupa: {europe_file.split('/')[-1]}")

            self.check_data_loaded()
        except Exception as e:
            messagebox.showerror("Hata", f"Avrupa dosyası yüklenemedi: {e}")
            self.status_label.config(text="Durum: Avrupa dosyası yüklenemedi")
        finally:
            self.progress.stop()

    def load_asia_data(self):
        asia_file = filedialog.askopenfilename(title="Asya Dosyasını Seç", filetypes=[("Excel Files", "*.xlsx")])

        if not asia_file:
            messagebox.showerror("Hata", "Lütfen Geçerli Bir Dosya Seç!")
            self.progress.stop()
            return

        try:
            self.df_asia = self.load_and_process_data(asia_file, 'ASYA')  # Fill this function
            self.status_label.config(text="Durum: Asya Dosyası Başarıyla Yüklendi!")

            # Show the selected Asia file in the listbox
            self.file_listbox.insert(tk.END, f"Asya: {asia_file.split('/')[-1]}")

            self.check_data_loaded()
        except Exception as e:
            messagebox.showerror("Hata", f"Asya dosyası yüklenemedi: {e}")
            self.status_label.config(text="Durum: Asya dosyası yüklenemedi")
        finally:
            self.progress.stop()
            
    def load_and_process_data(self, file_path, region):
        """This function loads and processes the data from the specified Excel file."""
        df = pd.read_excel(file_path, usecols=['Vakanın Enlemi', 'Vakanın Boylamı', 'Vaka Veriliş\nTarihi',
                                               'Vaka Veriliş\nSaati', 'Vakaya Çıkış Tarihi', 'Vakaya Çıkış Saati',
                                               'Olay Yeri Varış Tarihi', 'Olay Yeri Varış Saati', 'Kensel/Kırsal'])
        df['BOLGE'] = region  # Set region as 'AVRUPA' or 'ASYA'

        def to_datetime(row):
            try:
                return pd.to_datetime(row, format='%d-%m-%Y %H:%M:%S')
            except:
                try:
                    return pd.to_datetime(row, format='%Y-%m-%d %H:%M:%S')
                except:
                    return '-'

        def recalculate_reach(row):
            if row['KENSEL/KIRSAL'] == 'KIRSAL':
                row['reach_time'] = row['reach_time'] / 3
                return row['reach_time']
            else:
                return row['reach_time']

        # Start data processing
        df.columns = [col.strip().upper() for col in df.columns]

        columns_list = []
        for i in df.columns:
            i = i.replace('-', ' ').replace('Ç', 'C').replace('Ğ', 'G').replace('İ', 'I').replace('Ö', 'O').replace('Ş', 'S').replace('Ü', 'U').strip()
            columns_list.append(i)

        df.columns = columns_list

        df['VAKA VERILIS TARIH SAAT']= df['VAKA VERILIS\nTARIHI'] + ' ' + df['VAKA VERILIS\nSAATI']
        df['VAKA CIKIS TARIH SAAT'] = df['VAKAYA CIKIS TARIHI'] + ' '+ df['VAKAYA CIKIS SAATI']
        df['OLAY YER VARIS TARIH SAAT']= df['OLAY YERI VARIS TARIHI'] + ' ' + df['OLAY YERI VARIS SAATI']

        df['VAKA VERILIS TARIH SAAT'] = df['VAKA VERILIS TARIH SAAT'].apply(to_datetime)
        df['VAKA CIKIS TARIH SAAT'] = df['VAKA CIKIS TARIH SAAT'].apply(to_datetime)
        df['OLAY YER VARIS TARIH SAAT']= df['OLAY YER VARIS TARIH SAAT'].apply(to_datetime)

        df['hour']= df['VAKA VERILIS TARIH SAAT'].dt.strftime('%H')

        df['Gün'] = df['VAKA VERILIS TARIH SAAT'].dt.day_name(locale= 'tr_TR')
        df['Gün']= df['Gün'].str.replace('ý','I').str.replace('þ','Ş')
        df['Ay']= df['VAKA VERILIS TARIH SAAT'].dt.month
        df['Yıl']= df['VAKA VERILIS TARIH SAAT'].dt.year

        df['Gün']= df['Gün'].str.replace('i','İ').str.replace('ı','I').str.replace('ö','Ö').str.replace('ü','Ü').str.replace('ş','Ş').str.replace('ç','Ç').str.replace('ğ','Ğ').str.upper()

        df['ulasim_suresi']= (df['OLAY YER VARIS TARIH SAAT'] - df['VAKA CIKIS TARIH SAAT']).dt.seconds
        df['ulasim_suresi']= df['ulasim_suresi'].astype('float32')

        day_of_week= ['PAZARTESİ', 'SALI', 'ÇARŞAMBA', 'PERŞEMBE', 'CUMA', 'CUMARTESİ', 'PAZAR']
        df['Gün'] = pd.Categorical(df['Gün'], categories=day_of_week, ordered=True)
        df['week_day']= df['Gün'].apply(lambda x: 'HAFTA İÇİ' if x in ['PAZARTESİ', 'SALI', 'ÇARŞAMBA', 'PERŞEMBE', 'CUMA'] else 'HAFTA SONU')

        df['Value']= 1
        df['Value']= df['Value'].astype(int)
        df.rename(columns={'ulasim_suresi':'reach_time'}, inplace=True)

        df= df[((df['reach_time']<=3600) & (df['OLAY YER VARIS TARIH SAAT'] > df["VAKA CIKIS TARIH SAAT"]))]
        df['reach_time']= df['reach_time'].astype('float32')
        df['reach_time']= df.apply(recalculate_reach, axis=1)

        df['hour']= df['hour'].astype(int)
        df= df[(df['hour'] >= 10) & (df['hour']<22)]

        df['Ay']= df['Ay'].astype(int)
        df['Gün']= df['Gün'].str.strip()
        df['hour']= df['hour'].astype(int)

        df= df[df['VAKANIN ENLEMI'] != '-']
        df= df[df['VAKANIN BOYLAMI'] != '-']
        df['VAKANIN ENLEMI']= df['VAKANIN ENLEMI'].astype('float32')
        df['VAKANIN BOYLAMI']= df['VAKANIN BOYLAMI'].astype('float32')

        # Initialize MinMaxScaler
        scaler = MinMaxScaler(feature_range=(1, 100))

        # Apply log transformation and scaling within each group
        df['reach_time_log'] = df.groupby(['BOLGE', 'Ay', 'Gün'])['reach_time'].transform(lambda x: np.log1p(x))
        df['reach_time_scaled'] = df.groupby(['BOLGE', 'Ay', 'Gün'])['reach_time_log'].transform(lambda x: scaler.fit_transform(x.values.reshape(-1, 1)).flatten())

        df.drop_duplicates(inplace=True)

        return df

    def check_data_loaded(self):
        """Enable the Generate Graphs button if at least one file is loaded."""
        if self.loaded_files:
            self.generate_graphs_button.config(state=tk.NORMAL)


    def generate_graphs(self):
        if not self.save_path:
            messagebox.showerror("Hata", "Lütfen kaydetme konumu seç!")
            self.progress.stop()
            return

        try:
            # Process each file independently
            if self.loaded_files:
                all_dfs = []
                for file, region in self.loaded_files:
                    df = self.load_and_process_data(file, region)  # Pass the region as well (AVRUPA or ASYA)
                    all_dfs.append(df)

                # Concatenate all loaded dataframes
                df_combined = pd.concat(all_dfs, ignore_index=True)

                # Call the graph generation function
                generate_graphs_for_all_days(df_combined, self.save_path)
                self.status_label.config(text="Durum: Haritalar başarıyla oluşturuldu")
            else:
                messagebox.showerror("Hata", "Dosya Yüklenmedi!")
                self.progress.stop()
                return
        except Exception as e:
            messagebox.showerror("Hata", f"Haritalar oluşturulamadı: {e}")
            self.status_label.config(text="Durum: Haritalar oluşturulamadı")
        finally:
            self.progress.stop()


    def choose_save_path(self):
        self.save_path = filedialog.askdirectory(title="Kaydetme Konumu Seç")
        if self.save_path:
            self.status_label.config(text=f"Durum: Kaydetme konumu seçildi: {self.save_path}")

def generate_graphs_for_all_days(df, save_path):
    """Generates graphs for all days of the week and saves them to the specified path."""
    year = df['Yıl'].unique()[0]  # Get the year from the dataset

    days_of_week = ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]

    for month in df['Ay'].unique():
        filtered_df = df[df['Ay'] == month]  # Filter the DataFrame for the current month
        most_common_month = month

        if not filtered_df.empty:
            for day in days_of_week:
                selected_df = filtered_df[filtered_df['Gün'] == day]

                if not selected_df.empty:
                    visualize_map(selected_df, day, most_common_month, year, save_path)
                else:
                    print(f"Herhangi bir veri mevcut değil: {day}, {most_common_month}. Ay")

    
    # GENERATING GRAPHS FOR WEEKDAY AND WEEKEND
    week_day = ["HAFTA İÇİ", "HAFTA SONU"]
    for month in df['Ay'].unique():
        filtered_df = df[df['Ay'] == month]  # Filter the DataFrame for the current month
        most_common_month = month
        if not filtered_df.empty:
            for day in week_day:
                selected_df = filtered_df[filtered_df['week_day'] == day]

                if not selected_df.empty:
                    visualize_map(selected_df, day, most_common_month, year, save_path)
                else:
                    print(f"Herhangi bir veri mevcut değil: {day}, {most_common_month}. Ay")

    # GENERATING GRAPHS FOR OVERALL
    for month in df['Ay'].unique():
        filtered_df = df[df['Ay'] == month]  # Filter the DataFrame for the current month
        most_common_month = month
        day= 'Genel'
        if not filtered_df.empty:
            selected_df= filtered_df.copy()
            visualize_map(selected_df, day, most_common_month, year, save_path)
        else:
            print(f"Herhangi bir veri mevcut değil: {day}, {most_common_month}. Ay")


def visualize_map(df, day, most_common_month, year, save_path):
    """Visualizes and saves the map for the provided DataFrame, day, month, and year."""
    #print(f'Generating map for {day}, {most_common_month}/{year}...')

    try:
        radius = 20 if len(df) < 15000 else 10
        lat_center = df['VAKANIN ENLEMI'].mean()
        lon_center = df['VAKANIN BOYLAMI'].mean()

        fig = px.density_mapbox(df, lat='VAKANIN ENLEMI', lon='VAKANIN BOYLAMI', radius=radius,
                                center=dict(lat=lat_center, lon=lon_center), zoom=10,
                                mapbox_style="open-street-map", opacity=0.7,
                                color_continuous_scale=["blue", "yellow", "red"],
                                z='reach_time_scaled',
                                animation_frame='hour')

        fig.update_layout(
            title=f"VAKA YOĞUNLUK HARİTASI {day}, {most_common_month}. AY, {year}",  # Main title
            title_x=0.5,  # Center the title
            coloraxis_colorbar=dict(
                title="PUAN",  # Color bar title
            ),
            geo=dict(
                showland=True,  # Show land
                landcolor="lightgray"
            )
        )

        fig.add_annotation(
            text="AVRUPA112 */ Muhammed KAYA",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.95, y=0.05,
            font=dict(size=12, color="black")
        )

        filename = f'{most_common_month}_{str(day)}_{str(year)}_mapbox_graph.html'
        month_path = f'{save_path}/{str(year)}_{most_common_month}/'

        if not os.path.exists(month_path):
            os.makedirs(month_path)

        fig.write_html(os.path.join(month_path, filename))

        #print(f"Graph saved successfully as {filename}")

    except Exception as e:
        print(f"Grafikleme başarısız oldu, {day}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AmbulanceApp(root)
    root.mainloop()

import pandas as pd
import numpy as np
import datetime as dt


# İMZA ATAN PERSONEL RAPORU
df_signed= pd.read_excel(r"Downloads\İmza Atan Personel Raporu_20250526131359088.xls")

# NÖBET GÜNÜ İMZA ATMAYAN PERSONEL RAPORU
df_unsigned= pd.read_excel(r"Downloads\Nöbet Günü İmza Atmayan Personel Raporu_20250526131359791.xls")

# PERSONEL NÖBET LİSTESİ
df_staff_list= pd.read_excel(r"Downloads\Personel-Nöbet-Listesi (26).xls", header=None)

# ASHİ ADLARININ OLDUĞU SÖZLÜK
team_keyword= pd.read_csv(r"data\keywords\team_code_match\eu_team_code.csv")

# İSTASYON ÇALIŞMA SAATLERİ VE GEREKLİ SAĞLIKÇI - SÜRÜCÜ SAYISI
station_start_hours= pd.read_excel(r"data\keywords\station_start_hours\station_start_hours.xlsx")

df_signed.columns= ['İsim', 'Soyisim', 'T.C No', 'Telefon Numarası','Başlama Tarihi', 'Bitiş Tarihi','Nöbet Görevi','Giriş Tarihi', 'Çıkış Tarihi','Giriş Açıklama', 'Çıkış Açıklama', 'Nöbet Silindi Mi ?','Birim', 'Ekip Kodu', 'Ekip Adı']
df= pd.concat([df_signed, df_unsigned])

df= df[df['Birim'].astype(str).str.contains('ASHİ')]


team_dict= dict(zip(team_keyword['GENEL AD'], team_keyword['ASOS']))

df['Birim']= df['Birim'].astype(str).str.strip()
df['Ekip Kodu']= df['Birim'].map(team_dict)


station_start_hours['İSTASYON ADI'] = station_start_hours['İSTASYON ADI'].astype(str).str.strip()
team_dict_2= dict(zip(team_keyword['112ONLINE'], team_keyword['ASOS']))
station_start_hours['Ekip Kodu']= station_start_hours['İSTASYON ADI'].map(team_dict_2)
station_start_hours= station_start_hours[station_start_hours['Ekip Kodu'].notna()]
station_start_hours.drop(columns=['İSTASYON ADI'], inplace=True)

# merge Dataframe of signs with station working hours
df= pd.merge(df, station_start_hours, left_on='Ekip Kodu', right_on='Ekip Kodu')

# Clean Personel Nöbet Listesi
def staff_shift_file_cleaning(df):

    # WARNING: READ YOUR EXCEL FILE WITH header=None , F.e = pd.read_excel("df.xlsx", header=None)

    # Identify station rows: col1 has value, cols 2–4 are empty
    station_mask = df[1].notna() & df[[2, 3, 4]].isna().all(axis=1)
    df["RawStation"] = df[1].where(station_mask)

    # Forward fill station names
    df["İstasyon"] = df["RawStation"].ffill()
    df.columns= df.loc[df[df[1] == 'İsim'].index[0]]
    df= df[[col for col in df.columns if pd.notna(col)]]
    df.rename(columns={df.columns[-1]: 'İstasyon'}, inplace=True)
    df= df[(df['Kimlik No'].notna()) & (df['Kimlik No'] != 'Kimlik No')]

    return df

df_staff_list= staff_shift_file_cleaning(df_staff_list)
df_staff_list['İstasyon']= df_staff_list['İstasyon'].astype(str).str.strip()
df_staff_list['Ekip Kodu']= df_staff_list['İstasyon'].map(team_dict_2)
df_staff_list= df_staff_list[df_staff_list['Ekip Kodu'].notna()]
df_staff_list['Çalışma Türü']= pd.NA

# Find doctors from the list
df_staff_list.loc[(df_staff_list['Branş'] == 'YOK') & (df_staff_list['Görev'] == 'Ekip Sorumlusu'), 'Çalışma Türü']= 'Saha Doktor'

df_staff_list['Görev']= df_staff_list['Görev'].astype(str).str.strip()
df_staff_list.loc[((df_staff_list['Görev'].isin(['Ekip Sorumlusu', 'Yardımcı Sağlık Personeli'])) & (df_staff_list['Çalışma Türü'] != 'Saha Doktor')), 'Çalışma Türü']= 'Saha Sağlık Personeli'
df_staff_list.loc[df_staff_list['Görev']=='Sürücü', 'Çalışma Türü']= 'Sürücü'
df_staff_list= df_staff_list[df_staff_list['Görev']!='Refakatçi']

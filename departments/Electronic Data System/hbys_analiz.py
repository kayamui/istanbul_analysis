import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

path= str(input('Please enter the file path: '))
excel_sep= pd.ExcelFile(path)

df11= {sheet_name: excel_sep.parse(sheet_name) for sheet_name in excel_sep.sheet_names}
print(df11.keys())

def key_path():
  key_path= str(input('Please enter the key file path: '))
  try:
    df_eylul= df11[key_path]
    return df_eylul

  except:
    'Wrong input, try again'
    return key_path()


df_eylul= key_path()
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

def format_timedelta(seconds):
    """Formats timedelta in seconds to HH:MM:SS string."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

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

def hbys_hastane_tablosu():
  tabletten_gönderilmeyen= df_notablet.groupby(['Nakledilen Hastane']).agg({'Tabletten Gönderilme Tarih Saat':'sum'}).reset_index()
  tabletten_gönderilmeyen.rename(columns={'Tabletten Gönderilme Tarih Saat': 'Tabletten Gönderilmedi'},inplace=True)
  tabletten_gönderilen= df_tablet.groupby(['Nakledilen Hastane']).agg({'value':'sum'}).reset_index()
  tabletten_gönderilen.rename(columns={'value':'Tabletten Gönderilen'},inplace=True)
  onayli_sayisi= df_eylul.groupby(['Nakledilen Hastane', 'Onaylı']).agg({'value':'sum'}).reset_index()
  onayli= onayli_sayisi[onayli_sayisi['Onaylı']=='Evet']
  onayli.drop(columns='Onaylı', inplace=True)
  onaysiz= onayli_sayisi[onayli_sayisi['Onaylı']=='Hayır']
  onaysiz.drop(columns='Onaylı', inplace=True)
  onayli.rename(columns={'value':'Onaylı'},inplace=True)
  onaysiz.rename(columns={'value':'Onaysız'},inplace=True)
  toplam_vaka= df_eylul.groupby('Nakledilen Hastane').agg({'value':'sum'})
  toplam_vaka.rename(columns={'value':'Toplam Vaka'},inplace=True)
  onay_farki= df_onayli.groupby('Nakledilen Hastane').agg({'onay_farki':'mean'}).reset_index()
  onay_farki['onay_farki'].fillna(0, inplace=True)
  onay_farki['onay_farki']= onay_farki['onay_farki'].apply(format_timedelta)
  onay_farki.rename(columns={'onay_farki':'Doktor Onaylama Süresi'},inplace=True)


  merged_df = tabletten_gönderilen.merge(tabletten_gönderilmeyen, on='Nakledilen Hastane', how='outer')
  merged_df = merged_df.merge(onayli, on='Nakledilen Hastane', how='outer')
  merged_df = merged_df.merge(onaysiz, on='Nakledilen Hastane', how='outer')
  merged_df = merged_df.merge(toplam_vaka, on='Nakledilen Hastane', how='outer')
  merged_df = merged_df.merge(onay_farki, on='Nakledilen Hastane', how='outer')
  merged_df.fillna(0, inplace=True)
  merged_df['Onaylı Oranı']= round(merged_df['Onaylı']/merged_df['Toplam Vaka'] * 100, 2)
  merged_df['Onaysız Oranı']= 100- merged_df['Onaylı Oranı']
  merged_df.sort_values(by='Onaysız Oranı', ascending=False, inplace=True)

  return merged_df

df_ekip_hbys= hbys_ekip_tablosu()
df_hastane_hbys= hbys_hastane_tablosu()
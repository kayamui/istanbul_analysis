# -*- coding: utf-8 -*-
"""staff_work_hours.ipynb

Automatically generated by Colab.

"""

import pandas as pd
import numpy as np

excel_file = pd.ExcelFile('C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/case_reports/europe/2024/monthly/6-HAZİRAN 2024 AVR ASOS TANIDÖNÜŞTÜRÜLMÜŞ DEFTER.xlsx')
dataframes= {sheet_name:excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}
dataframes.keys()

case_report= dataframes['52852-DEFTER'].copy()

case_report['Ekipteki Kişiler']= case_report['Ekipteki Kişiler'].str.split(',')

case_report= case_report.explode('Ekipteki Kişiler')

case_report= case_report[case_report['Ekipteki Kişiler'].str.contains('Sürücü')]

case_report['Ekipteki Kişiler']= case_report['Ekipteki Kişiler'].str.split(' - Sürücü')

case_report['Ekipteki Kişiler']= case_report['Ekipteki Kişiler'].apply(lambda x: x[0].strip())

case_report['Start Date/Time']= case_report['Vakaya Çıkış Tarihi'] + ' ' + case_report['Vakaya Çıkış Saati']
case_report['Return Date/Time']= case_report['İstasyona Dönüş Tarihi'] + ' ' + case_report['İstasyona Dönüş Saati\n']

case_report['Start Date/Time']

def convert_to_datetime(date_str):
    try:
        return pd.to_datetime(date_str, format= '%d-%m-%Y %H:%M:%S')
    except:
        try:
          return pd.to_datetime(date_str, format= '%Y-%m-%d %H:%M:%S')
        except:
          return '-'

case_report['Start Date/Time']= case_report['Start Date/Time'].apply(convert_to_datetime)
case_report['Return Date/Time']= case_report['Return Date/Time'].apply(convert_to_datetime)

case_report[case_report['Start Date/Time']=='-']

case_report[case_report['Return Date/Time'] == '-']

case_report['Start Date/Time'].fillna('-', inplace=True)
case_report['Return Date/Time'].fillna('-', inplace=True)

case_report= case_report[case_report['Start Date/Time'] != '-']
case_report= case_report[case_report['Return Date/Time'] != '-']

case_report['Total Time in Minutes']= (case_report['Return Date/Time'] - case_report['Start Date/Time']).dt.total_seconds() / 60
case_report

case_report.drop_duplicates(subset=['KKM Protokol','Ekip No'], inplace=True)

case_report = case_report[case_report['Ekip No'] != 'BKR6']

case_report= case_report[case_report['Total Time in Minutes'] < 300]

case_report.groupby(['MANUEL ŞEF TARİHİ','Ekipteki Kişiler']).agg({'Total Time in Minutes': 'sum'}).sort_values(by='Total Time in Minutes', ascending=False).reset_index()

1358/60

case_report[(case_report['MANUEL ŞEF TARİHİ'] == '2024-06-06') & (case_report['Ekipteki Kişiler'] == 'YUNUS SARSILMAZ')]

shift_times = pd.read_excel('C:/Users/mkaya/Downloads/shift_times.xlsx')

shift_times['Ekipteki Kişiler']= shift_times['İsim'] + ' ' + shift_times['Soyisim']

shift_times['Ekipteki Kişiler']= shift_times['Ekipteki Kişiler'].str.strip()
case_report['Ekipteki Kişiler']= case_report['Ekipteki Kişiler'].str.strip()

shift_times.rename(columns= {'Başlangıç Tarihi':'MANUEL ŞEF TARİHİ'}, inplace=True)

shift_times

shift_times['Çalışma Saati']= (shift_times['Bitiş Tarihi'] - shift_times['MANUEL ŞEF TARİHİ']).dt.total_seconds() / 60 / 60

shift_times['MANUEL ŞEF TARİHİ']=pd.to_datetime(shift_times['MANUEL ŞEF TARİHİ'], format='%d-%m-%Y %H:%S')
shift_times['Bitiş Tarihi']=pd.to_datetime(shift_times['Bitiş Tarihi'], format='%d-%m-%Y %H:%S')

shift_times= shift_times[['Ekipteki Kişiler', 'MANUEL ŞEF TARİHİ','Çalışma Saati']]

shift_times['MANUEL ŞEF TARİHİ'].dt.strftime('%H-%M-%S').unique()

shift_times['MANUEL ŞEF TARİHİ'].fillna('-', inplace=True)
shift_times= shift_times[shift_times['MANUEL ŞEF TARİHİ'] != '-']

shift_times['MANUEL ŞEF TARİHİ']=pd.to_datetime(shift_times['MANUEL ŞEF TARİHİ'], format='%d-%m-%Y %H:%S')

shift_times.loc[shift_times['MANUEL ŞEF TARİHİ'].dt.strftime('%H-%M-%S').str.contains('04-00-00|03-00-30'), 'MANUEL ŞEF TARİHİ'] = shift_times['MANUEL ŞEF TARİHİ'] - pd.Timedelta(days=1)



shift_times['MANUEL ŞEF TARİHİ']= shift_times['MANUEL ŞEF TARİHİ'].dt.strftime('%Y-%m-%d')

shift_times['Ekipteki Kişiler']= shift_times['Ekipteki Kişiler'].str.strip()
case_report['Ekipteki Kişiler']= case_report['Ekipteki Kişiler'].str.strip()

case_report['MANUEL ŞEF TARİHİ']= case_report['MANUEL ŞEF TARİHİ'].dt.strftime('%Y-%m-%d')

case_report_merged= pd.merge(case_report, shift_times, on=['Ekipteki Kişiler', 'MANUEL ŞEF TARİHİ'], how='inner')

case_report_merged[(case_report_merged['Ekipteki Kişiler']== 'ÖZCAN PARLAK') & (case_report_merged['MANUEL ŞEF TARİHİ']== '2024-06-03')]


case_report_merged['Work Minutes']= case_report_merged['Çalışma Saati'] * 60

case_report_merged= case_report_merged[(case_report_merged['Çalışma Saati'] == 12) | (case_report_merged['Çalışma Saati'] == 8)]

case_report_merged

clear_table= case_report_merged.groupby(['Ekipteki Kişiler', 'MANUEL ŞEF TARİHİ','Ekip No']).agg({'Total Time in Minutes': 'sum', 'Work Minutes': 'mean', 'Çalışma Saati':'mean'}).sort_values(by='Total Time in Minutes', ascending=False).reset_index()

clear_table['Free Time'] = clear_table['Work Minutes'] - clear_table['Total Time in Minutes']

clear_table[clear_table['Free Time']>0].sort_values(by='Free Time', ascending=False)

len(clear_table[clear_table['Free Time']<0])

clear_table_positives= clear_table[clear_table['Free Time']>0]
clear_table_negatives= clear_table[clear_table['Free Time']<0]

clear_table_positives= clear_table_positives.rename(columns={'Total Time in Minutes':'Meşguliyet Süresi(Dakika)', 'Free Time':'Boşluk Süresi(Dakika)', 'MANUEL ŞEF TARİHİ':'Şef Tarihi','Ekipteki Kişiler':'Sürücü Adı'}).drop(columns=['Work Minutes'])[['Sürücü Adı','Ekip No', 'Şef Tarihi','Çalışma Saati','Meşguliyet Süresi(Dakika)', 'Boşluk Süresi(Dakika)']]

clear_table_positives.sort_values(by='Sürücü Adı', ascending=False, inplace=True)



case_report[(case_report['Ekipteki Kişiler'] == 'UTKU YALÇIN')]

case_report_merged[(case_report_merged['Ekipteki Kişiler']=='KAAN DÜLGER') & (case_report_merged['MANUEL ŞEF TARİHİ']=='2024-06-14')]

clear_table_positives.groupby('Sürücü Adı').agg({'Boşluk Süresi(Dakika)':'mean', 'Ekip No':'max'}).sort_values(by='Boşluk Süresi(Dakika)', ascending=False).reset_index()

clear_table_positives.to_excel('C:/Users/mkaya/Downloads/clear_table_positives.xlsx', index=False)

clear_table_positives

clear_table_positives.groupby(['Sürücü Adı', 'Çalışma Saati']).agg({'Boşluk Süresi(Dakika)':'mean', 'Meşguliyet Süresi(Dakika)':'mean','Ekip No':'max'}).reset_index().sort_values(by='Sürücü Adı').to_excel('C:/Users/mkaya/Downloads/clear_table_positives.xlsx', index=False)

case_report[case_report['Ekipteki Kişiler']=='İBRAHİM ŞEKER']



clear_table_positives[clear_table_positives['Sürücü Adı'] == 'KAAN DÜLGER']

clear_table_negatives

(clear_table_positives['Çalışma Saati'] == 12) | (clear_table_positives['Çalışma Saati'])

clear_table_positives

clear_table_negatives


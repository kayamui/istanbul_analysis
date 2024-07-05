def patient_types_city_based():
  
  import pandas as pd
  import numpy as np

  import datetime as dt

  import os

  import matplotlib.pyplot as plt
  import seaborn as sns
  import warnings
  warnings.filterwarnings('ignore')

  path= str(input('Please paste the path of the file: '))

  hospitals= pd.read_excel(path)

  hospital_name=str(input('Please enter a name for the file: '))

  print('--------------------------------------------------------------------------------------------------\n\n')


  columns= ["KKM Protokol",
            'Çağrı Nedeni',
            "Cinsiyet",
            "Yaş",
            "Adli Vaka",
            "Nakledilen Hastane",
            "ICD10 TANI\nADI",
            "ICD10 2'NCİ SEVİYE GRUP ADI",
            "ICD10 1'İNCİ SEVİYE GRUP ADI",
            "Triaj",
            "Bilinç",
            "Pupiller",
            "Solunum",
            "Cilt",
            "Nabız",
            "Tansiyon",
            "Glukoz",
            "Ateş",
            "SPO2",
            "Solunum Değeri",
            "Nabız Değeri"]

  single_hospital = hospitals.copy()
  single_hospital= single_hospital[columns]
  single_hospital['Sayı']= 1
  single_hospital= single_hospital[single_hospital['Nakledilen Hastane'] != '-']

  #---------------------------> GENDERS
  df_genders= single_hospital[single_hospital['Cinsiyet'] != '-']
  genders = df_genders.groupby(['Nakledilen Hastane', 'Cinsiyet']).agg({'Sayı': 'sum'}).reset_index().sort_values(by= 'Nakledilen Hastane')
  genders= genders.pivot_table(index= 'Nakledilen Hastane', columns= 'Cinsiyet', values= 'Sayı', aggfunc= 'sum').fillna(0)
  genders['CİNSİYET TOPLAM']= genders['ERKEK'] + genders['KADIN']
  genders['CİNSİYET YÜZDE']= (genders['CİNSİYET TOPLAM'] / sum(genders['CİNSİYET TOPLAM']) * 100)
  genders= genders.sort_values(by= 'CİNSİYET TOPLAM', ascending= False)
  genders.to_excel(f'{hospital_name} Cinsiyet.xlsx')

  #-------------------------> AGES

  df_age= single_hospital[single_hospital['Yaş'] != '-']
  df_age= df_age[df_age['Yaş'] != 'Kişisi Yok']
  df_age['Yaş']= df_age['Yaş'].astype(int)

  ages = pd.DataFrame(index=['65-74', '75-84', '85>'], columns=single_hospital['Nakledilen Hastane'].unique())

  for hospital in single_hospital['Nakledilen Hastane'].unique():
    df_age_hospital = df_age[df_age['Nakledilen Hastane'] == hospital]
    ages.loc['65-74', hospital] = len(df_age_hospital[(df_age_hospital['Yaş'] >= 65) & (df_age_hospital['Yaş'] < 75)]) # Use .loc with comma to access the correct row after transpose
    ages.loc['75-84', hospital] = len(df_age_hospital[(df_age_hospital['Yaş'] >= 75) & (df_age_hospital['Yaş'] <= 85)])
    ages.loc['85>', hospital] = len(df_age_hospital[df_age_hospital['Yaş'] > 85])

  # Transpose the DataFrame after filling values
  ages = ages.transpose()
  ages['YAŞ TOPLAM'] = ages.sum(axis=1)
  ages['YAŞ YÜZDE']= (ages['YAŞ TOPLAM'] / sum(ages['YAŞ TOPLAM']) * 100)
  ages = ages.sort_values(by='YAŞ TOPLAM', ascending= False)
  ages.to_excel(f'{hospital_name} Yaş.xlsx')

  #-----------------------------> PULSES

  pulses= pd.DataFrame(index= ['<60', '60-99', '>= 100'], columns= single_hospital['Nakledilen Hastane'].unique())
  df_pulse= single_hospital[single_hospital['Nabız Değeri'] != '-']
  df_pulse['Nabız Değeri']= df_pulse['Nabız Değeri'].astype(int)
  for hospital in single_hospital['Nakledilen Hastane'].unique():
    df_pulse_hospital = df_pulse[df_pulse['Nakledilen Hastane'] == hospital]
    pulses.loc['<60', hospital] = len(df_pulse_hospital[(df_pulse_hospital['Nabız Değeri'] < 60)]) # Use .loc with comma to access the correct row after transpose
    pulses.loc['60-99', hospital] = len(df_pulse_hospital[(df_pulse_hospital['Nabız Değeri'] >= 60) & (df_pulse_hospital['Nabız Değeri'] < 100)])
    pulses.loc['>= 100', hospital] = len(df_pulse_hospital[df_pulse_hospital['Nabız Değeri'] >= 100])
    # Transpose the DataFrame after filling values
  pulses = pulses.transpose()
  pulses['NABIZ TOPLAM'] = pulses.sum(axis=1)
  pulses['NABIZ YÜZDE']= (pulses['NABIZ TOPLAM'] / sum(pulses['NABIZ TOPLAM']) * 100)
  pulses = pulses.sort_values(by='NABIZ TOPLAM', ascending= False)
  pulses.to_excel(f'{hospital_name} Nabız.xlsx')

  #------------------------------> TRIAGE

  df_triage= single_hospital[single_hospital["Triaj"] != '-']
  triages= df_triage.groupby(['Nakledilen Hastane','Triaj']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  triages= triages.pivot_table(index= 'Nakledilen Hastane', columns= 'Triaj', values= 'Sayı', aggfunc= 'sum').fillna(0)
  triages['TRİAJ TOPLAM']= triages.sum(axis=1)
  triages['TRİAJ YÜZDE']= (triages['TRİAJ TOPLAM'] / sum(triages['TRİAJ TOPLAM']) * 100)
  triages= triages.sort_values(by= 'TRİAJ TOPLAM', ascending= False)
  triages.to_excel(f'{hospital_name} Triyaj.xlsx')

  #------------------------------> CALL REASONS

  df_call_reason= single_hospital.groupby(['Nakledilen Hastane','Çağrı Nedeni']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  call_reasons= df_call_reason.pivot_table(index= 'Nakledilen Hastane', columns= 'Çağrı Nedeni', values= 'Sayı', aggfunc= 'sum').fillna(0)
  call_reasons['ÇAĞRILAR TOPLAM']= call_reasons.sum(axis=1)
  call_reasons['ÇAĞRILAR YÜZDE']= (call_reasons['ÇAĞRILAR TOPLAM'] / sum(call_reasons['ÇAĞRILAR TOPLAM']) * 100)
  call_reasons= call_reasons.sort_values(by= 'ÇAĞRILAR TOPLAM', ascending= False)
  call_reasons.to_excel(f'{hospital_name} Çağrı Nedeni.xlsx')

  #------------------------------> SPO2

  spo2s= pd.DataFrame(index= ['<80', '80-84', '85-89', '90-94', '>=95'], columns= single_hospital['Nakledilen Hastane'].unique())
  df_spo2= single_hospital[single_hospital['SPO2'] != '-']
  df_spo2['SPO2']= df_spo2['SPO2'].astype(int)

  for hospital in single_hospital['Nakledilen Hastane'].unique():
    df_spo2_hospital = df_spo2[df_spo2['Nakledilen Hastane'] == hospital]
    spo2s.loc['<80', hospital] = len(df_spo2_hospital[(df_spo2_hospital['SPO2'] < 80)]) # Use .loc with comma to access the correct row after transpose
    spo2s.loc['80-84', hospital] = len(df_spo2_hospital[(df_spo2_hospital['SPO2'] >= 80) & (df_spo2_hospital['SPO2'] <= 84)])
    spo2s.loc['85-89', hospital] = len(df_spo2_hospital[(df_spo2_hospital['SPO2'] >= 85) & (df_spo2_hospital['SPO2'] <= 89)])
    spo2s.loc['90-94', hospital] = len(df_spo2_hospital[(df_spo2_hospital['SPO2'] >= 90) & (df_spo2_hospital['SPO2'] <= 94)])
    spo2s.loc['>=95', hospital] = len(df_spo2_hospital[df_spo2_hospital['SPO2'] >= 95])

  # Transpose the DataFrame after filling values
  spo2s = spo2s.transpose()
  spo2s['SPO2 TOPLAM'] = spo2s.sum(axis=1)
  spo2s['SPO2 YÜZDE']= (spo2s['SPO2 TOPLAM'] / sum(spo2s['SPO2 TOPLAM']) * 100)
  spo2s = spo2s.sort_values(by='SPO2 TOPLAM', ascending= False)
  spo2s.to_excel(f'{hospital_name} SPO2.xlsx')

  #----------------------------------> ICD10 CODES

  single_hospital = single_hospital.rename(columns={
      "ICD10 TANI\nADI": 'ICD10 Tanı Adı',
      "ICD10 2'NCİ SEVİYE GRUP ADI": 'ICD10 2. Seviye Grup Adı',
      "ICD10 1'İNCİ SEVİYE GRUP ADI": 'ICD10 1. Seviye Grup Adı'
  })

  df_icd= single_hospital.copy()
  df_icd['ICD10 Tanı Adı']= df_icd['ICD10 Tanı Adı'].fillna('NO ICD10')
  df_icd= df_icd[df_icd['ICD10 Tanı Adı'].str.contains('ARREST|ÖLÜM')]
  icds= df_icd.groupby(['Nakledilen Hastane', 'ICD10 Tanı Adı']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  icds= icds.pivot_table(index= 'Nakledilen Hastane', columns= 'ICD10 Tanı Adı', values= 'Sayı', aggfunc= 'sum').fillna(0)
  icds['ICD ARREST']= icds.sum(axis=1)
  icds['ICD YÜZDE']= (icds['ICD ARREST'] / sum(icds['ICD ARREST']) * 100)
  icds= icds.sort_values(by= 'ICD ARREST', ascending= False)
  icds= icds[['ICD ARREST', 'ICD YÜZDE']]
  icds.to_excel(f'{hospital_name} ARREST.xlsx')

  merged_df = pd.concat([genders, ages, pulses, triages, call_reasons, spo2s, icds], axis=1)
  merged_df.to_excel('test_merged.xlsx')

  return "Many loves from Muhammed Kaya :*"
patient_types_city_based()
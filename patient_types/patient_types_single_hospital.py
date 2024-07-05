def patient_types():

  import pandas as pd
  import numpy as np

  import datetime as dt

  import os

  import matplotlib.pyplot as plt
  import seaborn as sns
  import warnings
  warnings.filterwarnings('ignore')

  path= str(input('Please paste the path of the file here: '))

  hospitals= pd.read_excel(path)

  names= sorted(hospitals['Nakledilen Hastane'].unique())
  for i in names:
    print(i)
  print('--------------------------------------------------------------------------------------------------\n\n')

  hospital_name= str(input('Please paste the name of the hospital here: '))
  hospital_name= hospital_name.upper()

  single_hospital= hospitals[hospitals['Nakledilen Hastane'].str.contains(hospital_name)]

  columns= ["KKM Protokol",
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

  single_hospital= single_hospital[columns]
  single_hospital['Sayı']= 1


  genders= single_hospital.groupby('Cinsiyet').agg({'Sayı':'sum'}).reset_index().to_excel(f'{hospital_name} Cinsiyet.xlsx')

  ages= pd.DataFrame(index= ['65-74', '75-84', '85>'], columns= [f'{hospital_name}'])
  df_age= single_hospital[single_hospital['Yaş'] != '-']
  df_age= df_age[df_age['Yaş'] != 'Kişisi Yok']
  df_age['Yaş']= df_age['Yaş'].astype(int)
  ages.loc[('65-74')][f'{hospital_name}']= len(df_age[(df_age['Yaş'] >= 65) &( df_age['Yaş'] < 75)])
  ages.loc[('75-84')][f'{hospital_name}']= len(df_age[(df_age['Yaş'] >= 75) &( df_age['Yaş'] <= 85)])
  ages.loc['85>'][f'{hospital_name}']= len(df_age[df_age['Yaş'] > 85])

  ages.reset_index().to_excel(f'{hospital_name} Ages.xlsx')

  pulse= pd.DataFrame(index= ['<60', '60-100', '100>'], columns= [f'{hospital_name}'])
  pulses= single_hospital[single_hospital['Nabız Değeri'] != '-']
  pulses['Nabız Değeri']= pulses['Nabız Değeri'].astype(int)
  pulse.loc['<60'][f'{hospital_name}']= len(pulses[pulses['Nabız Değeri'] < 60])
  pulse.loc['60-100'][f'{hospital_name}']= len(pulses[(pulses['Nabız Değeri'] >= 60) & (pulses['Nabız Değeri'] <= 100)])
  pulse.loc['100>'][f'{hospital_name}']= (len(pulses[pulses['Nabız Değeri'] > 100]))

  pulse.reset_index().rename(columns= {'index': 'Nabız'}).to_excel(f'{hospital_name} Nabız.xlsx')

  tensions= single_hospital[single_hospital['Tansiyon'] != '-']
  tensions['Büyük Tansiyon']= tensions['Tansiyon'].apply(lambda x: x.split('/')[0])
  tensions['Küçük Tansiyon']= tensions['Tansiyon'].apply(lambda x: x.split('/')[1])
  tensions['Büyük Tansiyon']= tensions['Büyük Tansiyon'].astype(float)
  tensions['Küçük Tansiyon']= tensions['Küçük Tansiyon'].astype(float)

  tensions_frame= pd.DataFrame(index= ['<90', '90-120', '120-140', '>140', 'Toplam'], columns= [f'{hospital_name}', 'Yüzde'])
  tensions_frame.loc['>140'][f'{hospital_name}']= len(tensions[(((tensions['Büyük Tansiyon'] > 18) & (tensions['Büyük Tansiyon'] < 30)) | (tensions['Büyük Tansiyon'] > 180))])
  tensions_frame.loc['90-120'][f'{hospital_name}']= len(tensions[(((tensions['Büyük Tansiyon'] >= 9) & (tensions['Büyük Tansiyon'] <= 12)) | ((tensions['Büyük Tansiyon'] >= 90) & (tensions['Büyük Tansiyon'] < 120)))])
  tensions_frame.loc['120-140'][f'{hospital_name}']= len(tensions[(((tensions['Büyük Tansiyon'] >= 12) & (tensions['Büyük Tansiyon'] < 14)) | ((tensions['Büyük Tansiyon'] >= 120) & (tensions['Büyük Tansiyon'] < 140)))])
  tensions_frame.loc['<90'][f'{hospital_name}']= len(tensions[tensions['Büyük Tansiyon'] < 90])
  tensions_frame.loc['<90']['Yüzde']= tensions_frame.loc['<90'][f'{hospital_name}'] / sum(tensions_frame[f'{hospital_name}']) * 100
  tensions_frame.loc['90-120']['Yüzde']= tensions_frame.loc['90-120'][f'{hospital_name}'] / sum(tensions_frame[f'{hospital_name}']) * 100
  tensions_frame.loc['120-140']['Yüzde']= tensions_frame.loc['120-140'][f'{hospital_name}'] / sum(tensions_frame[f'{hospital_name}']) * 100
  tensions_frame.loc['>140']['Yüzde']= tensions_frame.loc['>140'][f'{hospital_name}'] / sum(tensions_frame[f'{hospital_name}']) * 100
  tensions_frame.loc['Toplam']= tensions_frame.sum()

  tensions_frame.reset_index().rename(columns= {'index': 'Sistolik Kan Basıncı'}).to_excel(f'{hospital_name} Tansiyon.xlsx')

  spo2= single_hospital[single_hospital['SPO2'] != '-']
  spo2['SPO2']= spo2['SPO2'].astype(int)
  spo2s= pd.DataFrame(index= ['<80', '80-85', '85-90', '90-95', '>95', 'Toplam'], columns= [f'{hospital_name}','Yüzde'])
  spo2s.loc['<80'][f'{hospital_name}']= len(spo2[spo2['SPO2'] < 80])
  spo2s.loc['80-85'][f'{hospital_name}']= len(spo2[(spo2['SPO2'] >= 80) & (spo2['SPO2'] <= 85)])
  spo2s.loc['85-90'][f'{hospital_name}']= len(spo2[(spo2['SPO2'] >= 85) & (spo2['SPO2'] <= 90)])
  spo2s.loc['90-95'][f'{hospital_name}']= len(spo2[(spo2['SPO2'] >= 90) & (spo2['SPO2'] <= 95)])
  spo2s.loc['>95'][f'{hospital_name}']= len(spo2[spo2['SPO2'] > 95])
  spo2s.loc['Toplam']= spo2.sum()

  spo2s.to_excel(f'{hospital_name} SPO2.xlsx')

  single_hospital = single_hospital.rename(columns={
      "ICD10 TANI\nADI": 'ICD10 Tanı Adı',
      "ICD10 2'NCİ SEVİYE GRUP ADI": 'ICD10 2. Seviye Grup Adı',
      "ICD10 1'İNCİ SEVİYE GRUP ADI": 'ICD10 1. Seviye Grup Adı'
  })

  df_icd= single_hospital.groupby(['ICD10 Tanı Adı']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  df_icd['Yüzde']= df_icd['Sayı'] / sum(df_icd['Sayı']) * 100

  df_icd.to_excel(f'{hospital_name} ICD10 Tanı Adı.xlsx')

  df_triaj= single_hospital[single_hospital["Triaj"] != '-']
  df_triaj['Sayı']= 1
  triaj= df_triaj.groupby(['Triaj']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  triaj['Yüzde']= df_triaj['Sayı'] / sum(df_triaj['Sayı']) * 100

  df_triaj.to_excel(f'{hospital_name} Triaj.xlsx')

  df_bilinç= single_hospital.groupby(['Bilinç']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  df_bilinç['Yüzde']= df_bilinç['Sayı'] / sum(df_bilinç['Sayı']) * 100

  df_bilinç.to_excel(f'{hospital_name} Bilinç.xlsx')

  df_pupils= single_hospital[single_hospital['Pupiller'] != '-']
  df_pupils= df_pupils.groupby(['Pupiller']).agg({'Sayı':'sum'}).sort_values(by= 'Sayı', ascending= False).reset_index()
  df_pupils['Yüzde']= df_pupils['Sayı'] / sum(df_pupils['Sayı']) * 100

  df_pupils.to_excel(f'{hospital_name} Pupiller.xlsx')
patient_types()
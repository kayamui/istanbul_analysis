import pandas as pd
import datetime

shift_list= pd.read_excel('C:/Users/mkaya/Downloads/Personel-Nöbet-Listesi (10).xls')

keyword_team_code= pd.read_csv('C:/Users/mkaya/Onedrive/Masaüstü/istanbul112_hidden/data/keywords/team_code_match/eu_team_code.csv')
keyword_team_dict= dict(zip(keyword_team_code['112ONLINE'].astype(str).str.strip(), keyword_team_code['ASOS'].astype(str).str.strip()))

df_cases= pd.read_excel('C:/users/mkaya/Downloads/İhbar işlemleri (78).xls')
df_cases.rename(columns={'Ekip Kodu': 'Ekip No'}, inplace=True)

df_report= pd.read_excel('C:/Users/mkaya/Downloads/Genel Vaka Araştırma Raporu_20250321104344226.xls')

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
  shift_list= shift_list[shift_list['Görev'].isin(['Ekip Sorumlusu','Yardımcı Sağlık Personeli'])]
  shift_list['İsim Soyisim'] = shift_list['İsim'] + ' ' + shift_list['Soyisim']
  shift_list.drop(columns=['İsim', 'Soyisim'], inplace=True)

  shift_list= shift_list[shift_list['Ekip No'] != 'row']
  shift_list.insert(1, 'İsim Soyisim',shift_list.pop('İsim Soyisim'))
  shift_list.insert(1, 'İsim Soyisim',shift_list.pop('İsim Soyisim'))

  shift_list.reset_index(drop=True, inplace=True)

  return shift_list
shift_list= shift_list_cleaning(shift_list)

def call_filter(report, cases):

  #Read the case research report
  df_names = report

  #Notices File
  df_cases = cases

  df_names['Tarih']= pd.to_datetime(df_names['Vaka Veriliş\nTarihi'] + ' ' + df_names['Vaka Veriliş\nSaati'], format= '%d-%m-%Y %H:%M:%S')

  #Left only necessary columns
  df_names = df_names[['Ekip No', 'KKM Protokol','Tarih','Ekip Sorumlusu', 'Ekipteki Kişiler']] #, 'İhbar/Çağrı Tarihi', 'İhbar/Çağrı  Saati'
  #df_names['Tarih/Saat'] = df_names['İhbar/Çağrı Tarihi'] + df_names['İhbar/Çağrı  Saati']
  df_cases.rename(columns={'Ekip Kodu': 'Ekip No'}, inplace=True)
  df_unmatched= df_cases[df_cases['Durum'] == 'Eşleşebilecekler']
  df_unmatched= df_unmatched[df_unmatched['Ekip No'].isin(df_names['Ekip No'])]
  merged_df = pd.merge(df_cases, df_names, on=['KKM Protokol', 'Ekip No'], how = 'left')
  merged_df= pd.concat([merged_df, df_unmatched])
  merged_df.drop(columns = ['KKM Seri No', 'Adres', 'Vaka Yeri Açıklaması'], inplace = True)

  option= str(input('For filtering a specific day, press 1, for all days press any: '))

  if option=='1':
    year= int(input('Enter year: '))
    month= int(input('Enter month: '))
    day= int(input('Enter day: '))
    hour= int(input('Enter hour: '))
    # show only where merged_df['Tarih'] starting from year-month-day hour for 24 hours in every 4 days
    start_date = datetime.datetime(year, month, day, hour)
    end_date = start_date + datetime.timedelta(days=1)

    filtered_df = merged_df[
        (merged_df['Tarih'] >= start_date) & (merged_df['Tarih'] < end_date)
    ]

    for i in range(1, 8):
      try:
        start_date += datetime.timedelta(days=4)
        end_date = start_date + datetime.timedelta(days=1)

        temp_df = merged_df[
            (merged_df['Tarih'] >= start_date) & (merged_df['Tarih'] < end_date)
        ]
        filtered_df = pd.concat([filtered_df, temp_df], ignore_index=True)
      except:
        pass
  else:
    filtered_df = merged_df
  filtered_df = filtered_df.sort_values(by = ['Ekip Sorumlusu'])[['KKM Protokol', 'Ekip No', 'Tarih', 'Durum','Ekip Sorumlusu', 'Ekipteki Kişiler']]
  filtered_df.sort_values(by='Ekip Sorumlusu',ascending=True, inplace=True)
  #filtered_df.drop(columns=['İhbar/Çağrı Tarihi', 'İhbar/Çağrı  Saati', 'Tarih/Saat'], inplace=True)

  df_unmatched= filtered_df[filtered_df['Ekipteki Kişiler'].isna()].reset_index(drop=True)
  filtered_df= filtered_df[filtered_df['Ekipteki Kişiler'].notna()]

  return filtered_df, df_unmatched
filtered_df, df_unmatched= call_filter(df_report, df_cases)

def match_call_list(df_unmatched,shift_list ,filtered_df):
  unmatch_merged= pd.merge(df_unmatched, shift_list, on=['Ekip No'], how = 'inner')
  unmatch_merged['Başlangıç Tarihi']= pd.to_datetime(unmatch_merged['Başlangıç Tarihi'], format='%d-%m-%Y %H:%M')
  unmatch_merged['Bitiş Tarihi']= pd.to_datetime(unmatch_merged['Bitiş Tarihi'], format='%d-%m-%Y %H:%M')
  unmatch_merged['is_date_between']= unmatch_merged.apply(lambda x: x['Başlangıç Tarihi'] <= x['Tarih'] <= x['Bitiş Tarihi'], axis=1)
  unmatch_merged= unmatch_merged[unmatch_merged['is_date_between']==True]
  unmatch_merged= unmatch_merged.groupby(['KKM Protokol', 'Ekip No', 'Tarih', 'Durum']).agg({'İsim Soyisim':','.join}).reset_index()
  unmatch_merged['KKM Protokol']= unmatch_merged['KKM Protokol'].astype(int)

  df= pd.concat([filtered_df, unmatch_merged]).sort_values(by= ['Ekip Sorumlusu'], ascending=True)
  df['Ekipteki Kişiler']= df.apply(lambda x: x['İsim Soyisim'] if pd.isna(x['Ekipteki Kişiler']) else x['Ekipteki Kişiler'], axis=1)
  df.drop(columns=['İsim Soyisim'], inplace=True)

  case_bugs= df[(df['Durum']== 'Eşleşebilecekler') & df['Ekip Sorumlusu'].notna()]
  if len(case_bugs) > 0:
    print('------------------------\nHatalı Kayıtlar Bulundu!\n')
    for i in range(len(case_bugs)):
      print('KKM Protokol: ',case_bugs.iloc[i]['KKM Protokol'], '-->', 'Ekip No: ', case_bugs.iloc[i]['Ekip No'], '\n')

  return df
df= match_call_list(df_unmatched,shift_list ,filtered_df)

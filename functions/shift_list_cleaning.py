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
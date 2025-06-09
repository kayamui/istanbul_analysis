# %load staff_shift_file_celaning.py
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
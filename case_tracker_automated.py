def case_tracker():

  def bring_case():
    import pandas as pd
    import numpy as np
    import os

    import warnings
    warnings.filterwarnings('ignore')

    #Create the Final DF
    wrong_inputs= pd.DataFrame()
    wrong_inputs['KKM Protokol'] = []
    wrong_inputs['Ekip No'] = []
    wrong_inputs['Tarih'] = []
    wrong_inputs['Olası Hata'] = []

    #Find the Files
    file_paths= {}
    for item in os.listdir(os.getcwd()):
      if os.path.isfile(item):
        if 'yanlis_kontrolu' not in item:
          if 'manuel_atn' not in item:
            file_paths[os.path.getsize(item)] = item

    #Read Big(Reports) and Small Data(Notice Actions)
    df_big= pd.read_excel(file_paths[sorted(file_paths)[-1]])
    df_small= pd.read_excel(file_paths[sorted(file_paths)[-2]])

    df_big.rename(columns = {'Ekip Kodu' : 'Ekip No'}, inplace = True)
    df_small.rename(columns = {'Ekip Kodu' : 'Ekip No'}, inplace = True)

    df_merged = pd.merge(df_big, df_small,  on = ['KKM Protokol', 'Ekip No'])
    df_merged.fillna('00',inplace= True)
    
    df_merged['Tc Kimlik No\n'] = df_merged['Tc Kimlik No\n'].astype(str)
    df_merged['Tc Kimlik No\n'] = df_merged['Tc Kimlik No\n'].astype(str)
    df_merged['Tc Kimlik No\n'] = df_merged['Tc Kimlik No\n'].str.upper()

    df_merged['Hasta Adı'] = df_merged['Hasta Adı'].fillna('00')
    df_merged['Hasta Adı'] = df_merged['Hasta Adı'].str.upper()

    df_merged['Yaş'] = df_merged['Yaş'].replace('Kişisi Yok', 1000)
    df_merged['Yaş'] = df_merged['Yaş'].fillna(1000)

    df_merged["ICD10 TANI\nADI"] = df_merged["ICD10 TANI\nADI"].fillna('UNKNOWN')
    df_merged["ICD10 TANI\nADI"] = df_merged["ICD10 TANI\nADI"].astype(str)

    df_merged['Vaka Adresi'] = df_merged['Vaka Adresi'].str.upper()
    df_merged['İhbar Adresi'] = df_merged['İhbar Adresi'].str.upper()
    df_merged['KKM Açıklama'] = df_merged['KKM Açıklama'].str.upper()
    df_merged['Vaka Yeri Aciklama'] = df_merged['Vaka Yeri Aciklama'].str.upper()

    df_merged['Sonuç'] = df_merged['Sonuç'].fillna('False')

    df_merged[['Vaka Adresi']].fillna('UNKNOWN', inplace = True) 
    df_merged[['İhbar Adresi']].fillna('UNKNOWN', inplace = True)
    df_merged[['KKM Açıklama']].fillna('UNKNOWN', inplace = True)
    df_merged[['Vaka Yeri Aciklama']].fillna('UNKNOWN', inplace = True)

    df_merged[['Vaka Adresi']]= df_merged[['Vaka Adresi']].astype(str)
    df_merged[['İhbar Adresi']]= df_merged[['İhbar Adresi']].astype(str)
    df_merged[['KKM Açıklama']]= df_merged[['KKM Açıklama']].astype(str)
    df_merged[['Vaka Yeri Aciklama']]= df_merged[['Vaka Yeri Aciklama']].astype(str)

    df_merged['KM Difference']= df_merged['Dönüş KM'] - df_merged['Çıkış KM']


    #Patients Who Have National IDs Starting From '9', Meanwhile Temporary Accommodations
    syrian_insurances= df_merged[df_merged['Tc Kimlik No\n'].str.startswith('9')][['KKM Protokol','Ekip No','Tarih']]
    syrian_insurances['Olası Hata']= "99'lu Hasta Güvencesi"

    #Patients Without ID-With Insurance(SGK)
    withoutID_withInsurance= df_merged[(df_merged['Tc Kimlik No\n'].str.len() != 11) & (df_merged['Tc Kimlik No\n'] != '00')& (df_merged['Yaş'] != 'Kişisi Yok') &(df_merged['Güvence'] != 'Güvencesiz') & (df_merged['Yaş'].astype(str) != '0') ][['KKM Protokol','Ekip No','Tarih']]
    withoutID_withInsurance['Olası Hata']= "Kimliksiz Güvenceli Hasta"

    #Potential Tourists, and Checking Their Insurances
    potential_tourists= df_merged[(df_merged['Tc Kimlik No\n'].str.len() != 11)  & (df_merged['Güvence'] != '-') & (df_merged['Güvence'] != 'SGK') & (~df_merged['Hasta Adı'].str.contains('BEBEK|KIMLIK|KİMLİK|ISIMSIZ|İSİMSİZ')) ][['KKM Protokol','Ekip No','Tarih']]
    potential_tourists['Olası Hata']= "Turist Güvencesi"

    #Wrongly Inputted Ambulance Tracking Codes
    ambulance_tracking_number= df_merged[(df_merged['ATN No'].str.len() != 7) | ~((df_merged['ATN No'].str.upper().str.startswith('I')) | (df_merged['ATN No'].str.upper().str.startswith('İ')) | (df_merged['ATN No'].str.upper().str.startswith('K')) )].sort_values(by = 'ATN No')[['Ekip No','KKM Protokol', 'Tarih']]
    ambulance_tracking_number['Olası Hata']= "Ambulans Takip Numarası"

    #Hospital Check
    hospital_check= df_merged[(df_merged['Nakledilen Hastane'].str.contains('DİYALİZ|PERİTON|EK KAMPÜS BEYLİKDÜZÜ|POLİKLİ|ŞİŞLİ HAMİDİYE ETFAL|ÇAPA|AİLE|SAĞLIĞI MERKEZİ|DİLMENER|SEMT|T.C. SAĞLIK BAKANLIĞI İSTANBUL HASEKİ EĞİTİM VE ARAŞTIRMA HASTANESİ')) | (df_merged['Sevk Eden Hastane'].str.contains('DİYALİZ|PERİTON|EK KAMPÜS BEYLİKDÜZÜ|POLİKLİ|ŞİŞLİ HAMİDİYE ETFAL|ÇAPA|AİLE|SAĞLIĞI MERKEZİ|DİLMENER|SEMT|T.C. SAĞLIK BAKANLIĞI İSTANBUL HASEKİ EĞİTİM VE ARAŞTIRMA HASTANESİ')) | (df_merged['Sevk Edilen Hastane'].str.contains('DİYALİZ|PERİTON|EK KAMPÜS BEYLİKDÜZÜ|POLİKLİ|ŞİŞLİ HAMİDİYE ETFAL|ÇAPA|AİLE|SAĞLIĞI MERKEZİ|DİLMENER|SEMT|T.C. SAĞLIK BAKANLIĞI İSTANBUL HASEKİ EĞİTİM VE ARAŞTIRMA HASTANESİ'))][['KKM Protokol','Ekip No', 'Tarih']]
    hospital_check['Olası Hata']= "Hastane" 

    #Legally Sensitive
    legally_sensitive= df_merged[df_merged['Adli Vaka']  == 'Adli Vaka'][['KKM Protokol', 'Ekip No','Tarih']]
    legally_sensitive['Olası Hata']= "Adli Vaka" 

    #No Form Picture
    no_form= df_merged[df_merged['Vaka Formu Dosyası\n'] != 'Var'][['KKM Protokol','Ekip No','Tarih']]
    no_form['Olası Hata']= "Vaka Formu"

    #Long Reactions
    long_reactions= df_merged[(df_merged['İstasyon Reaksiyon Sn'] > 600) & (df_merged['Ekip No'] != 'UÇAK34')][['KKM Protokol','Ekip No','Tarih']]
    long_reactions['Olası Hata']= "Uzun Reaksiyon"

    #Urban-Rural
    urban_rural= df_merged[(df_merged['Kensel/Kırsal'] == 'Kırsal') & ~(df_merged['Ekip No'].str.contains("ARN|SRY|SLV|BÇK|ÇTL|EYP")) & (df_merged['Ekip No'] != 'HAVA34') ][['KKM Protokol','Ekip No', 'Tarih']]
    urban_rural['Olası Hata']= "Kentsel/Kırsal"

    #Newborn Check
    newborns= df_merged[((df_merged['Yeni Doğan'] == '-') & (df_merged['Yaş'] == 0)) | ((df_merged['Yeni Doğan'] != '-') & (df_merged['Yaş'] !=0)) ][['KKM Protokol','Ekip No', 'Tarih']]
    newborns['Olası Hata']= "Yeni Doğan"

    #Arrests
    arrests= df_merged[df_merged["ICD10 TANI\nADI"].str.contains("ARREST|ÖLÜM")][['Ekip No', 'KKM Protokol', 'Tarih']]
    arrests['Olası Hata']= "Arrest"


    #Internal Transports Might Filled as Emergencies
    internal_transports= df_merged[(df_merged['İhbar Adresi'].str.contains('HASTANE|NAKİL|NKL') | df_merged['Vaka Yeri Aciklama'].str.contains('HASTANE|NAKİL|NKL')) & (df_merged['Nakledilen Hastane'] != '-')][['KKM Protokol','Ekip No','Tarih'] ]
    internal_transports['Olası Hata']= "Medikal Girilmiş Nakil"

    #Transported by Others
    transported_by_others= df_merged[df_merged['Sonuç'].str.contains('Başka Araçla Nakil')][["KKM Protokol", "Ekip No", "Tarih"]]
    transported_by_others['Olası Hata']= "Başka Araçla Nakil"

    #Suspicious Medical Inputted Cases (TRAFFIC ACCIDENT? BEAT? SHOOTING?)
    suspicious_medicals= df_merged[((df_merged['Vaka Adresi'].str.contains('DARP|YARALAMA|TRAFİK|İNTİHAR|INTIHAR|BIÇAK|KAZA|KURŞUN|ADTK|AİTK|AITK|MOTOR|ARAÇ|ARAC')) | (df_merged['İhbar Adresi'].str.contains('DARP|YARALAMA|TRAFİK|İNTİHAR|INTIHAR|BIÇAK|KAZA|KURŞUN|ADTK|AİTK|AITK|MOTOR|ARAÇ|ARAC')) | (df_merged['KKM Açıklama'].str.contains('DARP|YARALAMA|TRAFİK|İNTİHAR|INTIHAR|BIÇAK|KAZA|KURŞUN|ADTK|AİTK|AITK|MOTOR|ARAÇ|ARAC')) | (df_merged['Vaka Yeri Aciklama'].str.contains('DARP|YARALAMA|TRAFİK|İNTİHAR|INTIHAR|BIÇAK|KAZA|KURŞUN|ADTK|AİTK|AITK'))) & ((df_merged['Çağrı Nedeni'] == 'Medikal')) & ~( (df_merged['Vaka Adresi'].str.contains('PSIKIYATR|PSİKİYAT|MADDE')) | (df_merged['İhbar Adresi'].str.contains('PSIKIYATR|PSİKİYAT|MADDE')) | (df_merged['Vaka Yeri Aciklama'].str.contains('PSIKIYATR|PSİKİYAT|MADDE')) | (~df_merged['KKM Açıklama'].str.contains('PSIKIYATR|PSİKİYAT|MADDE')))][['KKM Protokol', 'Ekip No', 'Tarih']]
    suspicious_medicals['Olası Hata']= "Şüpheli Medikal"

    #Missing Applications
    missing_applications= df_merged[(df_merged['Sonuç'] != 'Görev İptali') & (df_merged['Sonuç'] != 'Yaralı Yok') & (df_merged['Sonuç'] != 'Olay Yerinde Bekleme') & (df_merged['Sonuç'] != 'Asılsız İhbar') & (df_merged['Sonuç'] != 'Başka Araçla Nakil') & (df_merged['Sonuç'] != 'Diğer')& (df_merged['Sonuç'] != 'Ex - Yerinde Bırakıldı') & (df_merged['SPO2']=='-') ][['KKM Protokol', 'Ekip No', 'Tarih']]
    missing_applications['Olası Hata']= "Uygulama Eksiği"

    #Unmatching Conclusions
    conclusions= df_merged[((df_merged['Sonuç']== 'Nakil-Red') | (df_merged['Sonuç'] == '') | (df_merged['Sonuç Detay'] != '-') ) & ((df_merged['Nakledilen Hastane'] != '-' ) | (df_merged['Sevk Eden Hastane'] != '-' ) | (df_merged['Sevk Edilen Hastane'] != '-' ))][['KKM Protokol', 'Ekip No', 'Tarih']]
    conclusions['Olası Hata']= "Sonuç\Hastane Uyumu"

    #Unmatching Triage\Patient
    triages= df_merged[((df_merged['Triaj'] == 'Siyah Kod') & ~(df_merged["ICD10 TANI\nADI"].str.contains("ARREST|ÖLÜM"))) | ((df_merged['Triaj'] != 'Kırmızı Kod') & (df_merged['Triaj'] != 'Siyah Kod') & (df_merged["ICD10 TANI\nADI"].str.contains("ARREST|ÖLÜM")))][['KKM Protokol', 'Ekip No', 'Tarih']]
    triages['Olası Hata']= "Triaj"
    
    #Low Valued Cases
    price= int(input('>>> Düşük Tutarlı Vakaları Görmek İçin Sınır-Değer Fiyat Bilgisi Giriniz: '))
    print("---------------------------------------------------------------------------")
    low_valued_cases= df_merged[(df_merged['Sonuç'] != 'Görev İptali')& (df_merged['Toplam Tutar'] != 0) & (df_merged['Toplam Tutar'] < price) & (df_merged['Sonuç'] != 'Yaralı Yok') & (df_merged['Sonuç'] != 'Olay Yerinde Bekleme') & (df_merged['Sonuç'] != 'Asılsız İhbar') & (df_merged['Sonuç'] != 'Başka Araçla Nakil') & (df_merged['Çağrı Nedeni'] != 'Nakil') ][['KKM Protokol', 'Ekip No', 'Tarih']]
    low_valued_cases['Olası Hata']= "Fiyat Bilgisi"

    #KM Difference
    km_difference= df_merged[df_merged['KM Difference'] > 100][['KKM Protokol', 'Ekip No', 'Tarih']]
    km_difference['Olası Hata']= "Yüksek KM Farkı"


    wrong_inputs = pd.concat([wrong_inputs, syrian_insurances], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, withoutID_withInsurance], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, potential_tourists], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, ambulance_tracking_number], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, hospital_check], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, legally_sensitive], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, no_form], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, long_reactions], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, urban_rural], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, newborns], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, arrests], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, low_valued_cases], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, internal_transports], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, transported_by_others], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, suspicious_medicals], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, missing_applications], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, conclusions], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, triages], ignore_index=True)
    wrong_inputs = pd.concat([wrong_inputs, km_difference], ignore_index=True)

    wrong_inputs.rename(columns= {'Olası Hata' : 'Kontrol'}, inplace= True)
    wrong_inputs.to_excel("yanlis_kontrolu.xlsx")
    print(">>> Yanlış-Kontrol Dosyası Oluşturuldu!")
    print("---------------------------------------")


    #Creates a new column which calculates the intervals between ATN's for each team
    print(">>> Manuel ATN Kontrol Dosyası Oluşturuluyor...")
    print("----------------------------------------------")
    try:
      df_merged['ATN No'] = df_merged['ATN No'].astype(str)
      df_merged["ATN No"] = df_merged["ATN No"].str.upper()
      df_merged['HARFSIZ ATN'] = df_merged['ATN No'].str[1::]
      df_merged['HARFSIZ ATN'] = df_merged['HARFSIZ ATN'].fillna("00")
      df_merged = df_merged[pd.to_numeric(df_merged['HARFSIZ ATN'], errors='coerce').notnull()]
      df_merged['HARFSIZ ATN'] = df_merged['HARFSIZ ATN'].astype(int)
      df_merged = df_merged.sort_values(by = 'HARFSIZ ATN', ascending = True)
      df_merged['Vaka Veriliş Tarih\Saat'] = df_merged['Vaka Veriliş\nTarihi'] +' '+ df_merged['Vaka Veriliş\nSaati']

      numeric_atns = []

      for i in range(len(df_merged['HARFSIZ ATN'])):
        try:
          if df_merged.iloc[i]['Ekip No'] == df_merged.iloc[i+1]['Ekip No']:
            numeric_atns.append(abs(df_merged.iloc[i]['HARFSIZ ATN'] - df_merged.iloc[i+1]['HARFSIZ ATN']))
          elif df_merged.iloc[i]['Ekip No'] == df_merged.iloc[i-1]['Ekip No']:
            numeric_atns.append(abs(df_merged.iloc[i]['HARFSIZ ATN'] - df_merged.iloc[i-1]['HARFSIZ ATN']))
          else:
            numeric_atns.append('***')
        except:
          numeric_atns.append(0)

      df_merged['Fark'] = numeric_atns

      df_merged[['Ekip No', 'KKM Protokol', 'HARFSIZ ATN','Vaka Veriliş Tarih\Saat', 'Fark']].sort_values(by = ['HARFSIZ ATN', 'Vaka Veriliş Tarih\Saat'], ascending = True).to_excel('manuel_atn.xlsx')
      
      print(">>> Manuel ATN Kontrol Dosyası Oluşturuldu!")
      print("---------------------------------------------")
    except:
      print(">>> Manuel ATN Kontrol Dosyası Oluşturulamadı!")
      print("---------------------------------------------")
      pass

    return wrong_inputs

  def writer(name,surname):
    if name == 'Muhammed':
      if surname == 'Kaya':
        print("Powered by Muhammed KAYA - Welcome to Case Tracker")
        print("--------------------------------------------------")
        print(">>> İşlem Sürüyor, Lütfen Bekleyiniz...")
        print("---------------------------------------")
        return bring_case()
      else:
        return "Whoops!"
    else:
      return "Whoops!"

  return writer("Muhammed", "Kaya")
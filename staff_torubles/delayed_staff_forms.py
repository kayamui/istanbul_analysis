def delayed_forms():
    import pandas as pd
    import numpy as np

    import matplotlib.pyplot as plt
    import seaborn as sns

    import warnings

    import os

    import re


    path= str(input('Please add the path of the file: '))
    
    df_ocak_mayis= pd.read_excel(path)

    def remove_surucu(name_list):
        return [name for name in name_list if 'Sürücü' not in name]

    def join_guys(name_list):
        return ','.join(name_list)
    
    df_ocak_mayis['Ayrık']= df_ocak_mayis['Ekipteki Kişiler'].apply(lambda x: x.split(','))
    df_ocak_mayis['Sürücüsüz Personel İsimleri'] = df_ocak_mayis['Ayrık'].apply(remove_surucu)
    df_ocak_mayis.rename(columns= {"İstasyon İçin Vaka Kapatma Süresi  (Vaka Veriliş - İlk KKM'ye gönderim)": 'Vaka Kapatma Süresi'}, inplace= True)
    df_ocak_mayis['x_Vaka Kapatma Süresi']= df_ocak_mayis['Vaka Kapatma Süresi'].apply(lambda x: x.split('Gün')) # Limit splits to 1 to separate days and remaining time
    df_ocak_mayis['Gün'] = df_ocak_mayis['x_Vaka Kapatma Süresi'].apply(lambda x: x[0])
    df_ocak_mayis['x_Vaka Kapatma Süresi']= df_ocak_mayis['x_Vaka Kapatma Süresi'].apply(lambda x: x[1::])
    df_ocak_mayis['x_Vaka Kapatma Süresi']= df_ocak_mayis['x_Vaka Kapatma Süresi'].apply(lambda x: ','.join(x))
    df_ocak_mayis['x_Vaka Kapatma Süresi']= df_ocak_mayis['x_Vaka Kapatma Süresi'].apply(lambda x: x.split('Saat'))
    df_ocak_mayis['Saat']= df_ocak_mayis['x_Vaka Kapatma Süresi'].apply(lambda x: x[0])
    df_ocak_mayis.drop(columns= 'Ayrık',inplace=True)
    df_ocak_mayis.drop(columns=['x_Vaka Kapatma Süresi', 'Vaka Kapatma Süresi'], inplace= True)
    df_ocak_mayis.rename(columns= {'Sürücüsüz Personel İsimleri':'x_Ekipteki Kişiler'},inplace=True)
    df_ocak_mayis['Sürücüsüz Personel İsimleri']= df_ocak_mayis['x_Ekipteki Kişiler']
    df_ocak_mayis['Gün']= df_ocak_mayis['Gün'].astype(int)
    df_ocak_mayis['Saat']= df_ocak_mayis['Saat'].astype(int)
    df_ocak_mayis= df_ocak_mayis[df_ocak_mayis['Gün'] >= 3]
    df_ocak_mayis['x_Ekipteki Kişiler']= df_ocak_mayis['x_Ekipteki Kişiler'].apply(lambda x: ','.join(x.split('Yardımcı Sağlık Personeli')))
    df_ocak_mayis['x_Ekipteki Kişiler']= df_ocak_mayis['x_Ekipteki Kişiler'].apply(lambda x: ','.join(x.split('Ekip Sorumlusu')))
    df_ocak_mayis['x_Ekipteki Kişiler']= df_ocak_mayis['x_Ekipteki Kişiler'].apply(lambda x: ','.join(x.split('-')).split(','))
    df_ocak_mayis['x_Ekipteki Kişiler'] = df_ocak_mayis['x_Ekipteki Kişiler'].apply(lambda x: [name for name in x if re.search('[a-zA-Z]', name)])
    df_ocak_mayis.drop(columns= 'Sürücüsüz Personel İsimleri', inplace= True)
    df_ocak_mayis['length']= df_ocak_mayis['x_Ekipteki Kişiler'].apply(lambda x: len(x))
    df_ocak_mayis['Toplam Saat']= df_ocak_mayis['Gün'] * 24 + df_ocak_mayis['Saat']
    

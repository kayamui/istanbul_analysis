import pandas as pd
import numpy as np

path1= "c:/Users/mkaya/Downloads/İmza Atan Personel Raporu_20250717144338412.xls"
path2= "C:/Users/mkaya/Downloads/Nöbet Günü İmza Atmayan Personel Raporu_20250717144350912.xls"
class SignReport(object):
    
    def __init__(self, imza_atan, nobet_gunu_imza_atmayan):
        self.imza_atan= imza_atan
        self.nobet_gunu_imza_atmayan= nobet_gunu_imza_atmayan
        
        self.convert_columns()
        self.concat_data()
        
    def convert_columns(self):
        self.nobet_gunu_imza_atmayan.columns= ['İsim', 'Soyisim', 'T.C. No','Cep Telefonu', 'Unvan', 'Branş', 'İstihdam Şekli', 'Birim', 'İstasyon Adı', 'Nöbet Görevi','Başlama T.', 'Bitiş T.', 'Giriş T.', 'Çıkış T.']
    
    def concat_data(self):
        self.concat_df= pd.concat([self.imza_atan, self.nobet_gunu_imza_atmayan], axis=0)
        self.concat_df.reset_index(drop=True, inplace=True)
        
        return self.concat_df
    
    def __getattr__(self,name):
        
        if hasattr(self.concat_df, name):
            return getattr(self.concat_df,name)
        else:
            raise AttributeError(f"'DataFrame' object has no attribute '{name}'")
    
    def __getitem__(self, idx):
        return self.concat_df[idx]
    
    def head(self):
        return self.concat_df.head()
    
    def __len__(self):
        return len(self.concat_df)
    
    def shape(self):
        return self.concat_df.shape
    
    def to_excel(self, path):
        self.concat_df.to_excel(path, index=False)
    
def main():
    
    sign_report= SignReport(imza_atan, nobet_gunu_imza_atmayan)
    sign_report.to_excel('C:/Users/mkaya/Downloads/sign_report.xlsx')
    
    print(sign_report.shape())
if __name__ == '__main__':
    
    imza_atan= pd.read_excel(path1)
    nobet_gunu_imza_atmayan= pd.read_excel(path2)
    
    main()
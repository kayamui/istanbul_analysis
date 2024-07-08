from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)

# İstanbul'un tüm ilçeleri
istanbul_districts = [
    "ADALAR", "ARNAVUTKÖY", "ATAŞEHİR", "AVCILAR", "BAĞCILAR", "BAHÇELİEVLER", "BAKIRKÖY",
    "BAŞAKŞEHİR", "BAYRAMPAŞA", "BEŞİKTAŞ", "BEYKOZ", "BEYLİKDÜZÜ", "BEYOĞLU",
    "BÜYÜKÇEKMECE", "ÇATALCA", "ÇEKMEKÖY", "ESENLER", "ESENYURT", "EYÜPSULTAN",
    "FATİH", "GAZİOSMANPAŞA", "GÜNGÖREN", "KADIKÖY", "KAĞITHANE", "KARTAL", "KÜÇÜKÇEKMECE",
    "MALTEPE", "PENDİK", "SANCAKTEPE", "SARIYER", "SİLİVRİ", "SULTANBEYLİ", "SULTANGAZİ",
    "ŞİLE", "ŞİŞLİ", "TUZLA", "ÜMRANİYE", "ÜSKÜDAR", "ZEYTİNBURNU"
]

# Büyük harfe çevirme işlemini Türkçe karakterler için doğru şekilde yapan fonksiyon
def to_upper_turkish(text):
    replacements = {
        "i": "İ", "ş": "Ş", "ğ": "Ğ", "ü": "Ü", "ö": "Ö", "ç": "Ç", "ı": "I"
    }
    return text.translate(str.maketrans(replacements)).upper()

# İstanbul ilçelerini büyük harfe çevir
istanbul_districts_upper = [to_upper_turkish(district) for district in istanbul_districts]

# İlçe düzeltme fonksiyonu
def correct_district_name(district):
    corrections = {
        "UMRANIYE": "ÜMRANİYE",
        "UMRANİYE": "ÜMRANİYE",
        "ÜMRANIYE": "ÜMRANİYE",
        "PENDIK": "PENDİK",
        "ATAŞEHIR": "ATAŞEHİR",
        "ŞILE": "ŞİLE",
        "SULTANBEYLI": "SULTANBEYLİ"
    }
    return corrections.get(district, district)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        sheet_name = request.form['sheet_name']
        address_column_name = request.form['address_column']
        output_file_name = request.form['output_file']

        if file and sheet_name and address_column_name and output_file_name:
            df = pd.read_excel(file, sheet_name=sheet_name)
            
            # 'İhbar Adresi' sütununu bulun
            address_column = None
            for col in df.columns:
                if address_column_name in col:
                    address_column = col
                    break

            if address_column is None:
                return "Kolon adı bulunamadı", 400

            # 'İhbar İlçesi' sütununu oluşturun
            df.insert(df.columns.get_loc(address_column) + 1, 'İhbar İlçesi', "")

            # İlçe isimlerini kontrol edin
            for index, row in df.iterrows():
                found_district = False
                address = to_upper_turkish(str(row[address_column]))  # Adresi büyük harfe çevir
                # Adresi newline ve çeşitli boşluk karakterlerine göre böl
                lines = address.split('\n')
                for line in lines:
                    words = line.split()
                    for i in range(len(words)):
                        if "İSTANBUL" in words[i]:
                            # İSTANBUL kelimesinden önceki tüm kelimeleri ters sırayla kontrol et
                            for j in range(i-1, -1, -1):
                                previous_word = words[j].replace(",", "").replace(".", "")
                                corrected_word = correct_district_name(previous_word)
                                if corrected_word in istanbul_districts_upper:
                                    df.at[index, 'İhbar İlçesi'] = corrected_word
                                    found_district = True
                                    break
                            if found_district:
                                break
                    if found_district:
                        break
                if not found_district:
                    df.at[index, 'İhbar İlçesi'] = "BULUNAMADI"

            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            writer.save()
            output.seek(0)

            return send_file(output, attachment_filename=output_file_name, as_attachment=True)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
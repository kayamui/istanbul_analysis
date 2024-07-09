from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
from io import BytesIO
import logging
from api.common.response import http_response_object

app = Flask(__name__)

# Logging ayarları
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# İstanbul'un tüm ilçeleri ve mahalleleri (büyük harfe dönüştürülmüş)
ISTANBUL_DISTRICTS = [
    "ADALAR", "ARNAVUTKÖY", "ATAŞEHİR", "AVCILAR", "BAĞCILAR", "BAHÇELİEVLER", "BAKIRKÖY",
    "BAŞAKŞEHİR", "BAYRAMPAŞA", "BEŞİKTAŞ", "BEYKOZ", "BEYLİKDÜZÜ", "BEYOĞLU",
    "BÜYÜKÇEKMECE", "ÇATALCA", "ÇEKMEKÖY", "ESENLER", "ESENYURT", "EYÜPSULTAN",
    "FATİH", "GAZİOSMANPAŞA", "GÜNGÖREN", "KADIKÖY", "KAĞITHANE", "KARTAL", "KÜÇÜKÇEKMECE",
    "MALTEPE", "PENDİK", "SANCAKTEPE", "SARIYER", "SİLİVRİ", "SULTANBEYLİ", "SULTANGAZİ",
    "ŞİLE", "ŞİŞLİ", "TUZLA", "ÜMRANİYE", "ÜSKÜDAR", "ZEYTİNBURNU"
]

ISTANBUL_MAHALLELERI = [
    "yeni sahra", "güzeltepe", "kavacık", "anadolu feneri", "yakacıkyeni", "burhaniye",
    "sofular", "azizmahmuthüdayi", "taşdelen", "kandilli", "polonezköy", "erenköy",
    "hürriyet", "erenler", "gülbahar", "gülsuyu", "satmazlı", "yenidoğan",
    "mehmet akif ersoy", "zühtüpaşa", "yunusemre", "ağaçdere", "öğümce", "fatihsultanmehmet",
    "uğurmumcu", "alemdağ", "sahrayıcedit", "hacı kasım", "orhantepe", "küplüce", "turgutreis",
    "esenşehir", "feyzullah", "kordonboyu", "veyselkarani", "baklacı", "gümüşpınar", "esenkent",
    "uğur mumcu", "yakacıkçarşı", "esenler", "sapan bağları", "evliya çelebi", "hilal", "muratreis",
    "görele", "zeynepkamil", "çift mahalle bilgisi", "akfırat", "içmeler", "soğanlık", "kızılca",
    "kurna", "nizam", "altıntepe", "mehmetakif", "eyüpsultan", "şerifali", "ulupelit", "yeniçamlıca",
    "murat reis", "zeynep kamil", "merdivenköy", "paşabahçe", "emirli", "namıkkemal", "acarlar",
    "fındıklı", "kısıklı", "eğitim", "soğullu", "tepeören", "mimarsinan", "dudullu osb", "üvezli",
    "hacıkasım", "hacıllı", "i̇saköy", "anadolu kavağı", "cami", "sahrayı cedit", "ünalan",
    "harmandere", "bostancı", "girne", "ahmediye", "yalı", "aziz mahmut hüdayi", "selamiali",
    "yayla", "şeyhli", "anadolu", "bozhane", "huzur", "19 mayıs", "yakacık yeni", "esatpaşa",
    "örnekköy", "kuzguncuk", "baltalimanı", "veysel karani", "osmangazi", "rasimpaşa", "kervansaray",
    "salacak", "bıçkıdere", "çengeldere", "göksu", "soğuksu", "yukarı", "göçe", "i̇shaklı",
    "ertuğrul gazi", "yavuzselim", "barbaros", "bozgoca", "karabeyli", "armağanevler", "ortaçeşme",
    "anadolukavağı", "petroli̇ş", "çavuşoğlu", "kurtköy", "çamlıbahçe", "küçük çamlıca", "yeniköy",
        "postane", "batı", "dudulluosb", "cemilmeriç", "ahmetyesevi", "kirazlıtepe", "çelebi", "namık kemal",
    "soğukpınar", "aydınevler", "paşamandıra", "mehmetakifersoy", "sultantepe", "doğancılı",
    "gökmaşlı", "doğu", "eyüp sultan", "kirazlıdere", "yunus", "caferağa", "göztepe", "ferhatpaşa",
    "atalar", "fevzi çakmak", "çamçeşme", "i̇stasyon", "güllübağlar", "suadiye", "i̇cadiye",
    "sülüntepe", "yalıköy", "güzelyalı", "fatih", "adem yavuz", "merkez", "alibahadır", "tatlısu",
    "acıbadem", "şifa", "aydıntepe", "mahmut şevket paşa", "soğanlık yeni", "site", "sırapınar",
    "hüseyinli", "mimar sinan", "çengelköy", "esenevler", "finanskent", "koşuyolu", "mescit",
    "valide-iatik", "cevizli", "orhangazi", "avcıkoru", "i̇stiklal", "başıbüyük", "küçükçamlıca",
    "sapanbağları", "maslak", "mustafakemal", "ertuğrulgazi", "ballıca", "kemal türkler",
    "anadoluhisarı", "ferah", "güllü bağlar", "yenimahalle", "cemil meriç", "dumlupınar", "topağacı",
    "feneryolu", "kurfallı", "aşağıdudullu", "esenceli", "şuayipli", "abdurrahmangazi", "kemaltürkler",
    "aşık veysel", "oruçoğlu", "alacalı", "yeşilvadi", "hasanpaşa", "yeni", "çiğdem", "orta",
    "ağva", "karacaköy", "mahmutşevketpaşa", "yeni mahalle", "saray", "mevlana", "yenisahra",
    "yakacık çarşı", "aşağı dudullu", "akçakese", "emek", "kavakpınar", "göllü", "sultançiftliği",
    "ramazanoğlu", "valide-i atik", "yavuztürk", "tepeüstü", "çiftlik", "gümüşsuyu",
    "büyükbakkalköy", "fatih sultan mehmet", "aşıkveysel", "i̇mrenli", "çayırbaşı", "çubuklu",
    "safa", "kozyatağı", "akpınar", "mustafa kemal", "osmanköy", "i̇dealtepe", "reşadiye",
    "kalem", "i̇ncirköy", "kabakoz", "kazımkarabekir", "karlıktepe", "bahçelievler", "kılıçlı",
    "esenyalı", "teke", "küçükbakkalköy", "sortullu", "küçükyalı", "çataklı", "burgazada",
    "orhanlı", "poyrazköy", "dudullu", "bağlarbaşı", "fetih", "içerenköy", "adil", "çavuş",
    "geredeli", "çamlık", "altunizade", "necip fazıl", "deriosb", "çatalmeşe", "osmanağa",
    "necipfazıl", "yaka", "hekimbaşı", "ekşioğlu", "atatürk", "altayçeşme", "belirtilmemiş",
    "velibaba", "kumbaba", "ahmet yesevi", "19mayıs", "cumhuriyet", "petroliş", "i̇nönü",
    "petrol i̇ş", "selami ali", "fevziçakmak", "aydınlı", "heybeliada", "gülensu", "ovacık",
    "i̇nkılap", "zümrütevler", "battalgazi", "sanayi", "göçbeyli", "çınardere", "kadıköy",
    "akbaba", "kuleli", "selimiye", "çengilli", "kaynarca", "yamanevler", "kınalıada",
    "çakmak", "rüzgarlıbahçe", "turgut reis", "yavuz selim", "örnek", "mehmet akif", "altınşehir",
    "meclis", "kömürlük", "atakent", "yunus emre", "kayışdağı", "madenler", "akşemsettin",
    "küçüksu", "ihlamurkuyu", "beylerbeyi", "değirmençayırı", "bulgurlu", "tokatköy",
    "yenişehir", "sahilköy", "bucaklı", "anadolufeneri", "fenerbahçe", "hamidiye",
    "deri osb", "dereseki", "zerzavatçı", "aydınlar", "maden", "ademyavuz", "kanlıca",
    "parseller", "tantavi", "sarıgazi", "ahmetli", "yazımanayır", "nişantepe", "anadolu hisarı",
    "i̇mrendere", "garipçe", "ömerli", "paşaköy", "elmalı", "balibey", "mecidiye", "kurtdoğmuş",
    "koçullu", "caddebostan", "riva", "karamandere", "hasanlı", "esentepe", "merve",
    "yukarı dudullu", "elmalıkent", "petrol iş", "çiftmahallebilgisi", "yeni çamlıca",
    "kazım karabekir", "yeşilbağlar", "yukarıdudullu", "güngören", "karakiraz", "çınar",
    "meşrutiyet", "korucu", "soğanlıkyeni", "yayalar", "darlık", "evliyaçelebi", "topselvi",
    "fikirtepe"
]

class AddressProcessor:
    def __init__(self, districts, neighborhoods):
        self.districts = [self.to_upper_turkish(district) for district in districts]
        self.neighborhoods = [self.to_upper_turkish(neighborhood) for neighborhood in neighborhoods]

    @staticmethod
    def to_upper_turkish(text):
        replacements = {
            "i": "İ", "ş": "Ş", "ğ": "Ğ", "ü": "Ü", "ö": "Ö", "ç": "Ç", "ı": "I"
        }
        return text.translate(str.maketrans(replacements)).upper()

    def correct_district_name(self, district):
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

    def find_district(self, address):
        address_upper = self.to_upper_turkish(address)
        for district in self.districts:
            if district in address_upper:
                return self.correct_district_name(district)
        return "BULUNAMADI"

    def find_neighborhood(self, address):
        address_upper = self.to_upper_turkish(address)
        for neighborhood in self.neighborhoods:
            if neighborhood in address_upper:
                return neighborhood
        return "BULUNAMADI"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        sheet_name = request.form['sheet_name']
        address_column_name = request.form['address_column']
        output_file_name = request.form['output_file']
        action = request.form['action']
        ilce = request.form.get('ilce')
        mahalle = request.form.get('mahalle')

        if not output_file_name.endswith('.xlsx'):
            output_file_name += '.xlsx'

        if file and sheet_name and address_column_name and output_file_name:
            df = pd.read_excel(file, sheet_name=sheet_name)
            address_column_index = df.columns.get_loc(address_column_name)

            processor = AddressProcessor(ISTANBUL_DISTRICTS, ISTANBUL_MAHALLELERI)

            if action == 'ilce_mahalle_bulucu':
                if ilce and mahalle:
                    df.insert(address_column_index + 1, 'İhbar İlçesi', df[address_column_name].apply(processor.find_district))
                    df.insert(address_column_index + 2, 'İhbar Mahallesi', df[address_column_name].apply(processor.find_neighborhood))
                elif ilce:
                    df.insert(address_column_index + 1, 'İhbar İlçesi', df[address_column_name].apply(processor.find_district))
                elif mahalle:
                    df.insert(address_column_index + 1, 'İhbar Mahallesi', df[address_column_name].apply(processor.find_neighborhood))

            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            writer.close()
            output.seek(0)

            logging.info(f'File processed successfully: {output_file_name}')
            return send_file(output, download_name=output_file_name, as_attachment=True)

        return http_response_object(success=False, message="Missing required fields", data={}, code=400)
    except Exception as e:
        logging.error(f'Error in upload_file: {e}')
        return http_response_object(success=False, message=str(e), data={}, code=500)

if __name__ == '__main__':
    app.run(debug=True)
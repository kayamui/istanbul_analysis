def find_district():
  
  """
  Based on the addresses have been taken, this function creates two columns to write the founded districts and neighbourhoods
  
  """

  import pandas as pd
  import numpy as np
  import warnings
  warnings.filterwarnings('ignore')

  import os

  # import Excel File and select the dataframe
  file_path= str(input('Lütfen Dosya Uzantısını Ekleyiniz: '))
  excel_file= pd.ExcelFile(file_path)

  dataframes= {sheet_name: excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}
  print(list(dataframes.keys()))
  sheet_path = str(input(f'Lütfen İşlem Yapmak İstediğiniz Sayfa Adını Yapıştırınız: '))
  df= dataframes[sheet_path]

  # Created a temporary file to not harm the original dataframe
  df_temp= df


  # Make columns uppercase and remove the blanks
  df_temp.columns = [col.strip().upper() for col in df_temp.columns]

  # Select the address column
  column_path= str(input('Lütfen İhbar Adreslerinin Bulunduğu Kolon Adını Yazınız: '))
  column_path= column_path.replace('-','').replace('Ç', 'C').replace('Ğ', 'G').replace('İ', 'I').replace('Ö', 'O').replace('Ş', 'S').replace('Ü', 'U').strip().upper()
  
  # New columns without any unnecessarities
  columns_list= []
  for i in df_temp.columns:
    i= i.replace('-',' ').replace('Ç', 'C').replace('Ğ', 'G').replace('İ', 'I').replace('Ö', 'O').replace('Ş', 'S').replace('Ü', 'U').strip()
    columns_list.append(i)

  df_temp.columns= columns_list #####################################

  df_temp[column_path]= df_temp[column_path].fillna('BELİRTİLMEMİŞ')
  column_data= [i for i in df_temp[column_path]]

  df_temp[column_path].fillna('BELİRTİLMEMİŞ', inplace= True)

  # Because of column_path written by user, an extra work has been done on it
  df_temp[column_path]= df_temp[column_path].str.upper().str.replace('-', ' ').str.replace('Ç', 'C').str.replace('Ğ', 'G').str.replace('İ', 'I').str.replace('Ö', 'O').str.replace('Ş', 'S').str.replace('Ü', 'U').str.strip()

  df_temp[column_path]= df_temp[column_path].str.strip().str.upper()

  # Dictionary keys of districts and neighbours for each side of Istanbul
  neighbourhoods= {'ARNAVUTKOY': {'DELIKLIKAYA', 'CILINGIR', 'TAYAKADIN', 'HADIMKOY', 'HICRET', 'OMERLI', 'TERKOS', 'KARABURUN', 'YENIKOY', 'BAKLALI', 'YESILBAYIR', 'DURUSU', 'BALABAN', 'BOYALIK', 'MARESAL FEVZI CAKMAK', 'HASTANE', 'ANADOLU', 'IMRAHOR', 'YAVUZ SELIM', 'KARLIBAYIR', 'HARACCI', 'FATIH', 'ARNAVUTKOY MERKEZ', 'YUNUS EMRE', 'BOLLUCA', 'MAVIGOL', 'BOGAZKOY ISTIKLAL', 'HACIMASLI', 'MEHMET AKIF ERSOY', 'MUSTAFA KEMAL PASA', 'ATATURK', 'YASSIOREN', 'TASOLUK', 'DURSUNKOY', 'ISLAMBEY', 'ADNAN MENDERES', 'SAZLIBOSNA', 'NENEHATUN'}, 'AVCILAR': {'UNIVERSITE', 'CIHANGIR', 'MERKEZ', 'DENIZKOSKLER', 'AMBARLI', 'FIRUZKOY', 'TAHTAKALE', 'YESILKENT', 'MUSTAFA KEMAL PASA', 'GUMUSPALA'}, 'BAGCILAR': {'GUNESLI', 'DEMIRKAPI', 'YENIMAHALLE', 'YENIGUN', 'BAGLAR', 'KIRAZLI', '15 TEMMUZ', 'HURRIYET', 'YILDIZTEPE', 'FATIH', 'CINAR', '100. YIL', 'SANCAKTEPE', 'INONU', 'GOZTEPE', 'KEMALPASA', 'MERKEZ', 'FEVZI CAKMAK', 'KAZIM KARABEKIR', 'MAHMUTBEY', 'BARBAROS', 'YAVUZ SELIM'}, 'BAHCELIEVLER': {'SIRINEVLER', 'FEVZI CAKMAK', 'CUMHURIYET', 'HURRIYET', 'SOGANLI', 'BAHCELIEVLER', 'SIYAVUSPASA', 'KOCASINAN', 'COBANCESME', 'YENIBOSNA', 'ZAFER'}, 'BAKIRKOY': {'SAKIZAGACI', 'ATAKOY 1. KISIM', 'ZEYTINLIK', 'SENLIKKOY', 'KARTALTEPE', 'YENIMAHALLE', 'ATAKOY 7 8 9 10. KISIM', 'ATAKOY 3 4 11. KISIM', 'YESILYURT', 'ATAKOY 2 5 6. KISIM', 'CEVIZLIK', 'ZUHURATBABA', 'YESILKOY', 'OSMANIYE', 'BASINKOY'}, 'ZEYTINBURNU': {'YESILTEPE', 'MALTEPE', 'TELSIZ', 'GOKALP', 'BESTELSIZ', 'CIRPICI', 'SEYITNIZAM', 'MERKEZEFENDI', 'VELIEFENDI', 'SUMER', 'YENIDOGAN', 'NURIPASA', 'KAZLICESME'}, 'BASAKSEHIR': {'ZIYA GOKALP', 'BASAK', 'KAYABASI', 'ALTINSEHIR', 'SAMLAR', 'GUVERCINTEPE', 'BAHCESEHIR 1. KISIM', 'BAHCESEHIR 2. KISIM', 'SAHINTEPE', 'BASAKSEHIR'}, 'BAYRAMPASA': {'ISMET PASA', 'KARTALTEPE', 'CEVATPASA', 'YILDIRIM', 'MURATPASA', 'KOCATEPE', 'TERAZIDERE', 'ALTINTEPSI', 'YENIDOGAN', 'ORTA', 'VATAN'}, 'BESIKTAS': {'LEVAZIM', 'ULUS', 'VISNEZADE', 'NISBETIYE', 'BALMUMCU', 'YILDIZ', 'KONAKLAR', 'AKAT', 'MECIDIYE', 'ARNAVUTKOY', 'ABBASAGA', 'SINANPASA', 'GAYRETTEPE', 'CIHANNUMA', 'ETILER', 'BEBEK', 'LEVENT', 'KULTUR', 'DIKILITAS', 'KURUCESME', 'TURKALI', 'MURADIYE', 'ORTAKOY'}, 'BEYLIKDUZU': {'GURPINAR', 'KAVAKLI', 'CUMHURIYET', 'YAKUPLU', 'SAHIL', 'MARMARA', 'ADNAN KAHVECI', 'BUYUKSEHIR', 'DEREAGZI', 'BARIS'}, 'BEYOGLU': {'CATMA MESCIT', 'GUMUSSUYU', 'OMER AVNI', 'KALYONCU KULLUGU', 'KUCUK PIYALE', 'HACIMIMI', 'ISTIKLAL', 'PIYALEPASA', 'EMEKYEMEZ', 'KATIP MUSTAFA CELEBI', 'FETIHTEPE', 'EVLIYA CELEBI', 'CAMIIKEBIR', 'SUTLUCE', 'BOSTAN', 'YENISEHIR', 'PIRI PASA', 'HUSEYINAGA', 'ARAP CAMI', 'KECECI PIRI', 'HALICIOGLU', 'SEHIT MUHTAR', 'KAMER HATUN', 'PURTELAS', 'ORNEKTEPE', 'KAPTANPASA', 'KULOGLU', 'CIHANGIR', 'ASMALI MESCIT', 'YAHYA KAHYA', 'BEREKETZADE', 'CUKUR', 'KILICALI PASA', 'TOMTOM', 'BULBUL', 'SURURI', 'FIRUZAGA', 'KADIMEHMET EFENDI', 'BEDRETTIN', 'KULAKSIZ', 'HACIAHMET', 'KEMANKES KARAMUSTAFA PASA', 'MUEYYETZADE', 'KOCATEPE', 'SAHKULU'}, 'BUYUKCEKMECE': {'ULUS', 'MIMAR SINAN MERKEZ', 'EKINOBA', '19 MAYIS', 'KARAAGAC', 'PINARTEPE', 'MURAT CESME', 'MIMAROBA', 'KAMILOBA', 'CAKMAKLI', 'ALKENT', 'YENIMAHALLE', 'TURKOBA', 'AHMEDIYE', 'GUZELCE', 'HURRIYET', 'DIZDARIYE', 'CELALIYE', 'FATIH', 'ATATURK', 'SINANOBA', 'CUMHURIYET', 'BAHCELIEVLER', 'KUMBURGAZ'}, 'CATALCA': {'IZZETTIN', 'BASAK', 'ORENCIK', 'OKLALI', 'SUBASI', 'FERHATPASA', 'KARAMANDERE', 'YAYLACIK', 'CAKIL', 'INCEGIZ', 'ELBASAN', 'CIFTLIKKOY', 'GUMUSPINAR', 'NAKKAS', 'CELEPKOY', 'KARACAKOY', 'KALEICI', 'AYDINLAR', 'KALFA', 'IHSANIYE', 'ORCUNLU', 'OVAYENICE', 'FATIH', 'CANAKCA', 'KABAKCA', 'AKALAN', 'ATATURK', 'HISARBEYLI', 'HALLACLI', 'ORMANLI', 'KESTANELIK', 'YALIKOY', 'MURATBEY MERKEZ', 'DAGYENICE', 'GOKCEALI', 'BAHSAYIS'}, 'ESENLER': {'KEMER', 'NINE HATUN', 'DAVUTPASA', 'CIFTE HAVUZLAR', 'FEVZI CAKMAK', 'MENDERES', '15 TEMMUZ', 'ORUCREIS', 'KAZIM KARABEKIR', 'FATIH', 'TURGUT REIS', 'BIRLIK', 'HAVAALANI', 'MIMAR SINAN', 'NAMIK KEMAL', 'YAVUZ SELIM', 'TUNA'}, 'ESENYURT': {'ASIK VEYSEL', 'AKSEMSEDDIN', 'SULEYMANIYE', 'ESENKENT', 'YENIKENT', 'SULTANIYE', 'INCIRTEPE', 'ISTIKLAL', 'YESILKENT', 'ZAFER', 'GUZELYURT', 'KOZA', 'MEVLANA', 'SAADETDERE', 'OSMANGAZI', 'SELAHADDIN EYYUBI', 'GOKEVLER', 'SEHITLER', 'PINAR', 'NECIP FAZIL KISAKUREK', 'ORNEK', 'ARDICLI', 'BALIKYOLU', 'TURGUT OZAL', 'HURRIYET', 'AKEVLER', 'FATIH', 'CINAR', 'YUNUS EMRE', 'PIRI REIS', 'MEHTERCESME', 'INONU', 'BARBAROS HAYRETTIN PASA', 'BATTALGAZI', 'MEHMET AKIF ERSOY', 'NAMIK KEMAL', 'ATATURK', 'TALATPASA', 'UCEVLER', 'CUMHURIYET', 'BAGLARCESME', 'ORHAN GAZI', 'AKCABURGAZ'}, 'EYUPSULTAN': {'CIFTALAN', 'NISANCI', 'MITHATPASA', 'AGACLI', 'DUGMECILER', 'RAMI YENI', 'ESENTEPE', 'CIRCIR', 'PIRINCCI', 'IHSANIYE', 'ODAYERI', 'ALIBEYKOY', 'TOPCULAR', 'YESILPINAR', 'EMNIYETTEPE', 'GUZELTEPE', 'AKPINAR', 'SILAHTARAGA', 'DEFTERDAR', 'MERKEZ', 'AKSEMSETTIN', 'ISLAMBEY', 'GOKTURK MERKEZ', 'RAMI CUMA', 'ISIKLAR', 'MIMAR SINAN', 'SAKARYA', '5. LEVENT', 'KARADOLAP'}, 'FATIH': {'KATIP KASIM', 'ATIKALI', 'SEYYID OMER', 'SEHREMINI', 'SULEYMANIYE', 'KUCUK AYASOFYA', 'ZEYREK', 'AYVANSARAY', 'MIMAR KEMALETTIN', 'HASEKI SULTAN', 'MOLLA FENARI', 'CIBALI', 'HIRKA I SERIF', 'KARAGUMRUK', 'TOPKAPI', 'TAHTAKALE', 'ALEMDAR', 'BALABANAGA', 'BEYAZIT', 'MOLLA HUSREV', 'RUSTEM PASA', 'MESIHPASA', 'MUHSINE HATUN', 'KALENDERHANE', 'MIMAR HAYRETTIN', 'CERRAHPASA', 'CANKURTARAN', 'HOBYAR', 'DEMIRTAS', 'HOCA GIYASETTIN', 'YAVUZ SULTAN SELIM', 'NISANCA', 'SILIVRIKAPI', 'BINBIRDIREK', 'ISKENDERPASA', 'MEVLANAKAPI', 'HOCA PASA', 'SARIDEMIR', 'YEDIKULE', 'SURURI', 'KOCA MUSTAFAPASA', 'MOLLA GURANI', 'AKSEMSETTIN', 'BALAT', 'KEMAL PASA', 'MERCAN', 'AKSARAY', 'ALI KUSCU', 'DERVIS ALI', 'SULTAN AHMET', 'SUMBUL EFENDI'}, 'GAZIOSMANPASA': {'KARLITEPE', 'MEVLANA', 'FEVZI CAKMAK', 'MERKEZ', 'YENI MAHALLE', 'HURRIYET', 'SARIGOL', 'YENIDOGAN', 'YILDIZTABYA', 'BARBAROS HAYRETTINPASA', 'KAZIM KARABEKIR', 'KARADENIZ', 'BAGLARBASI', 'SEMSIPASA', 'KARAYOLLARI', 'PAZARICI'}, 'GUNGOREN': {'AKINCILAR', 'MARESAL CAKMAK', 'MERKEZ', 'SANAYI', 'TOZKOPARAN', 'MEHMET NESIH OZMEN', 'HAZNEDAR', 'GUVEN', 'GUNESTEPE', 'ABDURRAHMAN NAFIZ GURMAN', 'GENCOSMAN'}, 'KAGITHANE': {'SULTAN SELIM', 'TELSIZLER', 'GURSEL', 'SEYRANTEPE', 'EMNIYET', 'GULTEPE', 'ORTABAYIR', 'SIRINTEPE', 'HURRIYET', 'CAGLAYAN', 'MEHMET AKIF ERSOY', 'TALATPASA', 'YESILCE', 'MERKEZ', 'HAMIDIYE', 'CELIKTEPE', 'YAHYA KEMAL', 'HARMANTEPE', 'NURTEPE'}, 'KUCUKCEKMECE': {'ATAKENT', 'TEVFIK BEY', 'KARTALTEPE', 'HALKALI', 'BESYOL', 'YARIMBURGAZ', 'MEHMET AKIF', 'ISTASYON', 'SOGUTLU CESME', 'GULTEPE', 'KANARYA', 'YENI MAHALLE', 'FATIH', 'SULTAN MURAT', 'YESILOVA', 'INONU', 'ATATURK', 'KEMALPASA', 'FEVZI CAKMAK', 'CUMHURIYET', 'CENNET'}, 'SARIYER': {'SARIYER MERKEZ', 'GUMUSDERE', 'POLIGON', 'FATIH SULTAN MEHMET', 'KIRECBURNU', 'AYAZAGA', 'TARABYA', 'RESITPASA', 'BAHCEKOY YENI', 'MADEN', 'YENI', 'YENIKOY', 'FERAHEVLER', 'KUMKOY', 'CAMLITEPE', 'USKUMRUKOY', 'MASLAK', 'PINAR', 'DEMIRCI', 'RUMELIFENERI', 'ZEKERIYAKOY', 'BAHCEKOY KEMER', 'BUYUKDERE', 'ISTINYE', 'KISIRKAYA', 'KOCATAS', 'EMIRGAN', 'CAYIRBASI', 'GARIPCE', 'BAHCEKOY MERKEZ', 'DARUSSAFAKA', 'CUMHURIYET', 'BALTALIMANI', 'RUMELI KAVAGI', 'KAZIM KARABEKIR', 'HUZUR', 'RUMELI HISARI', 'PTT EVLERI'}, 'SILIVRI': {'GAZITEPE', 'GUMUSYAKA', 'BUYUK KILICLI', 'FENER', 'KURFALLI', 'AKOREN', 'YENI', 'KAVAKLI ISTIKLAL', 'SELIMPASA', 'ALIBEY', 'PIRI MEHMET PASA', 'CELTIK', 'BALABAN', 'KUCUK SINEKLI', 'SEYMEN', 'CAYIRDERE', 'KAVAKLI HURRIYET', 'SAYALAR', 'FATIH', 'DEGIRMENKOY ISMETPASA', 'DANAMANDIRA', 'KADIKOY', 'YOLCATI', 'CUMHURIYET', 'SEMIZKUMLAR', 'ALIPASA', 'CANTA SANCAKTEPE', 'ORTAKOY', 'BUYUK CAVUSLU', 'MIMAR SINAN', 'BUYUK SINEKLI', 'DEGIRMENKOY FEVZIPASA', 'BEYCILER'}, 'SULTANGAZI': {'HABIBLER', 'UGUR MUMCU', 'CUMHURIYET', '50. YIL', 'YAYLA', 'ISMETPASA', 'CEBECI', 'GAZI', 'SULTANCIFTLIGI', 'MALKOCOGLU', 'ESENTEPE', '75. YIL'}, 'SISLI': {'TESVIKIYE', '19 MAYIS', 'HALIL RIFAT PASA', 'ESKISEHIR', 'PASA', 'MECIDIYEKOY', 'GULBAHAR', 'KUSTEPE', 'FULYA', 'MAHMUT SEVKET PASA', 'ESENTEPE', 'ERGENEKON', 'HARBIYE', 'HALIDE EDIP ADIVAR', 'INONU', 'HALASKARGAZI', 'DUATEPE', 'FERIKOY', 'MERKEZ', 'CUMHURIYET', 'MESRUTIYET', 'YAYLA', 'BOZKURT'}, 'UNKNOWN':{'UNKNOWN'}, 'BELİRTİLMEMİŞ':{'BELİRTİLMEMİŞ'},'UMRANIYE': {'ATAKENT', 'ASAGI DUDULLU', 'TATLISU', 'ESENKENT', 'ESENSEHIR', 'FATIH SULTAN MEHMET', 'CAKMAK', 'ISTIKLAL', 'INKILAP', 'DUDULLU', 'MEHMET AKIF', 'HEKIMBASI', 'YUKARI DUDULLU', 'TOPAGACI', 'ESENEVLER', 'FINANSKENT', 'SITE', 'SERIFALI', 'DUMLUPINAR', 'CEMIL MERIC', 'TEPEUSTU', 'YAMANEVLER', 'MADENLER', 'DUDULLU OSB', 'ALTINSEHIR', 'SARAY', 'NECIP FAZIL', 'NAMIK KEMAL', 'ASAGIDUDULLU', 'ATATURK', 'PARSELLER', 'CIFT MAHALLE BILGISI', 'TANTAVI', 'IHLAMURKUYU', 'ADEM YAVUZ', 'KAZIM KARABEKIR', 'CAMLIK', 'ARMAGANEVLER', 'ELMALIKENT', 'YUKARIDUDULLU', 'HUZUR'}, 'KARTAL': {'KORDONBOYU', 'ORHANTEPE', 'SOGANLIK YENI', 'ORTA', 'ATALAR', 'YUKARI', 'GUMUSPINAR', 'ESENTEPE', 'PETROL IS', 'HURRIYET', 'YALI', 'CEVIZLI', 'CAVUSOGLU', 'UGUR MUMCU', 'YAKACIK YENI', 'YAKACIK CARSI', 'CUMHURIYET', 'KARLIKTEPE', 'TOPSELVI', 'SOGANLIK', 'YUNUS'}, 'CEKMEKOY': {'ALEMDAG', 'SULTANCIFTLIGI', 'SOGUKPINAR', 'MEHMET AKIF', 'BELIRTILMEMIS', 'OMERLI', 'NISANTEPE', 'TASDELEN', 'RESADIYE', 'AYDINLAR', 'HUSEYINLI', 'GUNGOREN', 'KIRAZLIDERE', 'SIRAPINAR', 'CATALMESE', 'MERKEZ', 'HAMIDIYE', 'CUMHURIYET', 'CAMLIK', 'MIMAR SINAN', 'EKSIOGLU', 'KOCULLU'}, 'SANCAKTEPE': {'VEYSEL KARANI', 'SAFA', 'SARIGAZI', 'PASAKOY', 'BELIRTILMEMIS', 'MEVLANA', 'OSMANGAZI', 'MERVE', 'KEMAL TURKLER', 'EYUP SULTAN', 'MECLIS', 'FATIH', 'YUNUS EMRE', 'INONU', 'ATATURK', 'EMEK', 'AKPINAR', 'ABDURRAHMANGAZI', 'HILAL', 'YENIDOGAN'}, 'KADIKOY': {'KOZYATAGI', '19 MAYIS', 'RASIMPASA', 'FENERYOLU', 'MERDIVENKOY', 'CADDEBOSTAN', 'CAFERAGA', 'BELIRTILMEMIS', 'BOSTANCI', 'ZUHTUPASA', 'DUMLUPINAR', 'KOSUYOLU', 'ERENKOY', 'FIKIRTEPE', 'SUADIYE', 'GOZTEPE', 'FENERBAHCE', 'SAHRAYI CEDIT', 'OSMANAGA', 'ACIBADEM', 'EGITIM', 'HASANPASA'}, 'PENDIK': {'YAYALAR', 'ESENYALI', 'ORTA', 'SEYHLI', 'BELIRTILMEMIS', 'BATI', 'AHMET YESEVI', 'YENI', 'VELIBABA', 'YENISEHIR', 'KURNA', 'EMIRLI', 'KURTDOGMUS', 'SULUNTEPE', 'KAYNARCA', 'GOCBEYLI', 'DUMLUPINAR', 'KURTKOY', 'ESENLER', 'DOGU', 'SAPAN BAGLARI', 'GUZELYALI', 'FATIH', 'RAMAZANOGLU', 'CAMCESME', 'KAVAKPINAR', 'FEVZI CAKMAK', 'ORHANGAZI', 'SANAYI', 'BAHCELIEVLER', 'HARMANDERE', 'CAMLIK', 'GULLU BAGLAR', 'YESILBAGLAR', 'ERTUGRUL GAZI', 'BALLICA', 'CINARDERE'}, 'ATASEHIR': {'ASIK VEYSEL', 'FERHATPASA', 'BELIRTILMEMIS', 'FETIH', 'YENISEHIR', 'MEVLANA', 'KUCUKBAKKALKOY', 'YENI SAHRA', 'YENICAMLICA', 'YENI CAMLICA', 'MUSTAFA KEMAL', 'ORNEK', 'ICERENKOY', 'ASIKVEYSEL', 'INONU', 'ATATURK', 'ESATPASA', 'BARBAROS', 'MIMAR SINAN', 'KAYISDAGI'}, 'USKUDAR': {'SELAMI ALI', 'SULTANTEPE', 'KUPLUCE', 'KANDILLI', 'KUCUKSU', 'KUCUK CAMLICA', 'SELIMIYE', 'ICADIYE', 'YAVUZTURK', 'MURAT REIS', 'KISIKLI', 'FERAH', 'AHMEDIYE', 'UNALAN', 'KULELI', 'BURHANIYE', 'VALIDE I ATIK', 'ALTUNIZADE', 'MEHMET AKIF ERSOY', 'BEYLERBEYI', 'GUZELTEPE', 'BULGURLU', 'KIRAZLITEPE', 'CUMHURIYET', 'SALACAK', 'ZEYNEP KAMIL', 'BAHCELIEVLER', 'CENGELKOY', 'AZIZ MAHMUT HUDAYI', 'BARBAROS', 'ACIBADEM', 'MIMAR SINAN', 'KUZGUNCUK'}, 'SULTANBEYLI': {'MEHMET AKIF', 'AHMET YESEVI', 'ABDURRAHMANGAZI', 'ORHANGAZI', 'MECIDIYE', 'HAMIDIYE', 'AKSEMSETTIN', 'TURGUT REIS', 'FATIH', 'TURGUTREIS', 'NECIP FAZIL', 'MIMAR SINAN', 'YAVUZ SELIM', 'BATTALGAZI', 'ADIL', 'BELIRTILMEMIS', 'HASANPASA'}, 'MALTEPE': {'ZUMRUTEVLER', 'ALTAYCESME', 'ESENKENT', 'ALTINTEPE', 'IDEALTEPE', 'BELIRTILMEMIS', 'BASIBUYUK', 'GULENSU', 'AYDINEVLER', 'KUCUKYALI', 'YALI', 'CINAR', 'CEVIZLI', 'FEYZULLAH', 'BUYUKBAKKALKOY', 'BAGLARBASI', 'FINDIKLI', 'GULSUYU', 'GIRNE'}, 'BEYKOZ': {'GUMUSSUYU', 'ISHAKLI', 'GOKSU', 'GOLLU', 'ALIBAHADIR', 'ANADOLUHISARI', 'BOZHANE', 'DERESEKI', 'BELIRTILMEMIS', 'ANADOLUKAVAGI', 'ANADOLU KAVAGI', 'ANADOLU FENERI', 'AKBABA', 'PASABAHCE', 'ACARLAR', 'YENIMAHALLE', 'MAHMUT SEVKET PASA', 'KAYNARCA', 'ANADOLU HISARI', 'POLONEZKOY', 'CAMLIBAHCE', 'CIFTLIK', 'GORELE', 'POYRAZKOY', 'OGUMCE', 'CIGDEM', 'YENI MAHALLE', 'INCIRKOY', 'KILICLI', 'SOGUKSU', 'TOKATKOY', 'FATIH', 'CUBUKLU', 'ZERZAVATCI', 'GOZTEPE', 'PASAMANDIRA', 'KAVACIK', 'YALIKOY', 'MERKEZ', 'BAKLACI', 'CUMHURIYET', 'MAHMUTSEVKETPASA', 'RUZGARLIBAHCE', 'KANLICA', 'ORNEKKOY', 'CENGELDERE', 'ORTACESME', 'YAVUZ SELIM', 'RIVA', 'ELMALI'}, 'SILE': {'KUMBABA', 'ERENLER', 'UVEZLI', 'SORTULLU', 'GOKSU', 'KARAMANDERE', 'KURFALLI', 'GOCE', 'AVCIKORU', 'HACI KASIM', 'CELEBI', 'AHMETLI', 'BELIRTILMEMIS', 'KORUCU', 'SUAYIPLI', 'KOMURLUK', 'HACILLI', 'YENIKOY', 'KURNA', 'DOGANCILI', 'KARAKIRAZ', 'TEKE', 'AKCAKESE', 'SAHILKOY', 'KIZILCA', 'KERVANSARAY', 'KARACAKOY', 'BICKIDERE', 'CAVUS', 'KALEM', 'ISAKOY', 'ALACALI', 'IMRENLI', 'YAKA', 'ESENCELI', 'ORUCOGLU', 'ULUPELIT', 'CAYIRBASI', 'SOFULAR', 'AGACDERE', 'AGVA', 'BOZGOCA', 'CENGILLI', 'CATAKLI', 'DARLIK', 'YAZIMANAYIR', 'IMRENDERE', 'OVACIK', 'BALIBEY', 'MESRUTIYET', 'DEGIRMENCAYIRI', 'CIFT MAHALLE BILGISI', 'KADIKOY', 'GOKMASLI', 'HASANLI', 'YESILVADI', 'GEREDELI', 'KABAKOZ', 'OSMANKOY', 'BUCAKLI', 'KARABEYLI', 'SATMAZLI', 'SOGULLU', 'HACIKASIM'}, 'TUZLA': {'CAMI', 'ICMELER', 'DERI OSB', 'ORTA', 'BELIRTILMEMIS', 'EVLIYA CELEBI', 'SIFA', 'ISTASYON', 'POSTANE', 'ANADOLU', 'ORHANLI', 'AYDINLI', 'FATIH', 'AKFIRAT', 'TEPEOREN', 'AYDINTEPE', 'MESCIT', 'YAYLA', 'MIMAR SINAN'}, 'ADALAR': {'MADEN', 'KINALIADA', 'BURGAZADA', 'HEYBELIADA', 'NIZAM', 'BELIRTILMEMIS', 'BUYUKADA'}, 'SISLI': {'GULBAHAR', 'ESENTEPE', 'MERKEZ'}, 'SARIYER': {'MASLAK', 'BALTALIMANI', 'GARIPCE'}, 'UNKNOWN':{'UNKNOWN'}, 'BELİRTİLMEMİŞ':{'BELİRTİLMEMİŞ'}}
  
  # -*- coding: utf-8 -*-
  convert_key= {'ADNAN MENDERES': 'ADNAN MENDERES', 'ANADOLU': 'ANADOLU', 'ARNAVUTKOY MERKEZ': 'ARNAVUTKÖY MERKEZ', 'ATATURK': 'BARBAROS', 'BAKLALI': 'BAKLALI', 'BALABAN': 'BALABAN', 'BOGAZKOY ISTIKLAL': 'BOĞAZKÖY İSTİKLAL', 'BOLLUCA': 'BOLLUCA', 'BOYALIK': 'BOYALIK', 'CILINGIR': 'ÇİLİNGİR', 'DELIKLIKAYA': 'DELİKLİKAYA', 'DURSUNKOY': 'DURSUNKÖY', 'DURUSU': 'DURUSU', 'FATIH': 'FATİH', 'HACIMASLI': 'HACIMAŞLI', 'HADIMKOY': 'HADIMKÖY', 'HARACCI': 'HARAÇÇI', 'HASTANE': 'HASTANE', 'HICRET': 'HİCRET', 'IMRAHOR': 'İMRAHOR', 'ISLAMBEY': 'İSLAMBEY', 'KARABURUN': 'KARABURUN', 'KARLIBAYIR': 'KARLIBAYIR', 'MARESAL FEVZI CAKMAK': 'MAREŞAL FEVZİ ÇAKMAK', 'MAVIGOL': 'MAVİGÖL', 'MUSTAFA KEMAL PASA': 'MUSTAFA KEMAL PAŞA', 'NENEHATUN': 'NENEHATUN', 'OMERLI': 'REŞADİYE', 'SAZLIBOSNA': 'SAZLIBOSNA', 'TASOLUK': 'TAŞOLUK', 'TAYAKADIN': 'TAYAKADIN', 'TERKOS': 'TERKOS', 'YASSIOREN': 'YASSIÖREN', 'YAVUZ SELIM': 'YAVUZ SELİM', 'YENIKOY': 'YENİKÖY', 'YESILBAYIR': 'YEŞİLBAYIR', 'YUNUS EMRE': 'YUNUS EMRE', 'AMBARLI': 'AMBARLI', 'CIHANGIR': 'CİHANGİR', 'DENIZKOSKLER': 'DENİZKÖŞKLER', 'FIRUZKOY': 'FİRUZKÖY', 'GUMUSPALA': 'GÜMÜŞPALA', 'MERKEZ': 'MERKEZ', 'TAHTAKALE': 'TAHTAKALE', 'UNIVERSITE': 'ÜNİVERSİTE', 'YESILKENT': 'YEŞİLKENT', '100. YIL': '100. YIL', '15 TEMMUZ': '15 TEMMUZ', 'BAGLAR': 'BAĞLAR', 'BARBAROS': 'BARBAROS', 'CINAR': 'ÇINAR', 'DEMIRKAPI': 'DEMİRKAPI', 'FEVZI CAKMAK': 'FEVZİ ÇAKMAK', 'GOZTEPE': 'GÖZTEPE', 'GUNESLI': 'GÜNEŞLİ', 'HURRIYET': 'HÜRRİYET', 'INONU': 'İNÖNÜ', 'KAZIM KARABEKIR': 'KAZIM KARABEKİR', 'KEMALPASA': 'KEMALPAŞA', 'KIRAZLI': 'KİRAZLI', 'MAHMUTBEY': 'MAHMUTBEY', 'SANCAKTEPE': 'SANCAKTEPE', 'YENIGUN': 'YENİGÜN', 'YENIMAHALLE': 'YENIMAHALLE', 'YILDIZTEPE': 'YILDIZTEPE', 'BAHCELIEVLER': 'BAHÇELİEVLER', 'COBANCESME': 'CUMHURİYET', 'CUMHURIYET': 'CUMHURİYET', 'SIRINEVLER': 'ŞİRİNEVLER', 'SIYAVUSPASA': 'SİYAVUŞPAŞA', 'SOGANLI': 'SOĞANLI', 'YENIBOSNA': 'YENİBOSNA MERKEZ', 'ZAFER': 'ZAFER', 'KOCASINAN': 'KOCASİNAN MERKEZ', 'ATAKOY 1. KISIM': 'ATAKÖY 1. KISIM', 'ATAKOY 2 5 6. KISIM': 'ATAKÖY 2-5-6. KISIM', 'ATAKOY 3 4 11. KISIM': 'ATAKÖY 3-4-11. KISIM', 'ATAKOY 7 8 9 10. KISIM': 'ATAKÖY 7-8-9-10. KISIM', 'BASINKOY': 'BASINKÖY', 'CEVIZLIK': 'CEVİZLİK', 'KARTALTEPE': 'KARTALTEPE', 'OSMANIYE': 'OSMANİYE', 'SAKIZAGACI': 'SAKIZAĞACI', 'SENLIKKOY': 'ŞENLİKKÖY', 'YESILKOY': 'YEŞİLKÖY', 'YESILYURT': 'YEŞİLYURT', 'ZEYTINLIK': 'ZEYTİNLİK', 'ZUHURATBABA': 'ZUHURATBABA', 'BESTELSIZ': 'BEŞTELSİZ', 'CIRPICI': 'ÇIRPICI', 'GOKALP': 'GÖKALP', 'KAZLICESME': 'KAZLIÇEŞME', 'MALTEPE': 'MALTEPE', 'MERKEZEFENDI': 'MERKEZEFENDİ', 'NURIPASA': 'NURİPAŞA', 'SEYITNIZAM': 'SEYİTNİZAM', 'TELSIZ': 'TELSİZ', 'VELIEFENDI': 'VELİEFENDİ', 'YENIDOGAN': 'YENİDOĞAN', 'YESILTEPE': 'YEŞİLTEPE', 'SUMER': 'SÜMER', 'ALTINSEHIR': 'ALTINŞEHİR', 'BAHCESEHIR 1. KISIM': 'BAHÇEŞEHİR 1. KISIM', 'BAHCESEHIR 2. KISIM': 'BAHÇEŞEHİR 2. KISIM', 'BASAK': 'BAŞAK', 'BASAKSEHIR': 'BAŞAKŞEHİR', 'GUVERCINTEPE': 'GÜVERCİNTEPE', 'KAYABASI': 'KAYABAŞI', 'SAHINTEPE': 'ŞAHİNTEPE', 'SAMLAR': 'ŞAMLAR', 'ZIYA GOKALP': 'ZİYA GÖKALP', 'ALTINTEPSI': 'ALTINTEPSİ', 'CEVATPASA': 'CEVATPAŞA', 'ISMET PASA': 'İSMET PAŞA', 'MURATPASA': 'MURATPAŞA', 'ORTA': 'ORTA', 'TERAZIDERE': 'TERAZİDERE', 'VATAN': 'VATAN', 'YILDIRIM': 'YILDIRIM', 'KOCATEPE': 'KOCATEPE', 'ABBASAGA': 'ABBASAĞA', 'AKAT': 'AKAT', 'ARNAVUTKOY': 'ARNAVUTKÖY', 'BALMUMCU': 'BALMUMCU', 'BEBEK': 'BEBEK', 'CIHANNUMA': 'CİHANNÜMA', 'ETILER': 'ETİLER', 'GAYRETTEPE': 'GAYRETTEPE', 'KONAKLAR': 'KONAKLAR', 'KULTUR': 'KURUÇEŞME', 'KURUCESME': 'KÜLTÜR', 'LEVAZIM': 'LEVAZIM', 'LEVENT': 'LEVENT', 'MECIDIYE': 'MECİDİYE', 'MURADIYE': 'MURADİYE', 'NISBETIYE': 'NİSBETİYE', 'ORTAKOY': 'ORTAKÖY', 'SINANPASA': 'SİNANPAŞA', 'TURKALI': 'TÜRKALİ', 'ULUS': 'ULUS', 'VISNEZADE': 'VİŞNEZADE', 'YILDIZ': 'YILDIZ', 'DIKILITAS': 'DİKİLİTAŞ', 'BARIS': 'BARIŞ', 'BUYUKSEHIR': 'BÜYÜKŞEHİR', 'DEREAGZI': 'DEREAĞZI', 'GURPINAR': 'GÜRPINAR', 'KAVAKLI': 'KAVAKLI', 'MARMARA': 'MARMARA', 'SAHIL': 'SAHİL', 'YAKUPLU': 'YAKUPLU', 'ADNAN KAHVECI': 'ADNAN KAHVECİ', 'ARAP CAMI': 'ARAP CAMİ', 'ASMALI MESCIT': 'ASMALI MESCİT', 'BEDRETTIN': 'BEDRETTİN', 'BEREKETZADE': 'BEREKETZADE', 'BOSTAN': 'BOSTAN', 'BULBUL': 'BÜLBÜL', 'CAMIIKEBIR': 'CAMİİKEBİR', 'CUKUR': 'ÇUKUR', 'EMEKYEMEZ': 'EMEKYEMEZ', 'EVLIYA CELEBI': 'EVLİYA ÇELEBİ', 'FETIHTEPE': 'FETİHTEPE', 'FIRUZAGA': 'FİRUZAĞA', 'GUMUSSUYU': 'GÜMÜŞSUYU', 'HACIAHMET': 'HACIAHMET', 'HACIMIMI': 'HACIMİMİ', 'HALICIOGLU': 'HALICIOĞLU', 'HUSEYINAGA': 'HÜSEYİNAĞA', 'ISTIKLAL': 'İSTİKLAL', 'KADIMEHMET EFENDI': 'KADIMEHMET EFENDİ', 'KALYONCU KULLUGU': 'KALYONCU KULLUĞU', 'KAMER HATUN': 'KAMER HATUN', 'KAPTANPASA': 'KAPTANPAŞA', 'KATIP MUSTAFA CELEBI': 'KATİP MUSTAFA ÇELEBİ', 'KECECI PIRI': 'KEÇECİ PİRİ', 'KEMANKES KARAMUSTAFA PASA': 'KEMANKEŞ KARAMUSTAFA PAŞA', 'KILICALI PASA': 'KILIÇALİ PAŞA', 'KUCUK PIYALE': 'KÜÇÜK PİYALE', 'KULAKSIZ': 'KULAKSIZ', 'KULOGLU': 'KULOĞLU', 'MUEYYETZADE': 'MÜEYYETZADE', 'OMER AVNI': 'ÖMER AVNİ', 'ORNEKTEPE': 'ÖRNEKTEPE', 'PIRI PASA': 'PİRİ PAŞA', 'PIYALEPASA': 'PİYALEPAŞA', 'PURTELAS': 'PÜRTELAŞ', 'SAHKULU': 'ŞAHKULU', 'SEHIT MUHTAR': 'ŞEHİT MUHTAR', 'SURURI': 'SURURİ', 'SUTLUCE': 'SÜTLÜCE', 'TOMTOM': 'TOMTOM', 'YAHYA KAHYA': 'YAHYA KAHYA', 'YENISEHIR': 'YENİŞEHİR', 'CATMA MESCIT': 'ÇATMA MESCİT', '19 MAYIS': '19 MAYIS', 'AHMEDIYE': 'AHMEDİYE', 'ALKENT': 'ALKENT', 'CAKMAKLI': 'ÇAKMAKLI', 'CELALIYE': 'CELALİYE', 'EKINOBA': 'EKİNOBA', 'GUZELCE': 'GÜZELCE', 'KAMILOBA': 'KAMİLOBA', 'KARAAGAC': 'KARAAĞAÇ', 'KUMBURGAZ': 'KUMBURGAZ', 'MIMAR SINAN MERKEZ': 'MİMAR SİNAN MERKEZ', 'MIMAROBA': 'MİMAROBA', 'MURAT CESME': 'MURAT ÇEŞME', 'PINARTEPE': 'PINARTEPE', 'SINANOBA': 'SİNANOBA', 'TURKOBA': 'TÜRKOBA', 'DIZDARIYE': 'DİZDARİYE', 'AKALAN': 'AKALAN', 'AYDINLAR': 'AYDINLAR', 'BAHSAYIS': 'BAHŞAYİŞ', 'CAKIL': 'ÇAKIL', 'CANAKCA': 'ÇANAKÇA', 'CELEPKOY': 'CELEPKÖY', 'CIFTLIKKOY': 'ÇİFTLİKKÖY', 'DAGYENICE': 'DAĞYENİCE', 'ELBASAN': 'ELBASAN', 'FERHATPASA': 'FERHATPAŞA', 'GOKCEALI': 'GÖKÇEALİ', 'GUMUSPINAR': 'GÜMÜŞPINAR', 'HALLACLI': 'HALLAÇLI', 'HISARBEYLI': 'HİSARBEYLİ', 'IHSANIYE': 'İHSANİYE', 'IZZETTIN': 'İZZETTİN', 'KABAKCA': 'KABAKÇA', 'KALEICI': 'KALEİÇİ', 'KALFA': 'KALFA', 'KARACAKOY': 'KARACAKÖY', 'KARAMANDERE': 'KARAMANDERE', 'KESTANELIK': 'KESTANELİK', 'MURATBEY MERKEZ': 'MURATBEY MERKEZ', 'NAKKAS': 'NAKKAŞ', 'OKLALI': 'OKLALI', 'ORCUNLU': 'ÖRCÜNLÜ', 'ORENCIK': 'ÖRENCİK', 'ORMANLI': 'ORMANLI', 'OVAYENICE': 'OVAYENİCE', 'SUBASI': 'SUBAŞI', 'YALIKOY': 'YALIKÖY', 'YAYLACIK': 'YAYLACIK', 'KIZILCAALI': 'KIZILCAALİ', 'INCEGIZ': 'İNCEĞİZ', 'BELGRAT': 'BELGRAT', 'BIRLIK': 'BİRLİK', 'CIFTE HAVUZLAR': 'ÇİFTE HAVUZLAR', 'DAVUTPASA': 'DAVUTPAŞA', 'HAVAALANI': 'HAVAALANI', 'KEMER': 'KEMER', 'MENDERES': 'MENDERES', 'MIMAR SINAN': 'MİMAR SİNAN', 'NAMIK KEMAL': 'NAMIK KEMAL', 'ORUCREIS': 'ORUÇREİS', 'TUNA': 'TUNA', 'TURGUT REIS': 'TURGUT REİS', 'NINE HATUN': 'NİNE HATUN', 'AKCABURGAZ': 'AKÇABURGAZ', 'AKEVLER': 'AKEVLER', 'AKSEMSEDDIN': 'AKŞEMSEDDİN', 'ARDICLI': 'ARDIÇLI', 'ASIK VEYSEL': 'AŞIKVEYSEL', 'BAGLARCESME': 'BAĞLARÇEŞME', 'BALIKYOLU': 'BALIKYOLU', 'BARBAROS HAYRETTIN PASA': 'BARBAROS HAYRETTİN PAŞA', 'BATTALGAZI': 'BATTALGAZİ', 'ESENKENT': 'ESENKENT', 'GOKEVLER': 'GÖKEVLER', 'GUZELYURT': 'GÜZELYURT', 'INCIRTEPE': 'İNCİRTEPE', 'KOZA': 'KOZA', 'MEHTERCESME': 'MEHTERÇEŞME', 'MEVLANA': 'MEVLANA', 'NECIP FAZIL KISAKUREK': 'NECİP FAZIL KISAKÜREK', 'ORHAN GAZI': 'ORHAN GAZİ', 'ORNEK': 'ÖRNEK', 'OSMANGAZI': 'OSMANGAZİ', 'PINAR': 'PINAR', 'PIRI REIS': 'PİRİ REİS', 'SAADETDERE': 'SAADETDERE', 'SEHITLER': 'ŞEHİTLER', 'SELAHADDIN EYYUBI': 'SELAHADDİN EYYUBİ', 'SULEYMANIYE': 'SÜLEYMANİYE', 'SULTANIYE': 'SULTANİYE', 'TALATPASA': 'TALATPAŞA', 'TURGUT OZAL': 'TURGUT ÖZAL', 'UCEVLER': 'ÜÇEVLER', 'YENIKENT': 'YENİKENT', 'MEHMET AKIF ERSOY': 'MEHMET AKİF ERSOY', '5. LEVENT': '5. LEVENT', 'AGACLI': 'AĞAÇLI', 'AKPINAR': 'AKPINAR', 'AKSEMSETTIN': 'AKŞEMSETTİN', 'ALIBEYKOY': 'ALİBEYKÖY', 'CIFTALAN': 'ÇİFTALAN', 'CIRCIR': 'ÇIRÇIR', 'DEFTERDAR': 'DEFTERDAR', 'DUGMECILER': 'DÜĞMECİLER', 'EMNIYETTEPE': 'EMNİYETTEPE', 'ESENTEPE': 'ESENTEPE', 'GOKTURK MERKEZ': 'GÖKTÜRK MERKEZ', 'GUZELTEPE': 'GÜZELTEPE', 'KARADOLAP': 'KARADOLAP', 'MITHATPASA': 'MİTHATPAŞA', 'NISANCI': 'NİŞANCI', 'ODAYERI': 'ODAYERİ', 'PIRINCCI': 'PİRİNÇÇİ', 'RAMI CUMA': 'RAMİ CUMA', 'RAMI YENI': 'RAMİ YENİ', 'SAKARYA': 'SAKARYA', 'SILAHTARAGA': 'SİLAHTARAĞA', 'TOPCULAR': 'TOPÇULAR', 'YESILPINAR': 'YEŞİLPINAR', 'ISIKLAR': 'IŞIKLAR', 'AKSARAY': 'AKSARAY', 'ALEMDAR': 'ALEMDAR', 'ALI KUSCU': 'ALİ KUŞÇU', 'ATIKALI': 'ATİKALİ', 'AYVANSARAY': 'AYVANSARAY', 'BALABANAGA': 'BALABANAĞA', 'BALAT': 'BALAT', 'BEYAZIT': 'BEYAZIT', 'BINBIRDIREK': 'BİNBİRDİREK', 'CANKURTARAN': 'CANKURTARAN', 'CERRAHPASA': 'CERRAHPAŞA', 'CIBALI': 'CİBALİ', 'DEMIRTAS': 'DEMİRTAŞ', 'DERVIS ALI': 'DERVİŞ ALİ', 'HASEKI SULTAN': 'HASEKİ SULTAN', 'HIRKA I SERIF': 'HIRKA-İ ŞERİF', 'HOBYAR': 'HOBYAR', 'HOCA GIYASETTIN': 'HOCA GİYASETTİN', 'HOCA PASA': 'HOCA PAŞA', 'ISKENDERPASA': 'İSKENDERPAŞA', 'KALENDERHANE': 'KALENDERHANE', 'KARAGUMRUK': 'KARAGÜMRÜK', 'KATIP KASIM': 'KATİP KASIM', 'KEMAL PASA': 'KEMAL PAŞA', 'KOCA MUSTAFAPASA': 'KOCA MUSTAFAPAŞA', 'KUCUK AYASOFYA': 'KÜÇÜK AYASOFYA', 'MERCAN': 'MERCAN', 'MESIHPASA': 'MESİHPAŞA', 'MEVLANAKAPI': 'MEVLANAKAPI', 'MIMAR HAYRETTIN': 'MİMAR HAYRETTİN', 'MOLLA FENARI': 'MOLLA FENARİ', 'MOLLA GURANI': 'MOLLA GÜRANİ', 'MOLLA HUSREV': 'MOLLA HÜSREV', 'MUHSINE HATUN': 'MUHSİNE HATUN', 'NISANCA': 'NİŞANCA', 'RUSTEM PASA': 'RÜSTEM PAŞA', 'SARIDEMIR': 'SARIDEMİR', 'SEHREMINI': 'ŞEHREMİNİ', 'SEYYID OMER': 'SEYYİD ÖMER', 'SILIVRIKAPI': 'SİLİVRİKAPI', 'SULTAN AHMET': 'SULTAN AHMET', 'SUMBUL EFENDI': 'SÜMBÜL EFENDİ', 'TOPKAPI': 'TOPKAPI', 'YAVUZ SULTAN SELIM': 'YAVUZ SULTAN SELİM', 'YEDIKULE': 'YEDİKULE', 'ZEYREK': 'ZEYREK', 'SARAC IHSAK': 'SARAÇ İSHAK', 'SEHSUVAR BEY': 'ŞEHSUVAR BEY', 'TAYA HATUN': 'TAYA HATUN', 'YAVUZ SINAN': 'YAVUZ SİNAN', 'EMIN SINAN': 'EMİN SİNAN', 'HACI KADIN': 'HACI KADIN', 'BAGLARBASI': 'BAĞLARBAŞI', 'BARBAROS HAYRETTINPASA': 'BARBAROS HAYRETTİNPAŞA', 'KARADENIZ': 'KARADENİZ', 'KARAYOLLARI': 'KARAYOLLARI', 'KARLITEPE': 'KARLITEPE', 'PAZARICI': 'PAZARİÇİ', 'SARIGOL': 'SARIGÖL','SEMSIPASA': 'ŞEMSİPAŞA', 'YENI MAHALLE': 'YENİ MAHALLE', 'YILDIZTABYA': 'YILDIZTABYA', 'ABDURRAHMAN NAFIZ GURMAN': 'ABDURRAHMAN NAFİZ GÜRMAN', 'AKINCILAR': 'AKINCILAR', 'GENCOSMAN': 'GENÇOSMAN', 'GUNESTEPE': 'GÜNEŞTEPE', 'GUVEN': 'GÜVEN', 'MARESAL CAKMAK': 'MAREŞAL ÇAKMAK', 'MEHMET NESIH OZMEN': 'MEHMET NESİH ÖZMEN', 'SANAYI': 'SANAYİ', 'TOZKOPARAN': 'TOZKOPARAN', 'HAZNEDAR': 'HAZNEDAR', 'CAGLAYAN': 'ÇAĞLAYAN', 'CELIKTEPE': 'ÇELİKTEPE', 'EMNIYET': 'EMNİYET', 'GULTEPE': 'GÜLTEPE', 'GURSEL': 'GÜRSEL', 'HAMIDIYE': 'HAMİDİYE', 'HARMANTEPE': 'HARMANTEPE', 'NURTEPE': 'NURTEPE', 'ORTABAYIR': 'ORTABAYIR', 'SEYRANTEPE': 'SEYRANTEPE', 'SIRINTEPE': 'ŞİRİNTEPE', 'SULTAN SELIM': 'SULTAN SELİM', 'TELSIZLER': 'TELSİZLER', 'YAHYA KEMAL': 'YAHYA KEMAL', 'YESILCE': 'YEŞİLCE', 'ATAKENT': 'ATAKENT', 'CENNET': 'CENNET', 'HALKALI': 'HALKALI MERKEZ', 'ISTASYON': 'İSTASYON', 'KANARYA': 'KANARYA', 'MEHMET AKIF': 'MEHMET AKİF', 'SOGUTLU CESME': 'SÖĞÜTLÜ ÇEŞME', 'SULTAN MURAT': 'SULTAN MURAT', 'TEVFIK BEY': 'TEVFİK BEY', 'YARIMBURGAZ': 'YARIMBURGAZ', 'YESILOVA': 'YEŞİLOVA', 'BESYOL': 'BEŞYOL', 'AYAZAGA': 'AYAZAĞA', 'BAHCEKOY KEMER': 'BAHÇEKÖY KEMER', 'BAHCEKOY MERKEZ': 'BAHCEKOY MERKEZ', 'BAHCEKOY YENI': 'BAHÇEKÖY YENİ', 'BALTALIMANI': 'BALTALİMANI', 'BUYUKDERE': 'BÜYÜKDERE', 'CAMLITEPE': 'ÇAMLITEPE', 'CAYIRBASI': 'ÇAYIRBAŞI', 'DARUSSAFAKA': 'DARÜŞŞAFAKA', 'DEMIRCI': 'DEMİRCİKÖY', 'EMIRGAN': 'EMİRGAN', 'FATIH SULTAN MEHMET': 'FATİH SULTAN MEHMET', 'FERAHEVLER': 'FERAHEVLER', 'GARIPCE': 'GARİPÇE', 'GUMUSDERE': 'GÜMÜŞDERE', 'HUZUR': 'HUZUR', 'ISTINYE': 'İSTİNYE', 'KIRECBURNU': 'KİREÇBURNU', 'KISIRKAYA': 'KISIRKAYA', 'KOCATAS': 'KOCATAŞ', 'KUMKOY': 'KUMKÖY', 'MADEN': 'MADEN', 'MASLAK': 'MASLAK', 'POLIGON': 'POLİGON', 'PTT EVLERI': 'PTT EVLERİ', 'RESITPASA': 'REŞİTPAŞA', 'RUMELI HISARI': 'RUMELİ HİSARI', 'RUMELI KAVAGI': 'RUMELİ KAVAĞI', 'RUMELIFENERI': 'RUMELİFENERİ', 'SARIYER MERKEZ': 'SARIYER MERKEZ', 'TARABYA': 'TARABYA', 'USKUMRUKOY': 'USKUMRUKÖY', 'ZEKERIYAKOY': 'ZEKERİYAKÖY', 'YENI': 'YENİ', 'AKOREN': 'AKÖREN', 'ALIBEY': 'ALİBEY', 'ALIPASA': 'ALİPAŞA', 'BEYCILER': 'BEYCİLER', 'BUYUK CAVUSLU': 'BÜYÜK ÇAVUŞLU', 'BUYUK KILICLI': 'BÜYÜK KILIÇLI', 'BUYUK SINEKLI': 'BÜYÜK SİNEKLİ', 'CANTA SANCAKTEPE': 'ÇANTA SANCAKTEPE', 'CAYIRDERE': 'ÇAYIRDERE', 'CELTIK': 'ÇELTİK', 'DANAMANDIRA': 'DANAMANDIRA', 'DEGIRMENKOY FEVZIPASA': 'DEĞİRMENKÖY FEVZİPAŞA', 'DEGIRMENKOY ISMETPASA': 'DEĞİRMENKÖY İSMETPAŞA', 'FENER': 'FENER', 'GAZITEPE': 'GAZİTEPE', 'GUMUSYAKA': 'GÜMÜŞYAKA', 'KADIKOY': 'KADIKÖY', 'KAVAKLI HURRIYET': 'KAVAKLI HÜRRİYET', 'KAVAKLI ISTIKLAL': 'KAVAKLI İSTİKLAL', 'KUCUK SINEKLI': 'KÜÇÜK SİNEKLİ', 'KURFALLI': 'KURFALLI', 'PIRI MEHMET PASA': 'PİRİ MEHMET PAŞA', 'SAYALAR': 'SAYALAR', 'SELIMPASA': 'SELİMPAŞA', 'SEMIZKUMLAR': 'SEMİZKUMLAR', 'SEYMEN': 'SEYMEN', 'YOLCATI': 'YOLÇATI', 'KUCUK KILICLI': 'KÜÇÜK KILIÇLI', '75. YIL': '75. YIL', 'CEBECI': 'CEBECİ', 'GAZI': 'GAZİ', 'HABIBLER': 'HABİBLER', 'ISMETPASA': 'İSMETPAŞA', 'MALKOCOGLU': 'MALKOÇOĞLU', 'SULTANCIFTLIGI': 'SULTANÇİFTLİĞİ', 'UGUR MUMCU': 'YAKACIK ÇARŞI', 'YAYLA': 'YAYLA', '50. YIL': '50. YIL', 'ESKİ HABİPLER': 'ESKİ HABİPLER', 'ZÜBEYDE HANIM': 'ZÜBEYDE HANIM', 'BOZKURT': 'BOZKURT', 'DUATEPE': 'DUATEPE', 'ESKISEHIR': 'ESKİŞEHİR', 'FERIKOY': 'FERİKÖY', 'FULYA': 'FULYA', 'GULBAHAR': 'GÜLBAHAR', 'HALASKARGAZI': 'HALASKARGAZİ', 'HALIDE EDIP ADIVAR': 'HALİDE EDİP ADIVAR', 'HALIL RIFAT PASA': 'HALİL RIFAT PAŞA', 'HARBIYE': 'HARBİYE', 'KUSTEPE': 'KUŞTEPE', 'MAHMUT SEVKET PASA': 'MAHMUT ŞEVKET PAŞA', 'MECIDIYEKOY': 'MECİDİYEKÖY', 'MESRUTIYET': 'MEŞRUTİYET', 'PASA': 'PAŞA', 'TESVIKIYE': 'TEŞVİKİYE', 'ERGENEKON': 'ERGENEKON', 'IZZET PASA': 'İZZET PAŞA', 'UNKNOWN': 'UNKNOWN', 'ADEM YAVUZ': 'ADEM YAVUZ', 'ARMAGANEVLER': 'ARMAĞANEVLER', 'ASAGI DUDULLU': 'AŞAĞI DUDULLU', 'CAKMAK': 'ÇAKMAK', 'CAMLIK': 'ÇAMLIK', 'CEMIL MERIC': 'CEMİL MERİÇ', 'DUDULLU': 'DUDULLU', 'DUMLUPINAR': 'DUMLUPINAR', 'ELMALIKENT': 'ELMALIKENT', 'ESENEVLER': 'ESENEVLER', 'ESENSEHIR': 'ESENŞEHİR', 'FINANSKENT': 'FİNANSKENT', 'HEKIMBASI': 'HEKİMBAŞI', 'IHLAMURKUYU': 'IHLAMURKUYU', 'INKILAP': 'İNKILAP', 'MADENLER': 'MADENLER', 'NECIP FAZIL': 'NECİP FAZIL', 'PARSELLER': 'PARSELLER', 'SARAY': 'SARAY', 'SERIFALI': 'ŞERİFALİ', 'SITE': 'SİTE', 'TANTAVI': 'TANTAVİ', 'TATLISU': 'TATLISU', 'TEPEUSTU': 'TEPEÜSTÜ', 'TOPAGACI': 'TOPAĞACI', 'YAMANEVLER': 'YAMANEVLER', 'YUKARI DUDULLU': 'YUKARI DUDULLU', 'YUKARIDUDULLU': 'YUKARIDUDULLU', 'DUDULLU OSB': 'DUDULLU OSB', 'YALI': 'YALI', 'SOGANLIK YENI': 'SOĞANLIK YENİ', 'ATALAR': 'ATALAR', 'CAVUSOGLU': 'ÇAVUŞOĞLU', 'CEVIZLI': 'CEVİZLİ', 'KARLIKTEPE': 'KARLIKTEPE', 'KORDONBOYU': 'KORDONBOYU', 'ORHANTEPE': 'ORHANTEPE', 'PETROL IS': 'PETROL İŞ', 'SOGANLIK': 'SOĞANLIK YENİ', 'SOGUKPINAR': 'TOPSELVİ', 'TOPSELVI': 'UĞUR MUMCU', 'YAKACIK CARSI': 'YAKACIK YENİ', 'YAKACIK YENI': 'YALI', 'YUKARI': 'YUKARI', 'YUNUS': 'YUNUS', 'KIRAZLIDERE': 'KİRAZLIDERE', 'ALEMDAG': 'ALEMDAĞ', 'CATALMESE': 'ÇATALMEŞE', 'EKSIOGLU': 'EKŞİOĞLU', 'GUNGOREN': 'GÜNGÖREN', 'HUSEYINLI': 'HÜSEYİNLİ', 'KOCULLU': 'KOÇULLU', 'NISANTEPE': 'ÖMERLİ', 'RESADIYE': 'SIRAPINAR', 'SIRAPINAR': 'SOĞUKPINAR', 'TASDELEN': 'TAŞDELEN', 'KEMAL TURKLER': 'KEMAL TÜRKLER', 'ABDURRAHMANGAZI': 'ABDURRAHMANGAZİ', 'CAFERAGA': 'CAFERAĞA', 'EMEK': 'EMEK', 'EYUP SULTAN': 'EYÜP SULTAN', 'FIKIRTEPE': 'FİKİRTEPE', 'HILAL': 'HİLAL', 'MECLIS': 'MECLİS', 'MERVE': 'MERVE', 'PASAKOY': 'PAŞAKÖY', 'SAFA': 'SAFA', 'SARIGAZI': 'SARIGAZİ', 'VEYSEL KARANI': 'VEYSEL KARANİ', 'KOZYATAGI': 'KOZYATAĞI', 'ACIBADEM': 'ACIBADEM', 'BOSTANCI': 'BOSTANCI', 'CADDEBOSTAN': 'CADDEBOSTAN', 'EGITIM': 'EĞİTİM', 'EMIRLI': 'EMİRLİ', 'ERENKOY': 'ERENKÖY', 'FENERBAHCE': 'FENERBAHÇE', 'FENERYOLU': 'FENERYOLU', 'HASANPASA': 'HASANPAŞA', 'KOSUYOLU': 'KOŞUYOLU', 'MERDIVENKOY': 'MERDİVENKÖY', 'OSMANAGA': 'OSMANAĞA', 'RASIMPASA': 'RASİMPAŞA', 'SAHRAYI CEDIT': 'SAHRAYICEDİT', 'SUADIYE': 'SUADİYE', 'ZUHTUPASA': 'ZÜHTÜPAŞA', 'YESILBAGLAR': 'YEŞİLBAĞLAR', 'BALLICA': 'BALLICA', 'AHMET YESEVI': 'AHMET YESEVİ', 'BATI': 'BATI', 'CAMCESME': 'ÇAMÇEŞME', 'CINARDERE': 'ÇINARDERE', 'DOGU': 'DOĞU', 'ERTUGRUL GAZI': 'ERTUĞRUL GAZİ', 'ESENLER': 'ESENLER', 'ESENYALI': 'ESENYALI', 'GOCBEYLI': 'GÖÇBEYLİ', 'GULLU BAGLAR': 'GÜLLÜ BAĞLAR', 'GUZELYALI': 'GÜZELYALI', 'HARMANDERE': 'HARMANDERE', 'ICERENKOY': 'İÇERENKÖY', 'KAVAKPINAR': 'KAVAKPINAR', 'KAYNARCA': 'KAYNARCA', 'KURNA': 'KURNA', 'KURTDOGMUS': 'KURTDOĞMUŞ', 'KURTKOY': 'KURTKÖY', 'ORHANGAZI': 'ORHANGAZİ', 'RAMAZANOGLU': 'RAMAZANOĞLU', 'SAPAN BAGLARI': 'SAPAN BAĞLARI', 'SEYHLI': 'ŞEYHLİ', 'SULUNTEPE': 'SÜLÜNTEPE', 'VELIBABA': 'VELİBABA', 'YAYALAR': 'YAYALAR', 'ASIKVEYSEL': 'ATATÜRK', 'ESATPASA': 'ESATPAŞA', 'FETIH': 'FETİH', 'KAYISDAGI': 'KAYIŞDAĞI', 'KUCUKBAKKALKOY': 'KÜÇÜKBAKKALKÖY', 'MUSTAFA KEMAL': 'MUSTAFA KEMAL', 'YENI CAMLICA': 'YENİ ÇAMLICA', 'YENISAHRA': 'YENİSAHRA', 'YENICAMLICA': 'YENİÇAMLICA', 'YENI SAHRA': 'YENİ SAHRA', 'YENI SEHIR': 'YENİ ŞEHİR', 'ALTUNIZADE': 'ALTUNİZADE', 'AZIZ MAHMUT HUDAYI': 'AZİZ MAHMUT HÜDAYİ', 'BEYLERBEYI': 'BEYLERBEYİ', 'BULGURLU': 'BULGURLU', 'BURHANIYE': 'BURHANİYE', 'CENGELKOY': 'ÇENGELKÖY', 'ICADIYE': 'İCADİYE', 'KANDILLI': 'KANDİLLİ', 'KIRAZLITEPE': 'KİRAZLITEPE', 'KISIKLI': 'KISIKLI', 'KUCUK CAMLICA': 'KÜÇÜK ÇAMLICA', 'KUCUKSU': 'KÜÇÜKSU', 'KULELI': 'KÜPLÜCE', 'KUPLUCE': 'KULELİ', 'KUZGUNCUK': 'KUZGUNCUK', 'MURAT REIS': 'MURATREİS', 'SALACAK': 'SALACAK', 'SELAMI ALI': 'SELAMİ ALİ', 'SELIMIYE': 'SELİMİYE', 'SULTANTEPE': 'SULTANTEPE', 'UNALAN': 'ÜNALAN', 'VALIDE I ATIK': 'VALİDE-İ ATİK', 'YAVUZTURK': 'YAVUZTÜRK', 'ZEYNEP KAMIL': 'ZEYNEP KAMİL', 'FERAH': 'FERAH', 'ADIL': 'ADİL', 'TURGUTREIS': 'TURGUT REİS', 'AHMET YESEVİ': 'AHMET YESEVI', 'ALTAYCESME': 'ALTAYÇEŞME', 'ALTINTEPE': 'ALTINTEPE', 'BUYUKBAKKALKOY': 'BÜYÜKBAKKALKÖY', 'FEYZULLAH': 'FEYZULLAH', 'FINDIKLI': 'FINDIKLI', 'GIRNE': 'GİRNE', 'GULENSU': 'GÜLENSU', 'GULSUYU': 'GÜLSUYU', 'IDEALTEPE': 'İDEALTEPE', 'KUCUKYALI': 'KÜÇÜKYALI MERKEZ', 'ZUMRUTEVLER': 'ZÜMRÜTEVLER', 'AYDINEVLER': 'AYDINEVLER', 'BASIBUYUK': 'BAŞIBÜYÜK', 'ACARLAR': 'ACARLAR', 'AKBABA': 'AKBABA', 'ALIBAHADIR': 'ALİBAHADIR', 'ANADOLU HISARI': 'ANADOLU HİSARI', 'ANADOLU KAVAGI': 'ANADOLU KAVAĞI', 'ANADOLUHISARI': 'ANADOLUHİSARI', 'ANADOLUKAVAGI': 'ANADOLUKAVAĞI', 'BAKLACI': 'BAKLACI', 'BOZHANE': 'BOZHANE', 'CAMLIBAHCE': 'ÇAMLIBAHÇE', 'CENGELDERE': 'ÇENGELDERE', 'CIFTLIK': 'ÇİFTLİK', 'CIGDEM': 'ÇİĞDEM', 'CUBUKLU': 'ÇUBUKLU', 'DERESEKI': 'DERESEKİ', 'ELMALI': 'ELMALI', 'GOKSU': 'GÖKSU', 'GOLLU': 'GÖLLÜ', 'GORELE': 'GÖRELE', 'INCIRKOY': 'İNCİRKÖY', 'ISHAKLI': 'İSHAKLI', 'KANLICA': 'KANLICA', 'KAVACIK': 'KAVACIK', 'KILICLI': 'KILIÇLI', 'MAHMUTSEVKETPASA': 'MAHMUTŞEVKETPAŞA', 'OGUMCE': 'ÖĞÜMCE', 'ORNEKKOY': 'ÖRNEKKÖY', 'ORTACESME': 'ORTAÇEŞME', 'PASABAHCE': 'PAŞABAHÇE', 'PASAMANDIRA': 'PAŞAMANDIRA', 'POLONEZKOY': 'POLONEZKÖY', 'POYRAZKOY': 'POYRAZKÖY', 'RIVA': 'RİVA', 'RUZGARLIBAHCE': 'RÜZGARLIBAHÇE', 'SOGUKSU': 'SOĞUKSU', 'TOKATKOY': 'TOKATKÖY', 'ZERZAVATCI': 'ZERZAVATÇI', 'ANADOLU FENERI': 'ANADOLUFENERİ', 'AGACDERE': 'AĞAÇDERE', 'AGVA': 'AĞVA MERKEZ', 'AHMETLI': 'AHMETLİ', 'ALACALI': 'ALACALI', 'AVCIKORU': 'AVCIKORU', 'BALIBEY': 'BALİBEY', 'BICKIDERE': 'BIÇKIDERE', 'BOZGOCA': 'BOZGOCA', 'BUCAKLI': 'BUCAKLI', 'CATAKLI': 'ÇATAKLI', 'CAVUS': 'ÇAVUŞ', 'CELEBI': 'ÇELEBİ', 'CENGILLI': 'ÇENGİLLİ', 'DARLIK': 'DARLIK', 'DEGIRMENCAYIRI': 'DEĞİRMENÇAYIRI', 'DOGANCILI': 'DOĞANCILI', 'ERENLER': 'ERENLER', 'ESENCELI': 'ESENCELİ', 'GEREDELI': 'GEREDELİ', 'GOCE': 'GÖÇE', 'GOKMASLI': 'GÖKMAŞLI', 'HACI KASIM': 'HACI KASIM', 'HACIKASIM': 'HACIKASIM', 'HACILLI': 'HACILLI', 'HASANLI': 'HASANLI', 'IMRENDERE': 'İMRENDERE', 'IMRENLI': 'İMRENLİ', 'ISAKOY': 'İSAKÖY', 'KABAKOZ': 'KABAKOZ', 'KALEM': 'KALEM', 'KARABEYLI': 'KARABEYLİ', 'KARAKIRAZ': 'KARAKİRAZ', 'KERVANSARAY': 'KERVANSARAY', 'KIZILCA': 'KIZILCA', 'KORUCU': 'KORUCU', 'KOMURLUK': 'KÖMÜRLÜK', 'KUMBABA': 'KUMBABA', 'ORUCOGLU': 'ORUÇOĞLU', 'OSMANKOY': 'OSMANKÖY', 'OVACIK': 'OVACIK', 'SAHILKOY': 'SAHİLKÖY', 'SATMAZLI': 'SATMAZLI', 'SOFULAR': 'SOFULAR', 'SOGULLU': 'SOĞULLU', 'SORTULLU': 'SORTULLU', 'SUAYIPLI': 'ŞUAYİPLİ', 'TEKE': 'TEKE', 'ULUPELIT': 'ULUPELİT', 'UVEZLI': 'ÜVEZLİ', 'YAKA': 'YAKA', 'YAZIMANAYIR': 'YAZIMANAYIR', 'YESILVADI': 'YEŞİLVADİ', 'AKCAKESE': 'AKÇAKESE', 'YAYLALI': 'YAYLALI', 'ICMELER': 'İÇMELER', 'AKFIRAT': 'AKFIRAT', 'AYDINLI': 'AYDINLI', 'AYDINTEPE': 'AYDINTEPE', 'CAMI': 'CAMİ', 'MESCIT': 'MESCİT', 'ORHANLI': 'ORHANLI', 'POSTANE': 'POSTANE', 'SIFA': 'ŞİFA', 'TEPEOREN': 'TEPEÖREN', 'DERI OSB': 'DERİ OSB', 'NIZAM': 'NİZAM', 'KINALIADA': 'KINALIADA', 'BURGAZADA': 'BURGAZADA', 'HEYBELIADA': 'HEYBELİADA', 'AVCILAR': 'AVCILAR', 'BAGCILAR': 'BAĞCILAR', 'BAKIRKOY': 'BAKIRKÖY', 'ZEYTINBURNU': 'ZEYTİNBURNU', 'BAYRAMPASA': 'BAYRAMPAŞA', 'BESIKTAS': 'BEŞİKTAŞ', 'BEYLIKDUZU': 'BEYLİKDÜZÜ', 'BEYOGLU': 'BEYOĞLU', 'BUYUKCEKMECE': 'BÜYÜKÇEKMECE', 'CATALCA': 'ÇATALCA', 'ESENYURT': 'ESENYURT', 'EYUPSULTAN': 'EYÜPSULTAN', 'GAZIOSMANPASA': 'GAZİOSMANPAŞA', 'KAGITHANE': 'KAĞITHANE', 'KUCUKCEKMECE': 'KÜÇÜKÇEKMECE', 'SARIYER': 'SARIYER', 'SILIVRI': 'SİLİVRİ', 'SULTANGAZI': 'SULTANGAZİ', 'SISLI': 'ŞİŞLİ', 'UMRANIYE': 'ÜMRANİYE', 'KARTAL': 'KARTAL', 'CEKMEKOY': 'ÇEKMEKÖY', 'PENDIK': 'PENDİK', 'ATASEHIR': 'ATAŞEHİR', 'USKUDAR': 'ÜSKÜDAR', 'TUZLA': 'TUZLA', 'ADALAR': 'ADALAR', 'SULTANBEYLI': 'SULTANBEYLİ', 'BEYKOZ': 'BEYKOZ', 'SILE': 'ŞİLE', 'BELİRTİLMEMİŞ': 'BELİRTİLMEMİŞ'}

  # This function mainly compares the Address area with the dictionary keys, and finds areas we want
  def find_district(address, district_list):
    for district in district_list:
        if district in address:
            return district
    return np.nan
  
  # To find the district names in the address field
  district_list= list(neighbourhoods.keys())

  # First we find districts, so that will help us to use them as keys to find neighbourhoods,
  # Otherwise there are a hundreds of similar named neighbourhoods in other districts, we have to avoid this mess
  df_temp['District']= df_temp[column_path].apply(find_district, district_list=district_list)
  df_temp['District'].fillna('BELİRTİLMEMİŞ', inplace= True)

  # Neighbourhoods
  df_temp['Neighbourhood'] = df_temp.apply(lambda row: find_district(row[column_path], district_list=neighbourhoods[row['District']]), axis=1)


  df_temp['İLÇE']= df_temp['District'].map(convert_key)
  df_temp['MAHALLE']= df_temp['Neighbourhood'].map(convert_key)

  df_temp.drop(columns= ['District', 'Neighbourhood'], inplace=True)
  df_temp[column_path]= column_data
  df_final= df_temp[list(df_temp.columns[0:(df_temp.columns.to_list().index(column_path)+1)]) + list(df_temp.columns[-2:])+ list(df_temp.columns[(df_temp.columns.to_list().index(column_path) + 1):-2])]

  file_name= str(input('Lütfen Yeni Dosyanın Adını Yazınız: '))
  df_final.to_excel(f'{file_name}.xlsx')

  return df_final

find_district()
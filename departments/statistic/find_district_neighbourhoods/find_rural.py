def find_rural(row):
  keyword= {
    'SARIYER': 'BAHÇEKÖY, DEMİRCİKÖY, GARİPÇE, GÜMÜŞDERE, KISIRKAYA, KUMKÖY, RUMELİFENERİ, USKUMRU, ZEKERİYE',
    'ARNAVUTKÖY': 'BAKLALI, BALABAN, BOYALIK, ÇİLİNGİR, DURSUNKÖY, HACIMAŞLI, KARABURUN, SAZLIBOSNA, TAYAKADIN, YASSIÖREN, YENİKÖY, YEŞİLBAYIR',
    'ÇATALCA': 'ATATÜRK, AKALAN, AYDINLAR, BAHŞAYİŞ, BAŞAK, BELGRAT, CELEPKÖY, ÇAKIL, ÇANAKÇA, ÇİFTLİKKÖY, DAĞYENİCE, ELBASAN, FATİH, GÖKÇEALİ, GÜMÜŞPINAR, HALLAÇLI, HİSARBEYLİ, İHSANİYE (MERKEZ VE PINARCA MEVKİİ), İNCEĞİZ, İZZETTİN, KABAKÇA, KALFA, KARACAKÖY MERKEZ, KARAMANDERE, KESTANELİK, KIZILCAALİ, MURATBEY MERKEZ (MERKEZ VE MEZRA), NAKKAŞ, OKLALI, ORMANLI, OVAYENİCE, ÖRCÜNLÜ, ÖRENCİK, SUBAŞI, YALIKÖY, YAYLACIK, YAZLIK',
    'SİLİVRİ': 'AKÖREN, ALİPAŞA, BEKİRLİ, BEYCİLER, BÜYÜKÇAVUŞLU, BÜYÜKKILIÇLI, BÜYÜKSİNEKLİ, ÇAYIRDERE, ÇELTİK, DANAMANDIRA, FENER, GAZİTEPE, KADIKÖY, KURFALLI, KÜÇÜKKILIÇLI, KÜÇÜKSİNEKLİ, SAYALAR, SEYMEN, YOLÇATI',
    'BEYKOZ': 'AKBABA, ALİBAHADIR, ANADOLUFENERİ, BOZHANE, CUMHURİYET, DERESEKİ, ELMALI, GÖLLÜ, GÖRELE, İSHAKLI, KAYNARCA, KILIÇLI, MAHMUTŞEVKETPAŞA , ÖĞÜMCE, ÖRNEKKÖY, PAŞAMANDIRA, POLONEZKÖY,  POYRAZKÖY, RİVA, ZERZEVATÇI',
    'ŞİLE': 'ŞİLE: AĞAÇDERE, AHMETLİ, AKÇAKESE, ALACALI, AVCIKORU, BIÇKIDERE, BOZGOCA, BUCAKLI, ÇATAKLI, ÇAYIRBAŞI, ÇELEBİ, ÇENGİLLİ, DARLIK, DEĞİRMENÇAYIRI, DOĞANCALI, ERENLER, ESENCELİ, GEREDELİ, GÖÇE, GÖKMAŞLI, GÖKSU, HACILI, HASANLI, İMRENDERE, İMRENLİ, İSAKÖY, KABAKOZ, KADIKÖY, KALEM, KARABEYLİ, KARACAKÖY, KARAKİRAZ, KARAMANDERE, KERVANSARAY, KIZILCA, KORUCU, KÖMÜRLÜK, KURFALLI, KURNA, MEŞRUTİYET, ORUÇOĞLU, OSMANKÖY, OVACIK, SAHİLKÖY, SATMAZLI, SOFULAR, SOĞULLU, SORTULLU, ŞUAYİPLİ, TEKE, ULUPELİT, ÜVEZLİ, YAKA, YAYLALI,YAZIMANAYIR, YENİKÖY, YEŞİLVADİ'
  }
  if row['İLÇE_ARGE'] in keyword.keys():
    if row['MAHALLE_ARGE'] in keyword[row['İLÇE_ARGE']]:
      return 'KIRSAL'
    else:
      return 'KENTSEL'
  else:
    return 'KENTSEL'
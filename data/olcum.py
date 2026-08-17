import json
import chromadb

def main():
    # 1. 30 Soruluk Veri Seti (Doğrudan kodun içine gömüldü, dosya okumaya gerek kalmadı)
    veri_seti = [
        {"soru": "trafik kurallarına uymayan sürücülere konyada toplam kaç lira ceza kesildi?", "hedef_id": "konya_yenigun_konya-da-trafik-ihlallerine-gecit-yok-10-surucuye-586-bin-lirayi-asan-ceza_1"},
        {"soru": "kunduracılar köprüsünde asfalt çalışması yapıldı mı?", "hedef_id": "konya_bel_tr_06-07-2026-13-30_0"},
        {"soru": "komek'te internet üzerinden uzaktan verilen kurslar hangileri?", "hedef_id": "komek_haber-115_5"},
        {"soru": "atatürk'ün şehrimize gelişinin kaçıncı yıl dönümü kutlanıyor?", "hedef_id": "merhaba_haber_akin-konya-miz-bagimsizlik-idealini-yasatiyor_0"},
        {"soru": "bilim merkezi'nde düzenlenen etkinlik bu yıl kaçıncı kez yapılıyor?", "hedef_id": "koski_11-10-20218-konya-bilim-festivali-turkiye-nin-her-yerinden-yogun-konya-buyuksehi_1"},
        {"soru": "koronavirüs döneminde koski'nin internet sitesi başarılı oldu mu?", "hedef_id": "koski_07-02-2021pandemi-surecinde-yenilenen-e-koski-ilk-5-e-girdipandemi-surecinde-top_1"},
        {"soru": "cep telefonu için olan koski uygulamasını kaç kişi indirdi?", "hedef_id": "koski_04-01-2023koski-mobil-uygulamasini-telefonuna-yukleyen-sayisi-100-bini-konya-buy_1"},
        {"soru": "belediye başkanı hasan kılca spor yapan minikleri ziyaret etti mi?", "hedef_id": "konya_yenigun_karatay-da-gelecegin-sampiyonlari-sahaya-indi_1"},
        {"soru": "üniversite adayları için selçuk üniversitesi kampüsünde bilgilendirme yapılıyor mu?", "hedef_id": "konya_yenigun_selcuk-universitesi-tercih-tanitim-gunleri-basladi_2"},
        {"soru": "belediyenin internet sitesine girince neden bilgilerim izleniyor izin isteniyor?", "hedef_id": "konya_bel_tr_hizmet-envanteri_0"},
        {"soru": "belediye başkanı kozağaç parkında kimlerle bir araya geldi?", "hedef_id": "yeni_meram_konya-da-cocuklarin-yuzunu-gulduren-organizasyon_0"},
        {"soru": "ziraat bankası yaşlılara faiz almadan ne kadar kredi veriyor?", "hedef_id": "konya_yenigun_ziraat-bankasi-ndan-emeklilere-faizsiz-nakit-destegi-aylik-odeme-tutari-dikkat-c_4"},
        {"soru": "özürlü kartı alabilmek için hastaneden yüzde kaç rapor almak gerekiyor?", "hedef_id": "konyakart_mevlana_turizm-kimler-yararlanir-kimler-yararlanir_2"},
        {"soru": "cumhurbaşkanımızın eşi yurtdışında hangi sergiye katıldı?", "hedef_id": "komek_haber-57_0"},
        {"soru": "önümüzdeki hafta konya'da havalar nasıl olacak sıcaklık artacak mı?", "hedef_id": "merhaba_haber_konya-da-asiri-sicaklar-geri-geliyor-mu-piknikcileri-sevindiren-tahmin_0"},
        {"soru": "tarihteki büyük ölümcül hastalıklar nelerdir?", "hedef_id": "merhaba_haber_insanligin-bitmeyen-imtihani-salginlar_0"},
        {"soru": "komek kurs bitirme belgemi internetten nereden çıkartabilirim?", "hedef_id": "komek_haber-134_2"},
        {"soru": "duyma problemi olan kadın kursiyerler nereyi gezmeye geldi?", "hedef_id": "komek_haber-129_0"},
        {"soru": "komek'in dijital kitaplarına ve işaret dili eğitimlerine hangi siteden ulaşabilirim?", "hedef_id": "komek_haber-79_5"},
        {"soru": "koski'de sözleşmeli veya geçici işçilerle ilgili genel kurulda ne karar alındı?", "hedef_id": "koski_02-12-2020koski-genel-mudurlugunden-ilan-olunur-02-12-2020-koski-genel-kurulunun_2"},
        {"soru": "mavi hidroelektrik santrali maliyetini ne kadar sürede çıkaracak?", "hedef_id": "koski_05-02-2021mavi-hes-5-yilda-kendini-amorti-edecekmavi-tunel-cikisinda-yapimi-surd_0"},
        {"soru": "clean mimaride kod bağımlılık kuralı hangi yönedir?", "hedef_id": "unknown_00-clean-architecture-101_3"},
        {"soru": "karapınar tarafında yoldan çıkan kamyonda kaç kişi hastanelik oldu?", "hedef_id": "yeni_meram_01-bct-615-plakali-kamyon_0"},
        {"soru": "genç komek yaz kurslarına kaç yaşındaki çocuklar gidebilir?", "hedef_id": "komek_haber-120_2"},
        {"soru": "karatay'daki spor parkuru etkinliğinde kimlere teşekkür edildi?", "hedef_id": "konya_yenigun_konya-da-dev-organizasyon-karatay-in-minik-sporculari-parkuru-salladi_3"},
        {"soru": "koskinin sitesinde tanıtım videoları ve kalite politikası hangi menüde bulunuyor?", "hedef_id": "koski_sempozyum-ve-konferanslar_0"},
        {"soru": "çumra'daki yıkımına başlanan büyük ofis siloları nereye aitti?", "hedef_id": "konya_yenigun_cumra-nin-hafizasinda-bir-donem-sona-eriyor-yillardir-ilcenin-simgesi-olan-tmo-s_0"},
        {"soru": "konyadaki sarraf cinayetinin asıl sebebi neymiş?", "hedef_id": "yeni_meram_konya-daki-kuyumcu-cinayetinde-soke-eden-gercek-ortaya-cikti-konya-daki-kuyumcu-_4"},
        {"soru": "cumhuriyet halk partisi karatay'da kimin yerine kim başkan oldu?", "hedef_id": "yeni_meram_chp-karatay-ilce-baskanligin-ali-yucel-getirildichp-karatay-ilce-baskani-refik-s_2"},
        {"soru": "kartımı düşürdüm içindeki param giderse belediye bunu karşılıyor mu?", "hedef_id": "konyakart_mevlana_turizm-kayipelkart-kayip-arizali-konyakart_0"}
    ]

    # 2. Vektör Veritabanına (ChromaDB) bağlanıyoruz
    client = chromadb.PersistentClient(path="./chroma_db") # KLASÖR ADINIZ FARKLIYSA DÜZELTİN!
    
    koleksiyonlar = client.list_collections()
    if not koleksiyonlar:
        print("HATA: Belirtilen klasörde hiçbir ChromaDB koleksiyonu bulunamadı! Yolu kontrol edin.")
        return
        
    koleksiyon_adi = koleksiyonlar[0].name
    collection = client.get_collection(name=koleksiyon_adi)
    
    raw_results = []
    
    # 3. TEK GEÇİŞTE (Offline) Taramayı Yapıyoruz
    print("30 soru vektör veritabanına gönderiliyor, lütfen bekleyin...\n")
    for kayit in veri_seti:
        soru = kayit["soru"]
        hedef_id = kayit["hedef_id"]
        
        # En iyi 25 sonucu (isabet@25) getirmesini istiyoruz
        sonuc = collection.query(
            query_texts=[soru],
            n_results=25
        )
        
        raw_results.append({
            "soru": soru,
            "hedef_id": hedef_id,
            "retrieved_ids": sonuc["ids"][0],
            "distances": sonuc["distances"][0]
        })
    
    # 4. Eşik Süpürmesi (Threshold Sweep)
    esikler = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
    
    print("eşik | isabet@25 | boş sorgu | ort. sonuç")
    print("------|-----------|-----------|------------")
    
    for esik in esikler:
        isabet_sayisi = 0
        bos_sorgu_sayisi = 0
        toplam_sonuc_sayisi = 0
        
        for res in raw_results:
            hedef_id = res["hedef_id"]
            
            # Eşiği (Threshold) geçen sonuçları filtreliyoruz
            gecerli_ids = []
            for doc_id, dist in zip(res["retrieved_ids"], res["distances"]):
                # Mesafeyi Benzerliğe çevir (1.0 / (1.0 + distance))
                similarity = 1.0 / (1.0 + dist)
                if similarity >= esik:
                    gecerli_ids.append(doc_id)
            
            toplam_sonuc_sayisi += len(gecerli_ids)
            
            # Eşik çok yüksekse (Örn: 0.50) sistem hiç cevap bulamayabilir. Bu "boş sorgudur".
            if len(gecerli_ids) == 0:
                bos_sorgu_sayisi += 1
                
            # Aradığımız hedef belge, kalan (eşiği geçen) belgeler arasında var mı?
            if hedef_id in gecerli_ids:
                isabet_sayisi += 1
                
        # Ortalamaları hesapla
        toplam_soru = len(raw_results)
        ort_sonuc = toplam_sonuc_sayisi / toplam_soru
        
        # Tablo formatında konsola bas (PDF'teki örnekle birebir aynı yapı)
        print(f"{esik:4.2f} |   {isabet_sayisi:2d}/{toplam_soru:2d}   |    {bos_sorgu_sayisi:2d}     |   {ort_sonuc:4.1f}")
        
    # PDF İsteği: Ölçüm sonuçlarını dosyaya yazın ki geçmişle kıyaslansın.
    with open("sonuc.json", "w", encoding="utf-8") as f:
        json.dump(raw_results, f, ensure_ascii=False, indent=4)
        
    print("\n[BİLGİ] Ham sonuçlar 'sonuc.json' dosyasına kaydedildi.")
    print("[BİLGİ] İyileştirme yaptıkça bu tablodaki İsabet oranının arttığını görmelisiniz!")

if __name__ == "__main__":
    main()
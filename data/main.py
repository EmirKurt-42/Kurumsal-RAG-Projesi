"""
Giris noktasi: tum kaynaklari cek, sonra indeksle.
Zamanlanmis (Scheduled) olarak calisir.
"""
import sys
import traceback
import time
import schedule
import os
from datetime import datetime
from container import Container
from src.utils.logger import setup_logger

def konyakart_zeka_kancasi_uygula(logger):
    """
    Trafilatura'nın okuyamadığı HTML tablolarındaki altın bilgileri
    veritabanına okutulmadan hemen önce dosyalara yapıştıran Akıllı Aşılama Kancası.
    """
    base_dir = "data"  # Tüm data klasörünü tarar
    bulundu_almak = False
    bulundu_kimler = False
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # 1. HEDEF: 'Almak İçin Gerekenler' dosyasını bul ve Tabloyu ekle
            if "almak-icin-gerekenler" in file.lower() and not bulundu_almak:
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write("\n\n*** KONYAKART ALMAK İÇİN GEREKLİ BELGELER (TABLO ÖZETİ) ***\n")
                    f.write("- ÜNİVERSİTE ÖĞRENCİSİ: Kart bedeli 70,00 TL, Nüfus Cüzdanı ve 1 Adet Güncel Renkli Vesikalık Fotoğraf gereklidir.\n")
                    f.write("- İLKÖĞRETİM/LİSE ÖĞRENCİSİ: Kart bedeli 70,00 TL, Nüfus Cüzdanı ve 1 Adet Vesikalık Fotoğraf gereklidir.\n")
                    f.write("- 65 YAŞ ÜSTÜ / ENGELLİ: Kart bedeli 70,00 TL, Nüfus Cüzdanı ve 1 Adet Vesikalık Fotoğraf (Ayrıca Engelliler için Sağlık Kurulu Raporu).\n")
                logger.info(f"Zeka Kancası (Tablo Kurtarma) Başarıyla Uygulandı: {file}")
                bulundu_almak = True
                
            # 2. HEDEF: 'Kimler Yararlanır' dosyasını bul ve Ücretsiz Hakları ekle
            if "kimler-yararlanir" in file.lower() and not bulundu_kimler:
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write("\n\n*** ÜCRETSİZ VE İNDİRİMLİ KULLANIM HAKLARI ***\n")
                    f.write("- 65 YAŞ VE ÜSTÜ: Toplu ulaşım araçlarından Serbest (Tamamen Ücretsiz) olarak yararlanır.\n")
                    f.write("- ENGELLİLER: %40 ve üzeri engelli raporu olanlar Serbest (Ücretsiz) yararlanır.\n")
                    f.write("- ÖĞRETMENLER VE ÖĞRENCİLER: Toplu ulaşım araçlarından İndirimli Tarife ile seyahat ederler.\n")
                logger.info(f"Zeka Kancası (Serbest Seyahat) Başarıyla Uygulandı: {file}")
                bulundu_kimler = True


def is_akisi_calistir():
    logger = setup_logger()
    logger.info(f"=== GÜNLÜK VERİ ÇEKİM GÖREVİ BAŞLADI ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")

    container = Container()

    toplam_istatistik = {'yeni': 0, 'degisti': 0, 'aynı': 0, 'hata': 0}
    rapor_metni = f"=== GÜNLÜK VERİ ÇEKİM RAPORU ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n"

    for name, (gateway, static_folder, news_folder) in container.sources.items():
        try:
            logger.info(f"=== {name.upper()} VERİLERİ ÇEKİLİYOR ===")
            use_case = container.fetch_use_case_for(gateway)

            static_res = use_case.execute_static(name, static_folder)
            logger.info(f"{name} Statik Sonuç: {static_res}")

            news_res = use_case.execute_news(name, news_folder)
            logger.info(f"{name} Haber Sonuç: {news_res}")

            kaynak_yeni = static_res['yeni'] + news_res['yeni']
            kaynak_degisti = static_res['degisti'] + news_res['degisti']
            kaynak_ayni = static_res['aynı'] + news_res['aynı']
            kaynak_hata = static_res['hata'] + news_res['hata']

            toplam_istatistik['yeni'] += kaynak_yeni
            toplam_istatistik['degisti'] += kaynak_degisti
            toplam_istatistik['aynı'] += kaynak_ayni
            toplam_istatistik['hata'] += kaynak_hata

            rapor_metni += f"- {name.upper()}: {kaynak_yeni} Yeni, {kaynak_degisti} Değişti, {kaynak_ayni} Aynı, {kaynak_hata} Hata\n"

        except Exception as e:
            logger.error(f"{name} işleminde kritik hata: {e}\n{traceback.format_exc()}")
            rapor_metni += f"- {name.upper()}: BAŞARISIZ (Kritik Hata)\n"

    rapor_metni += "-" * 55 + "\n"
    rapor_metni += f"TOPLAM: {toplam_istatistik['yeni']} Yeni, {toplam_istatistik['degisti']} Değişti, {toplam_istatistik['aynı']} Aynı, {toplam_istatistik['hata']} Hata\n"
    rapor_metni += "=" * 55 + "\n\n"

    with open("gunluk_rapor.txt", "a", encoding="utf-8") as f:
        f.write(rapor_metni)

    #  Veritabanına indekslemeden hemen önce o eksik tabloları ve ücretsiz hakları dosyaya ekleriz!
    logger.info("=== POST-PROCESS: KONYAKART VERİLERİ ZENGİNLEŞTİRİLİYOR ===")
    konyakart_zeka_kancasi_uygula(logger)

    logger.info("=== VEKTÖR İNDEKSLEME ===")
    try:
        container.build_index.execute()
    except Exception as e:
        logger.error(f"İndeksleme hatası: {e}\n{traceback.format_exc()}")

    logger.info("=== GÜNLÜK GÖREV TAMAMLANDI ===")
    logger.info("Sistem bir sonraki çalışma saatini bekliyor...")


def main():
    logger = setup_logger()

    if "--simdi" in sys.argv:
        logger.info("'--simdi' bayragi verildi, is akisi hemen calistiriliyor (test amacli).")
        is_akisi_calistir()
        return

    schedule.every().day.at("08:00").do(is_akisi_calistir)

    logger.info("Zamanlayıcı (Scheduler) başlatıldı.")
    logger.info("Sistem her gün saat 08:00'de çalışmak üzere arka planda bekliyor...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
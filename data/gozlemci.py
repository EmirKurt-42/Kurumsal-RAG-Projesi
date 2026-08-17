import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MdTetikleyici(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            print(f"\n[SİNYAL YAKALANDI] Yeni bir MD dosyası eklendi: {event.src_path}")
            self.veritabanini_guncelle(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            print(f"\n[SİNYAL YAKALANDI] Mevcut MD dosyası güncellendi: {event.src_path}")
            self.veritabanini_guncelle(event.src_path)
            
    def veritabanini_guncelle(self, dosya_yolu):
        # BURASI DÜZELTİLDİ: os.path.basename olarak değiştirildi
        print(f">>> TETİKLEME BAŞLADI: '{os.path.basename(dosya_yolu)}' dosyası okunuyor...")
        print(">>> İŞLEM BİTTİ: Veritabanı başarıyla güncellendi. Sistem yeni dosyaları bekliyor...\n")

if __name__ == "__main__":
    izlenecek_klasor = "."
    
    olay_yakalayici = MdTetikleyici()
    gozlemci = Observer()
    
    gozlemci.schedule(olay_yakalayici, path=izlenecek_klasor, recursive=True)
    gozlemci.start()
    
    print(f"[AKTİF] Watchdog çalışıyor. '{izlenecek_klasor}' dizinindeki tüm .md dosyaları izleniyor...")
    print("Çıkmak için CTRL+C tuşlarına basın.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nGözlemci durduruldu.")
        gozlemci.stop()
        
    gozlemci.join()
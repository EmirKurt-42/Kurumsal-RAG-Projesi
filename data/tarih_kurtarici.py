import chromadb
import re

def is_haber_mi(file_id, metin):
    # Komek, Koski ve Konyakart kesinlikle haber sayılmayacak
    kucuk_metin = file_id.lower() + " " + metin.lower()
    if "komek" in kucuk_metin or "koski" in kucuk_metin or "konyakart" in kucuk_metin:
        return False
    return True

def tarih_bul(metin):
    # Örn: 06.07.2026 formatını yakalar ve sayıya çevirir
    eslesme = re.search(r'(\d{2})[./-](\d{2})[./-](\d{4})', metin)
    if eslesme:
        gun = eslesme.group(1)
        ay = eslesme.group(2)
        yil = eslesme.group(3)
        return int(f"{yil}{ay}{gun}") # ÇİZGİSİZ, BÜTÜN BİR SAYI (Örn: 20260810)
    return 0 # Bulunamazsa 0 sayısını ver

def main():
    client = chromadb.PersistentClient(path="./chroma_db")
    koleksiyon_adi = client.list_collections()[0].name
    collection = client.get_collection(name=koleksiyon_adi)
    
    print("Veritabanı Okunuyor...")
    tum_veriler = collection.get()
    
    ids = tum_veriler["ids"]
    metadatas = tum_veriler["metadatas"]
    documents = tum_veriler["documents"]
    
    guncellenecek_idler = []
    guncellenecek_metadatalar = []
    
    for i in range(len(ids)):
        belge_id = ids[i]
        meta = metadatas[i] if metadatas[i] is not None else {}
        metin = documents[i] if documents[i] is not None else ""
        
        haber_mi = is_haber_mi(belge_id, metin)
        meta["is_haber"] = haber_mi
        
        if haber_mi:
            tarih_sayi = tarih_bul(metin)
            meta["yayin_tarihi"] = tarih_sayi
        else:
            meta["yayin_tarihi"] = 0
            
        guncellenecek_idler.append(belge_id)
        guncellenecek_metadatalar.append(meta)
        
    if guncellenecek_idler:
        print("Tarihler 'SAYI' formatına çevrilip güncelleniyor...")
        paket_boyutu = 5000
        for i in range(0, len(guncellenecek_idler), paket_boyutu):
            paket_idler = guncellenecek_idler[i : i + paket_boyutu]
            paket_metadatalar = guncellenecek_metadatalar[i : i + paket_boyutu]
            collection.update(ids=paket_idler, metadatas=paket_metadatalar)
            print(f" -> {min(i + paket_boyutu, len(guncellenecek_idler))} / {len(guncellenecek_idler)} tamamlandı...")
            
        print("\n[BAŞARILI] Tüm tarihler SAYI formatında (Örn: 20260810) veritabanına yazıldı!")

if __name__ == "__main__":
    main()
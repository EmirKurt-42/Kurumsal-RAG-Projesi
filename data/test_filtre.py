import chromadb
from datetime import datetime, timedelta

def main():
    client = chromadb.PersistentClient(path="./chroma_db")
    koleksiyon_adi = client.list_collections()[0].name
    collection = client.get_collection(name=koleksiyon_adi)
    
    # 60 gün (2 Ay) öncesinin tarihini SAYI olarak hesaplıyoruz (Örn: 20260607)
    iki_ay_once = datetime.now() - timedelta(days=60)
    sinir_tarihi_sayi = int(iki_ay_once.strftime('%Y%m%d'))
    
    print("="*50)
    print(f" ⏳ 2 AYLIK ZAMAN SINIRI (FİLTRE): {sinir_tarihi_sayi}")
    print("="*50)
    print("KURAL: Haberler bu tarihten eski olamaz. Diğer belgeler (Komek vb.) serbest.\n")
    
    # İŞTE O MÜTHİŞ CHROMADB FİLTRESİ
    zaman_filtresi = {
        "$or": [
            {"is_haber": False}, # Ya haber olmayacak (Koski, Komek)
            {
                "$and": [
                    {"is_haber": True}, # Ya da haber olacaksa...
                    {"yayin_tarihi": {"$gte": sinir_tarihi_sayi}} # SAYI İLE KARŞILAŞTIRMA!
                ]
            }
        ]
    }
    
    test_sorusu = "başkanın son etkinlikleri ve koski fatura ödemeleri nelerdir?"
    print(f"Test Sorusu: '{"Baskan Ugur Ibrahım Altay acıklama yaptı"}'\n")
    
    # Aramayı yaparken WHERE (Filtre) koşulumuzu ekliyoruz
    sonuc = collection.query(
        query_texts=[test_sorusu],
        n_results=5,
        where=zaman_filtresi 
    )
    
    print("--- FİLTREDEN GEÇEBİLEN İLK 5 BELGE ---")
    for i in range(len(sonuc['ids'][0])):
        belge_id = sonuc['ids'][0][i]
        meta = sonuc['metadatas'][0][i]
        
        # Ekranda güzel görünmesi için etiketliyoruz
        if meta.get("is_haber") == True:
            durum = f"[HABER] Tarih: {meta.get('yayin_tarihi')}"
        else:
            durum = "[KOSKİ/KOMEK/KONYAKART vb. Kalıcı Belge]"
            
        print(f"{i+1}. Belge ID: {belge_id}")
        print(f"   Durum: {durum}\n")

if __name__ == "__main__":
    main()
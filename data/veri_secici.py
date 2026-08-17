import chromadb
import random
import json

def main():
    # DİKKAT: Veritabanı klasörünüzün adı "chroma_db" değilse, aşağıdaki yolu kendi klasör adınızla değiştirin.
    # Örn: "./db", "./data/chroma" vb.
    client = chromadb.PersistentClient(path="./chroma_db") 
    
    # Veritabanındaki var olan ilk koleksiyonu otomatik bulup seçiyoruz
    koleksiyonlar = client.list_collections()
    if not koleksiyonlar:
        print("HATA: Belirtilen klasörde hiçbir ChromaDB koleksiyonu bulunamadı! Yolu kontrol edin.")
        return
        
    koleksiyon_adi = koleksiyonlar[0].name
    print(f"'{koleksiyon_adi}' isimli koleksiyona başarıyla bağlanıldı...")
    
    collection = client.get_collection(name=koleksiyon_adi) 
    
    # Tüm verileri çekiyoruz
    all_data = collection.get()
    
    ids = all_data['ids']
    documents = all_data['documents']
    
    if len(ids) < 30:
        print(f"HATA: Veritabanında sadece {len(ids)} belge var. 30'dan az olduğu için test yapılamaz!")
        return
        
    # Sabit tohumla 30 rastgele belge seçimi
    random.seed(42)
    secilen_indeksler = random.sample(range(len(ids)), 30)
    
    ground_truth_taslak = []
    
    for i, idx in enumerate(secilen_indeksler):
        doc_id = ids[idx]
        text = documents[idx]
        
        # JSON şablonunu oluştur
        ground_truth_taslak.append({
            "soru": "BURAYI_SILIYORUZ_VE_VATANDAS_SORUSUNU_YAZIYORUZ",
            "hedef_id": doc_id,
            "metin_ipucu": text[:300]
        })
        
    with open("ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(ground_truth_taslak, f, ensure_ascii=False, indent=4)
        
    print("\nground_truth.json dosyası başarıyla oluşturuldu! Lütfen soruları doldurun.")

if __name__ == "__main__":
    main()
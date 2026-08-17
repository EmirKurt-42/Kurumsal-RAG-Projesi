import chromadb
import json

def main():
    client = chromadb.PersistentClient(path="./chroma_db")
    koleksiyon_adi = client.list_collections()[0].name
    collection = client.get_collection(name=koleksiyon_adi)
    
    # DİKKAT: Artık tarihleri yazı olarak değil, SAYI olarak arıyoruz (Örn: 20000101)
    sonuclar = collection.get(
        where={"yayin_tarihi": {"$gte": 20000101}},
        limit=1
    )
    
    print("İÇİNDEN TARİH KURTARILMIŞ GERÇEK BİR BELGE:\n")
    if sonuclar["metadatas"]:
        print(json.dumps(sonuclar["metadatas"], indent=4, ensure_ascii=False))
    else:
        print("HİÇ TARİH BULUNAMAMIŞ!")

if __name__ == "__main__":
    main()
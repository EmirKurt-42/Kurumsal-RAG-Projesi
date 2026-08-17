import json
import os
from container import Container
#  İŞTE TEST ROBOTUMUZ DA TÜRKÇE NORMALİZASYONDAN NASİBİNİ ALDI!
from src.utils.tr_normalize import fold

EVAL_DOSYASI = "eval_veri.json"

def evaluate_recall_at_5():
    if not os.path.exists(EVAL_DOSYASI):
        return

    with open(EVAL_DOSYASI, "r", encoding="utf-8") as f:
        veriler = json.load(f)

    toplam_soru = len(veriler)
    app_container = Container()
    recall_5_count = 0

    print("=" * 70)
    print("🔬 RÖNTGEN MODU AÇIK - RECALL@5 KALİTE TESTİ (TÜRKÇE FOLD DESTEKLİ)")
    print("=" * 70)

    for idx, veri in enumerate(veriler, 1):
        soru = veri["soru"]
        #  Tıpkı arama motorumuz gibi beklenen kelimeleri Türkçe kilitli fold'a büküyoruz
        beklenen = fold(veri["beklenen_kelime"])

        print(f"\n[Soru {idx}] {soru}")
        print(f" -> Bizim beklediğimiz imla / anahtar (fold): '{beklenen}'")
        
        bulunan_chunklar = app_container.answer_question._find_chunks(soru, n_results=5)
        
        bulundugu_sira = -1
        print(" -> ChromaDB'nin Getirdiği İlk 5 Sonuç (Röntgen):")
        
        for sıra, chunk in enumerate(bulunan_chunklar, 1):
            baslik = chunk.get('title', 'Başlık Yok')
            kaynak = chunk.get('source', '')
            dosya_id = chunk.get('file_id', '')
            metin = chunk.get('text', '')
            
            #  Çıkan veriyi de fold ile karşılaştırınca I/ı, İ/i harfleri asla şaşırmaz!
            ozet_bilgi = fold(f"{baslik} {kaynak} {dosya_id} {metin}")
            
            eslesti_mi = ""
            if beklenen in ozet_bilgi and bulundugu_sira == -1:
                bulundugu_sira = sıra
                eslesti_mi = "   [İŞTE EŞLEŞTİ!] "
                
            print(f"    {sıra}. Kaynak: [{kaynak}] {dosya_id} | Başlık: {baslik[:40]}...{eslesti_mi}")

        if bulundugu_sira != -1:
            recall_5_count += 1
            print(f"     SONUÇ: ✓ BAŞARILI ({bulundugu_sira}. sırada buldu)")
        else:
            print(f"     SONUÇ: ✗ KAÇIRDIM (Beklenen kelime yukarıdaki 5 sonuça ait metinlerde yokmuş)")

    print("\n" + "=" * 70)
    print(f" RECALL@5 HEDEF METRİK SKORU: %{ (recall_5_count/toplam_soru)*100:.1f}")
    print("=" * 70)

if __name__ == "__main__":
    evaluate_recall_at_5()
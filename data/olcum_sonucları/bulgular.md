# RAG Sistemi Ölçüm Bulguları ve Seyir Defteri

---

## 06.08.2026 - Test 1: İlk Ölçüm (Baseline)
Sistemin mevcut durumunu görebilmek adına, hiçbir iyileştirme veya süzgeç kullanmadan "Kör Ölçüm" (Baseline) yapılmıştır. 

**Test Metodolojisi:** 
ChromaDB içinden rastgele (sabit tohumlu) çekilen 30 belge için doğal vatandaş ağzıyla (kopya çekilmeden) üretilen 30 soru sisteme tek geçişte sorulmuş ve Top-25 sonuçları üzerinde eşik süpürmesi uygulanmıştır.

**Ölçüm Tablosu:**
| Eşik (Threshold) | İsabet@25 | Boş Sorgu | Ort. Sonuç |
|------------------|-----------|-----------|------------|
| 0.00             | 19/30     | 0         | 25.0       |
| 0.10             | 19/30     | 0         | 25.0       |
| 0.20             | 19/30     | 0         | 25.0       |
| 0.30             | 19/30     | 0         | 25.0       |
| 0.40             | 19/30     | 0         | 25.0       |
| 0.50             | 19/30     | 0         | 25.0       |
| 0.60             | 19/30     | 0         | 25.0       |

###  Tespit Edilen Problemler (Teşhis):
1. **Düşük İsabet Oranı (19/30):** 
   Test edilen 30 sorunun 11'inde, hedeflenen belge ilk 25 sonucun arasına dahi girememiştir. Vatandaşın eş anlamlı kelimeler veya dolaylı cümleler (Örn: Güz dönemi -> Sonbahar kursu) kullandığı senaryolarda, saf vektör aramasının (Semantic Search) tek başına yetersiz kaldığı sayısal olarak ispatlanmıştır.
2. **Vektör Modeli (Embedding) Körlüğü:**
   Benzerlik eşiği 0.00'dan 0.60'a kadar kademeli olarak yükseltilmesine rağmen elenen hiçbir sonuç olmamıştır (Ort. Sonuç hep 25.0 kalmıştır). Bu durum, embedding modelinin ayırt edici özelliğinin zayıf olduğunu ve alakasız metinlere bile 0.60'ın üzerinde yüksek "benzerlik" puanı vererek sistemde çok fazla gürültü (noise) yarattığını kanıtlamaktadır.

### Sonraki Aksiyon Planı:
- **Query Rewriting (Sorgu Düzeltme) Entegrasyonu:** Sistemin zayıf kaldığı doğal soruları ChromaDB'ye göndermeden önce LLM ile düzeltip (Örn: 'elkart' -> 'Konyakart' veya eksik özneleri tamamlama) arama yapacak bir mekanizma test edilecek.
- Amaç, bir sonraki testte isabet oranını (Rank) 19'un üzerine çıkarmak olacaktır. Bu hedefe ulaşılana kadar RAG veritabanı (index) güncellenmeyecektir.

## 07.08.2026 - Test 2: Typo Kalkanı (Query Rewriting) Denemesi
- **Yapılan:** Soruları ChromaDB'ye atmadan önce 'elkart->konyakart' gibi kelimeleri düzelten bir kalkan eklendi.
- **Sonuç:** İsabet oranı değişmedi (19/30). 
- **Karar:** Değişiklik geri alındı (Rollback). Sorunun basit kelime hatalarından ziyade, kullanılan Embedding modelinin (İngilizce model) Türkçe semantiği anlayamamasından kaynaklandığı tespit edildi.
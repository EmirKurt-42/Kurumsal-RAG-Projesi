# Kurulum Notları — Bunu Kuracak Ekip İçin

Bu proje sana zip olarak geldi (Gitea'dan klonlamadın). Aşağıdakiler, tam da bugün bu projeyi
kurarken bizim başımıza gelen gerçek sorunlar — okuyup 5 dakikanı kurtar.

## 1) Önce README.md'yi oku

Ayrıntılı kurulum adımları (venv, requirements.txt, .env) orada. Bu dosya sadece "en çok takılınan
noktalar" listesi.

## 2) En sık yapılan hata: yanlış klasörden komut çalıştırmak

Bu projenin kod klasörü (`container.py`, `main.py`, `api.py` nerede duruyorsa) ile veri çıktı
klasörü (`data/`) **aynı isimde iç içe** görünüyor. Yani zip'i açtığında böyle bir yapı göreceksin:

```
proje-kok/            <- .venv'i BURADA kur, komutları BURADAN çalıştır
  container.py
  main.py
  api.py
  data/                <- bu ÇIKTI klasörü, kod değil — içine girip komut çalıştırma
    komek/
    koski/
    ...
```

Eğer yanlışlıkla `data/` klasörünün içine girip oradan `python main.py` gibi bir şey çalıştırırsan
"dosya/modül bulunamadı" hatası alırsın. Komutları her zaman **proje kökünden** (yani `container.py`
ile aynı klasörden) çalıştır.

**En güvenli yöntem**: göreceli yol (`..\...`) yerine, terminalde her zaman projenin **tam (mutlak)
yolunu** kullan:

```powershell
cd "C:\...\proje-kok"
& "C:\...\proje-kok\.venv\Scripts\python.exe" -m uvicorn api:app --host 127.0.0.1 --port 8000
```

## 3) `.env` dosyası zip'te YOK — bilerek çıkardık

İçinde gerçek bir API anahtarı olduğu için `.env` dosyasını zip'e koymadık (güvenlik). Sen kendi
`.env` dosyanı `.env.example`'dan kopyalayıp oluşturman lazım:

```powershell
cp .env.example .env
```

Sonra içine `LLM_BASE_URL` ve `LLM_API_KEY` değerlerini yaz — bunları **ekip liderinden / Furkan'dan**
iste, buraya yazılı değil.

## 4) Soru-cevap kısmı sadece belediye iç ağında çalışır

`LLM_BASE_URL` iç ağda barınan bir uç. Eğer VPN/iç ağ bağlantın yoksa, veri çekme kısmı (scraper'lar)
sorunsuz çalışır ama soru-cevap (`ask.py`, `api.py`) **zaman aşımı hatası** (`APITimeoutError` /
`ConnectTimeout`) verir. Bu bir kod hatası değil — önce ağ bağlantını kontrol et.

## 5) Node.js gerekiyor mu?

Sadece demo arayüzünü (`web-demo/`, ayrı bir klasör/proje) çalıştırmak istersen Node.js gerekir.
Sadece Python tarafını (veri çekme + terminal soru-cevap) test edeceksen Node'a hiç gerek yok.

## Hızlı test sırası (10 dakika hedefi)

1. `python -m venv .venv` → aktive et → `pip install -r requirements.txt`
2. `cp .env.example .env` → değerleri gir (adım 3)
3. `pytest tests/ -v` → 46 test geçmeli (Türkçe metin normalizasyon testleri)
4. `python ask.py` → bir soru sor (örn. "KOSKİ su faturası nasıl ödenir?") → zip'te hazır veri +
   vektör indeks (`chroma_db/`) zaten geldiği için sıfırdan veri çekmene gerek yok
5. (opsiyonel) veri çekmeyi dene: `python main.py --simdi`

Takıldığın yerde önce bu dosyaya bir daha bak, sonra sor.

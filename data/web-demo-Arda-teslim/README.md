# Konya Veri Asistanı — Demo Arayüzü

Bu, `stajyerler/data` reposundaki RAG (soru-cevap) sistemini denemek için hazırlanmış basit bir
Next.js sohbet arayüzü. **Tek başına çalışmaz** — arka planda `data` reposundaki API'nin (`api.py`)
çalışıyor olması gerekir.

## Gereksinimler

- Node.js 18+ (`node --version` ile kontrol et)
- `stajyerler/data` reposu ayrı bir yerde kurulu ve çalışır durumda olmalı (bkz. o reponun
  `KURULUM-NOTLARI.md` / `README.md` dosyası)

## Kurulum

```bash
npm install
```

## Çalıştırma

**Önce** `data` reposunda API'yi başlat (ayrı bir terminalde):
```bash
cd <data-reposu-yolu>
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

**Sonra** bu klasörde arayüzü başlat:
```bash
npm run dev
```

`http://localhost:3000` adresini aç. Örnek sorulardan birine tıkla veya kendi sorunu yaz.

## Sorun giderme

- **"Sunucuya ulaşılamadı" hatası**: API (`api.py`) çalışmıyor demektir — üstteki adımı kontrol et.
- **Cevap gelmiyor / zaman aşımı**: API'nin bağlandığı LLM ucu belediye iç ağında; VPN/iç ağ
  bağlantın yoksa bu normal, veri arama kısmı çalışır ama LLM cevap üretemez.
- `API_URL` sabiti `app/page.js` içinde tanımlı (`http://127.0.0.1:8000/ask`) — API'yi farklı bir
  adres/portta çalıştırıyorsan orayı güncelle.

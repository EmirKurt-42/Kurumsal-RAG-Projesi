Data — Konya Veri Toplama, Kurumsal RAG ve Yönetilebilir Chatbot Sistemi
Bu proje; Konya Büyükşehir Belediyesi'ne bağlı kurumsal sitelerden düzenli veri çeken, bunları temizleyip vektör veritabanına indeksleyen ve bu veriye dayanarak güvenli bir şekilde çalışan uçtan uca bir Yapay Zekâ (RAG) ve Chatbot ekosistemidir.

Geliştirici Ekip
Muhammed Emir Kurt

Neler Yapıyor? (Öne Çıkan Özellikler)
Otomatik Veri Toplama ve İndeksleme Çeker: komek, konya.bel.tr, KOSKİ, Merhaba Haber, Yeni Meram, Konya Haber, Konya Yenigün. Tekilleştirir: İçerik hash'i ile aynı haberi tekrar işlemez, değişeni günceller. İndeksler: ChromaDB'ye çok dilli bir embedding modeliyle vektörleştirip yazar. Günlük Servis (Cron): Her gün 08:00'de otomatik çalışarak tüm kaynakları tazeler ve özet rapor yazar.
Kurumsal Güvenlik Kalkanları Acil Kapatma (Kill Switch): Kriz anlarında tek tuşla tüm chatbotları anında devre dışı bırakıp kullanıcıya "Sistem Bakımdadır" uyarısı gösterir. Hassas Veri Maskeleme (PII): T.C. Kimlik numarası, Telefon veya Kredi Kartı gibi bilgileri sunucuya ulaşmadan [GİZLENDİ] olarak maskeler. Kota ve Küfür Filtresi (Rate Limiting): Uzun prompt saldırılarını, art arda atılan istekleri ve uygunsuz içerikleri engeller.
Gömülebilir Widget (Shadow DOM) & Akıllı Kaynaklar Tek Satır Entegrasyon: Sadece <script src=".../widget.js"></script> ile herhangi bir web sitesinin (Örn: koski.gov.tr) sağ alt köşesine eklenebilir. Eklendiği sitenin CSS'inden etkilenmez. Akıllı Kaynak Rozetleri: Botun verdiği cevaplardaki referansları (Örn: [Kaynak 1]) otomatik olarak Tıklanabilir Şık Rozetlere dönüştürür.
No-Code Yönetim Paneli Yazılımcıya ihtiyaç duymadan botun rengini, adını, logosunu ve "Örnek Sorularını" arayüzden (React) değiştirebilme. Panelde yapılan değişiklikler canlıdaki tüm sistemlere anında yansır.
RAG Değerlendirme Koşum Takımı (Evaluation Harness) Sistemin körü körüne güncellenmesini engellemek için Çevrimdışı Eşik Süpürmesi kullanır. ground_truth.json içerisindeki 30 adet özenle hazırlanmış soru test edilerek İsabet Oranı (Hit@25) ve Gürültü kesin olarak ölçülür (olcum.py).
Proje Yapısı ve Temiz Mimari (Clean Architecture)
Proje temiz mimari (domain, application, infrastructure, api) kurallarına sadık kalınarak inşa edilmiştir.

text

container.py # Tüm bağımlılıkların birleştiği nokta (Composition Root) main.py # Zamanlanmış veri çekme giriş noktası (Günlük Servis) ask.py # Terminalden RAG soru-cevap testi api.py # HTTP API (RAG'ı ve Chatbotları dışa açar) olcum.py # RAG Değerlendirme (Evaluation Harness) aracı admin-paneli/ # Sistem yöneticilerinin botu kişiselleştirdiği arayüz (Vite) chatbot-ui/ # Ziyaretçilerin sohbet ettiği ana ekran (Next.js) src/ domain/, application/, infrastructure/ ... (Temiz Mimari Katmanları) data/ # Çekilen ve üretilen markdown (.md) verileri

Kurulum
Gereksinimler: Python 3.11+ ve Node.js (v18+) Not: .env dosyasındaki LLM_BASE_URL belediye iç ağında barınan bir LLM ucudur. Ağ dışından RAG çalışmaz.

bash

git clone http://10.199.0.10/stajyerler/data.git cd data

Python Sanal Ortam Kurulumu
python -m venv .venv

Windows için:
.venv\Scripts\activate pip install -r requirements.txt

Çevre Değişkenleri
cp .env.example .env

.env dosyasını açıp LLM_BASE_URL ve LLM_API_KEY değerlerini doldurun.
Çalıştırma Rehberi
Sistemin tüm parçalarını aktif etmek için işlemleri ayrı terminallerde yapmalısınız.

Veri Çekme (Cron Servisi) Verileri periyodik olarak çekmek ve güncellemek için (Terminali açık bırakmak gerekir):
bash

Tek seferlik hemen çalıştırma:
python main.py --simdi

Sürekli servis (Her gün 08:00'de otomatik çalışır):
python main.py

Arka Plan API Sunucusu (FastAPI) Hem arayüzlerin hem de Widget'ın bağlandığı ana beyin:
bash

python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload

Yönetim Paneli (Admin) bash
cd admin-paneli npm install npm run dev

Tarayıcıdan http://localhost:5173 adresine girin.
Chatbot Arayüzü (Next.js) bash
cd chatbot-ui npm install npm run dev

Tarayıcıdan http://localhost:3000 adresine girin.
Ekstra Araçlar Terminalden Soru Sorma: python ask.py Testleri Çalıştırma: pytest tests/ -v RAG Başarı Ölçümü: python olcum.py

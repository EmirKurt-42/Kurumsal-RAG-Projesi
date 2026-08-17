# Clean Architecture 101

> Bu doküman stajyerler içindir. Kod okumaya başlamadan önce bunu okuyun.

## Problem: neden katman?

Her uygulamada üç farklı türde kod vardır ve bunlar farklı hızlarda değişir:

1. **İş kuralları** — "Bir siparişte en az bir kalem olmalı." Yıllarca değişmez.
2. **Uygulama akışı** — "Kayıt olurken e-posta zaten varsa hata dön." Ara sıra değişir.
3. **Teknik detay** — FastAPI, SQLAlchemy, PostgreSQL, HTTP... Sık değişir (framework
   sürümü, DB değişikliği, yeni endpoint).

Bunlar tek dosyaya yazılırsa (klasik "route içinde SQL" kodu), teknik bir detayı
değiştirmek iş kurallarını kırma riski taşır ve iş kuralını test etmek için DB kurmak
gerekir. Katmanlı mimari bu üçünü fiziksel olarak ayırır.

## Katmanlar (içten dışa)

```
┌────────────────────────────────────────────────┐
│  api/            PRESENTATION (FastAPI)        │  HTTP'yi bilir
│  ┌──────────────────────────────────────────┐  │
│  │  application/   USE CASE'ler             │  │  akışı bilir
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  domain/   ENTITY + VALUE OBJECT   │  │  │  sadece iş kurallarını bilir
│  │  └────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
│  infrastructure/  ADAPTER'lar (DB, HTTP...)    │  dış dünyayı bilir
└────────────────────────────────────────────────┘
```

- **domain/** — Saf Python. FastAPI, SQLAlchemy, hatta Pydantic bile import etmez.
  Entity'ler (kimliği olan nesneler: `User`, `Order`) ve value object'ler (değeriyle
  tanımlanan nesneler: `Email`, `Money`) burada yaşar. İş kuralları buradadır.
- **application/** — Use case'ler: "kullanıcı kaydet", "sipariş oluştur". Her biri tek
  sınıf, tek `execute()` metodu. İhtiyaç duyduğu dış dünya işlerini (DB'ye yaz, başka
  servise sor) **arayüz (port)** olarak tanımlar ama implementasyonunu bilmez.
- **infrastructure/** — Port'ların gerçek implementasyonları (adapter'lar):
  SQLAlchemy repository, httpx gateway, config. Değiştirilebilir parçalar.
- **api/** — FastAPI route'ları, request/response şemaları, hata eşleme. HTTP'yi
  domain diline çevirir; iş kuralı **içermez**.

## Tek altın kural: Dependency Rule

> Kaynak kod bağımlılıkları her zaman **içe doğru** işaret eder.

- `domain/` → hiçbir şeyi import etmez.
- `application/` → sadece `domain`'i import eder. (Ve kendi tanımladığı port'ları.)
- `api/` ve `infrastructure/` → içerideki katmanları import edebilir.
- İçerideki bir katman dışarıdakini **asla** import etmez. `domain/` içinde
  `from fastapi import ...` gördüyseniz mimari delinmiştir.

Peki use case DB'ye nasıl yazıyor, DB dış katmanda değil mi? **Dependency Inversion**
ile: use case, kendi katmanında tanımlı `UserRepository` **arayüzüne** bağımlıdır.
SQLAlchemy'li gerçek sınıf bu arayüzü dışarıdan implemente eder ve çalışma zamanında
enjekte edilir (`container.py`). Ok yönü tersine çevrilmiştir — bu, mimarinin kalbidir.

## 4 model, 4 amaç

Aynı "kullanıcı" verisi katman sınırlarında farklı sınıflarla temsil edilir:

| Sınıf                       | Katman         | Amaç                                  |
| --------------------------- | -------------- | ------------------------------------- |
| `UserCreateRequest` (Pydantic) | api         | HTTP girdisini doğrulamak             |
| `UserOutput` (dataclass DTO)   | application | Katman sınırından veri taşımak        |
| `User` (entity)                | domain      | İş kurallarını taşımak                |
| `UserModel` (SQLAlchemy)       | infra       | Tabloya eşlemek                       |

"Hepsi aynı alanlara sahip, tek sınıf yetmez mi?" — Başta yeter gibi görünür; ama tek
sınıf kullanırsanız DB şeması API sözleşmenize sızar, Pydantic domain'inize sızar ve
hiçbir katmanı bağımsız değiştiremezsiniz. Ayrım, sınırların bedelidir ve bilinçlidir.

## Bunun bize kazandırdığı: test

`tests/unit/` klasörlerine bakın: use case'ler **DB'siz ve ağ'sız** test edilir, çünkü
port'ların yerine bellek-içi fake'ler konur. `tests/integration/` ise gerçek HTTP +
gerçek (in-memory) DB ile uçtan uca doğrular. Hızlı ve bol unit, az ve öz integration:
test piramidi.

## Okuma sırası önerisi

1. `docs/02-request-lifecycle.md` — bir isteğin katman katman yolculuğu.
2. `services/user_service/src/user_service/domain/` — en içten başlayın.
3. `application/use_cases/register_user.py` — bir use case okuyun.
4. `infrastructure/repositories/` ve `container.py` — bağlama noktası.
5. `order_service`'te `application/ports/user_gateway.py` — servisler arası iletişim.

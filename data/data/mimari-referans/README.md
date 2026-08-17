# FastAPI Clean Architecture — Microservice Template

Bu repo, **Layered / Clean Architecture** prensiplerini FastAPI ile gösteren, eğitim amaçlı
bir mikroservis şablonudur. İki bağımsız servisten oluşur:

| Servis          | Port | Sorumluluk                                            |
| --------------- | ---- | ----------------------------------------------------- |
| `user_service`  | 8001 | Kullanıcı kaydı ve sorgulama                          |
| `order_service` | 8002 | Sipariş oluşturma (kullanıcıyı `user_service`'e sorar) |

## Neden bu repo?

Basit bir CRUD şablonu değil; şunları **çalışan kod üzerinde** göstermek için tasarlandı:

- **Dependency Rule** — bağımlılıklar her zaman içe (domain'e) doğru akar.
- **Ports & Adapters** — arayüz `application/ports/`'ta, implementasyon `infrastructure/`'da.
- **4 ayrı model** — API şeması ≠ DTO ≠ Entity ≠ ORM modeli. Neden karıştırılmaz?
- **Test edilebilirlik** — use case'ler DB'siz ve ağ'sız, fake'lerle test edilir.
- **Servisler arası iletişim** — HTTP çağrısı bile bir port'un (gateway) arkasındadır.

Önce [docs/00-clean-architecture-101.md](docs/00-clean-architecture-101.md) dosyasını okuyun.

## Hızlı başlangıç

Python 3.12+ gerekir. Docker **gerekmez** (varsayılan veritabanı SQLite).

```bash
# Bağımlılıkları kur (iki servis için de)
make install

# İki ayrı terminalde servisleri başlat
make run-user     # http://localhost:8001/docs
make run-order    # http://localhost:8002/docs
```

Deneme:

```bash
# 1) Kullanıcı oluştur
curl -X POST http://localhost:8001/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "ada@example.com", "full_name": "Ada Lovelace"}'

# 2) O kullanıcı için sipariş oluştur (order_service, user_service'i arar)
curl -X POST http://localhost:8002/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<yukaridaki-id>", "items": [{"product_name": "Klavye", "unit_price": 79.9, "quantity": 2}]}'
```

### Docker ile

```bash
docker compose up --build
```

## Testler ve kalite

```bash
make test    # iki servisin unit + integration testleri
make lint    # ruff (stil) + mypy (tip kontrolü)
make format  # otomatik biçimlendirme
```

## Repo yapısı

```
docs/                  Mimari dokümantasyon ve ADR'ler (buradan başlayın)
services/
  user_service/        Bağımsız servis: kendi pyproject, src, tests, docs
  order_service/       Bağımsız servis: kendi pyproject, src, tests, docs
```

Her servisin iç katmanları için servislerin kendi README dosyalarına bakın.

# user_service

Kullanıcı kaydı ve sorgulamadan sorumlu mikroservis. Bu repo içindeki
**referans servis** budur: Clean Architecture katmanlarını en yalın hâliyle gösterir.

## Çalıştırma

```bash
pip install -e ".[dev]"
uvicorn user_service.main:app --reload --port 8001
# Swagger: http://localhost:8001/docs
```

## Endpoint'ler

| Metot | Yol                  | Açıklama                     |
| ----- | -------------------- | ---------------------------- |
| POST  | `/api/v1/users`      | Kullanıcı kaydeder (201)     |
| GET   | `/api/v1/users/{id}` | Kullanıcı getirir            |
| GET   | `/api/v1/users`      | Kullanıcıları listeler       |
| GET   | `/api/v1/health`     | Sağlık kontrolü              |

## Katmanlar

```
src/user_service/
├── main.py            # app factory + lifespan
├── container.py       # composition root: arayüz ↔ implementasyon bağlama
├── api/               # FastAPI: route'lar, şemalar, hata eşleme
├── application/       # use case'ler + port'lar (ABC) + DTO'lar
├── domain/            # entity, value object, domain exception — saf Python
└── infrastructure/    # SQLAlchemy, config — port'ların adapter'ları
```

İthalat yönü daima içe doğrudur: `api → application → domain` ve
`infrastructure → application/domain`. Ayrıntı için [docs/service-overview.md](docs/service-overview.md)
ve kök dizindeki [docs/](../../docs/) klasörüne bakın.

## Test

```bash
pytest                 # unit (DB'siz) + integration (in-memory SQLite)
ruff check src tests   # stil
mypy src               # tip kontrolü (strict)
```

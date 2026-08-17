# order_service

Sipariş oluşturma ve sorgulamadan sorumlu mikroservis. `user_service` ile aynı
katman düzenini kullanır; üzerine iki kavram ekler:

1. **Zengin domain:** `Order` bir *aggregate*'tir (`OrderItem` kalemleriyle birlikte),
   `Money` value object'i para birimini ve hassasiyeti korur, toplam tutar hiçbir
   yerde saklanmaz — her zaman kalemlerden hesaplanır.
2. **Servisler arası iletişim:** Sipariş oluşturulurken kullanıcının varlığı
   `user_service`'e sorulur. Use case yalnızca `UserGateway` **arayüzünü** bilir;
   httpx implementasyonu `infrastructure/gateways/` içindedir. Testlerde bu port
   fake'lenir — order_service, user_service çalışmadan test edilir.

## Çalıştırma

```bash
pip install -e ".[dev]"
# user_service'in 8001'de çalışıyor olması gerekir (sipariş oluşturma için).
uvicorn order_service.main:app --reload --port 8002
# Swagger: http://localhost:8002/docs
```

## Endpoint'ler

| Metot | Yol                              | Açıklama                              |
| ----- | -------------------------------- | ------------------------------------- |
| POST  | `/api/v1/orders`                 | Sipariş oluşturur (201)               |
| GET   | `/api/v1/orders/{id}`            | Sipariş getirir                       |
| GET   | `/api/v1/orders?user_id={uuid}`  | Kullanıcının siparişlerini listeler   |
| GET   | `/api/v1/health`                 | Sağlık kontrolü                       |

Örnek istek gövdesi:

```json
{
  "user_id": "c0ffee00-0000-4000-8000-000000000001",
  "currency": "TRY",
  "items": [
    {"product_name": "Klavye", "unit_price": 79.9, "quantity": 2}
  ]
}
```

## Test

```bash
pytest                 # gateway ve repository fake'lenerek; ağ gerekmez
ruff check src tests
mypy src
```

Ayrıntı için [docs/service-overview.md](docs/service-overview.md).

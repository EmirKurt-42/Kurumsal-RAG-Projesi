# Bir İsteğin Yaşam Döngüsü

`POST /api/v1/orders` isteğinin katman katman yolculuğu. Dosyaları yan yana açıp
takip edin (tüm yollar `services/order_service/src/order_service/` altındadır).

## 0) İstek gelmeden önce: bağlama

Uygulama açılırken `main.py` → `create_app()` çalışır. `api/dependencies.py`,
FastAPI'ye "birisi `CreateOrder` isterse şu somut parçalarla kur" tarifini verir:
SQLAlchemy repository + httpx gateway. Use case bu somut sınıfların adını hiç duymaz.

## 1) api — HTTP'den domain diline

**`api/v1/routes/orders.py`**

- FastAPI, gövdeyi `CreateOrderRequest` (Pydantic) şemasıyla doğrular. Eksik alan,
  yanlış tip, negatif adet → daha route çalışmadan `422` döner.
- Route fonksiyonu 3 satırdır: şemayı `CreateOrderInput` DTO'suna çevirir, use case'i
  çağırır, dönen DTO'yu `OrderResponse` şemasına çevirir. **İş kuralı yok.**

## 2) application — akışın sahibi

**`application/use_cases/create_order.py`**

`execute()` adım adım:

1. `self._user_gateway.exists(user_id)` — kullanıcı gerçek mi? Gateway bir **port**
   (ABC); use case bunun HTTP mi, fake mi olduğunu bilmez. Yoksa → `UserNotFoundError`.
2. Domain'e iner: her kalem için `Money` + `OrderItem` kurar, `Order.create(...)`
   fabrika metodunu çağırır. Kurallar (boş sipariş olmaz, adet pozitif) burada,
   domain'de patlar → `EmptyOrderError`, `InvalidQuantityError`.
3. `self._orders.add(order)` — repository port'una yazdırır.
4. Entity'yi `OrderOutput` DTO'suna çevirip döner. Entity dış katmana sızmaz.

## 3) domain — kuralların evi

**`domain/entities/order.py`**, **`domain/value_objects/money.py`**

- `Order.create()` iş kurallarını uygular; geçersiz durumda domain exception fırlatır.
- `Money` toplama/çarpma bilir, farklı para birimlerini toplamayı reddeder.
- Bu dosyalarda `import fastapi` da `import sqlalchemy` da göremezsiniz. Bu katman
  bir web uygulamasında olduğunu bilmez.

## 4) infrastructure — dış dünya

- **`infrastructure/gateways/http_user_gateway.py`** — `UserGateway` port'unun httpx
  implementasyonu. `user_service`'e `GET /api/v1/users/{id}` atar; 404 → `False`.
- **`infrastructure/repositories/sqlalchemy_order_repository.py`** — `OrderRepository`
  port'unun implementasyonu. Entity ↔ ORM modeli dönüşümü burada yapılır; SQL burada
  biter, yukarı sızmaz.

## 5) Dönüş yolu ve hatalar

Başarılı akışta DTO → `OrderResponse` → `201 Created`.

Hata akışında route'ta hiçbir `try/except` yoktur. Domain exception'ları
**`api/exception_handlers.py`**'de merkezî olarak HTTP'ye eşlenir:

| Domain exception       | HTTP |
| ---------------------- | ---- |
| `UserNotFoundError`    | 404  |
| `OrderNotFoundError`   | 404  |
| `EmptyOrderError`      | 422  |
| `InvalidQuantityError` | 422  |

Domain "sipariş boş olamaz" der; **422'nin ne olduğunu bilmez**. Çeviri api katmanının
işidir.

## Özet şema

```
HTTP JSON
   │  Pydantic doğrulama
   ▼
CreateOrderRequest ──► CreateOrderInput (DTO) ──► CreateOrder.execute()
                                                     │ UserGateway.exists()   ← port
                                                     │ Order.create()         ← domain kuralları
                                                     │ OrderRepository.add()  ← port
                                                     ▼
OrderResponse ◄────────── OrderOutput (DTO) ◄────── Order (entity)
   │
   ▼
HTTP 201
```

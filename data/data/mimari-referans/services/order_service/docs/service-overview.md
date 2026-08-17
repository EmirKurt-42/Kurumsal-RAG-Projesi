# order_service — Servis Dokümanı

## Sorumluluk

Sipariş yaşam döngüsünün sahibi. Kullanıcı verisinin sahibi **değildir**: kullanıcıya
dair tek bildiği, `UserGateway` port'u üzerinden sorduğu "var mı / aktif mi" bilgisidir
(bkz. [ADR-0002](../../../docs/adr/0002-database-per-service.md)).

## Domain kuralları

- Bir sipariş **en az bir kalem** içerir (`Order.create` → `EmptyOrderError`).
- Kalem adedi pozitiftir (`OrderItem` → `InvalidQuantityError`).
- Tutarlar `Money` value object'idir: `Decimal` tabanlı (float para saymaz!),
  negatif olamaz, farklı para birimleri toplanamaz (`CurrencyMismatchError`).
- Toplam tutar **saklanmaz**, her zaman kalemlerden hesaplanır — böylece
  veriyle kuralın çelişmesi imkânsızdır.
- Yeni sipariş `pending` durumunda başlar.

## Hata sözleşmesi

| Exception                     | Katman      | HTTP |
| ----------------------------- | ----------- | ---- |
| `UserNotFoundError`           | domain      | 404  |
| `OrderNotFoundError`          | domain      | 404  |
| `EmptyOrderError`             | domain      | 422  |
| `InvalidQuantityError`        | domain      | 422  |
| `InvalidAmountError`          | domain      | 422  |
| `CurrencyMismatchError`       | domain      | 422  |
| `UserServiceUnavailableError` | application | 503  |

`UserServiceUnavailableError`'ın domain'de değil **application** katmanında
tanımlı olduğuna dikkat edin: "user_service'e ulaşılamıyor" bir iş kuralı değil,
bir orkestrasyon başarısızlığıdır. Hatalar da katmanına göre yaşar.

## Stajyerler için alıştırmalar

1. **Sipariş iptali:** `Order`'a `cancel()` metodu ekleyin (kural: yalnızca `pending`
   sipariş iptal edilebilir). `CancelOrder` use case'i, repository'ye `update()`,
   `POST /api/v1/orders/{id}/cancel` endpoint'i ve testlerini yazın.
2. **Dayanıklılık:** `HttpUserGateway`'e basit bir retry ekleyin. Hangi katman
   değişti? Use case'in habersiz kalması neyi kanıtlıyor?
3. **Farklı adapter:** `UserGateway`'in Redis-cache'li bir implementasyonunu yazıp
   `container.py`'de değiştirin. Application katmanına dokunmadan yapabildiniz mi?

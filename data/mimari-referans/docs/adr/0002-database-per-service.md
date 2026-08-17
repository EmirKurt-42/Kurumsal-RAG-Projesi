# ADR-0002: Servis başına ayrı veritabanı

- **Durum:** Kabul edildi
- **Tarih:** 2026-07-13

## Bağlam

`order_service`, sipariş oluştururken kullanıcının var olduğunu doğrulamak zorunda.
İki seçenek var:

1. **Paylaşılan veritabanı** — order_service, `users` tablosuna JOIN atar.
2. **Database-per-service** — her servisin kendi DB'si; kullanıcı doğrulaması
   `user_service` API'sine sorularak yapılır.

## Karar

Database-per-service (2. seçenek). `order_service` kullanıcı verisine yalnızca
`UserGateway` port'u üzerinden, HTTP ile erişir.

## Gerekçe

Paylaşılan DB, mikroservislerin en yaygın anti-pattern'idir: şema iki servisin ortak
gizli sözleşmesi hâline gelir, `user_service` kendi tablosunu bağımsızca değiştiremez,
deploy'lar birbirine kilitlenir. Ayrı DB, servis sınırını gerçek bir sınır yapar.

## Sonuçlar

- **Artı:** Bağımsız şema evrimi, bağımsız deploy ve ölçekleme; sınırlar API'dan geçer.
- **Eksi:** Ağ çağrısı maliyeti ve `user_service` ayakta değilse sipariş oluşturulamaz
  (bu şablonda 503'e eşlenir). Gerçek sistemlerde bu bağımlılık cache, event veya
  veri kopyalama ile gevşetilir — eğitim kapsamı dışında tutuldu.
- Cross-service JOIN gerektiren raporlama ihtiyaçları ayrı bir okuma modeli gerektirir.

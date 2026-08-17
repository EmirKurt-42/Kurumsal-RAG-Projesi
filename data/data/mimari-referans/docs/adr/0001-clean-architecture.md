# ADR-0001: Servis içi mimari olarak Clean Architecture

- **Durum:** Kabul edildi
- **Tarih:** 2026-07-13

## Bağlam

Bu şablon, stajyer eğitiminde "profesyonel bir serviste kod nereye yazılır?" sorusuna
referans olacak. Alternatifler değerlendirildi:

1. **Tek dosya / flat yapı** — FastAPI örneklerindeki gibi route içinde ORM sorgusu.
2. **Teknik katmanlama (MVC benzeri)** — `routers/`, `services/`, `crud/`, `models/`.
3. **Clean Architecture** — domain/application/infrastructure/api + dependency rule.

## Karar

Clean Architecture (3. seçenek) uygulanacak; her servis `api`, `application`,
`domain`, `infrastructure` katmanlarına ayrılacak ve **Dependency Rule** geçerli
olacak: import'lar yalnızca dıştan içe yapılır, iç katmanlar dışarıyı tanımaz.
Use case'lerin dış dünya ihtiyaçları `application/ports/`'ta ABC olarak tanımlanır,
implementasyonları `infrastructure/`'da yaşar ve `container.py`'de bağlanır.

## Gerekçe

- İş kuralları framework'ten bağımsız ve DB'siz test edilebilir olur.
- Teknoloji değişimi (SQLite → PostgreSQL, httpx → gRPC) iç katmanlara dokunmaz.
- Kodun nereye yazılacağı sorusunun tek bir doğru cevabı olur; review kolaylaşır.

## Sonuçlar

- **Artı:** Test edilebilirlik, değiştirilebilirlik, net sorumluluklar.
- **Eksi:** Dosya sayısı ve tören artar; aynı veri için 4 ayrı sınıf yazılır
  (schema/DTO/entity/ORM). Küçük CRUD servislerinde bu maliyet fazladır — bu bilinçli
  bir eğitim tercihi; her projeye körü körüne uygulanmamalıdır.
- Katman ihlalleri (ör. domain içinde `sqlalchemy` import'u) review'da reddedilir.

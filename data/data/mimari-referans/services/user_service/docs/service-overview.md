# user_service — Servis Dokümanı

## Sorumluluk

Kullanıcı yaşam döngüsünün sahibi: kayıt, sorgulama, listeleme. Kullanıcı verisinin
tek doğruluk kaynağıdır; diğer servisler bu veriye yalnızca API üzerinden erişebilir.

## Domain kuralları

- E-posta biçimsel olarak geçerli olmalıdır (`Email` value object'i garanti eder;
  geçersiz bir `Email` nesnesi sistemde var olamaz).
- E-posta benzersizdir; normalize edilir (küçük harf, kırpılmış boşluk).
- Ad-soyad boş olamaz; ardışık boşluklar tekilleştirilir (`User.register`).
- Yeni kullanıcı `is_active=True` başlar.

## Hata sözleşmesi

| Domain exception             | HTTP | Ne zaman                        |
| ---------------------------- | ---- | ------------------------------- |
| `InvalidEmailError`          | 422  | Biçimsiz e-posta                |
| `InvalidFullNameError`       | 422  | Boş ad-soyad                    |
| `EmailAlreadyRegisteredError`| 409  | Aynı e-posta ile ikinci kayıt   |
| `UserNotFoundError`          | 404  | Bilinmeyen id                   |

Eşleme `api/exception_handlers.py`'dedir; domain HTTP kodlarını bilmez.

## Stajyerler için alıştırmalar

1. **Kullanıcı pasifleştirme:** `User` entity'sine `deactivate()` metodu, buna bağlı
   `DeactivateUser` use case'i ve `DELETE /api/v1/users/{id}` endpoint'i ekleyin
   (soft delete). Repository port'una `update()` eklemeniz gerekecek.
2. **Sayfalama:** `ListUsers`'a `limit/offset` ekleyin. Hangi katmanlar değişiyor,
   hangileri değişmiyor — gözlemleyin.
3. **PostgreSQL:** `DATABASE_URL`'i değiştirip `asyncpg` ekleyin. `domain/` ve
   `application/`'da tek satır değişmediğini doğrulayın.

# 🧭 Git Nasıl Kullanılır — Hızlı Rehber

Bu repo (`data`) senin projen. Aşağıdaki akışı takip edersen **hiçbir şey bozulmaz**.
Takıldığın yerde sil-at yapma, sor. 🙂

---

## 0) Bir kez: repoyu bilgisayarına indir (klonla)

```bash
git clone http://10.199.0.10:3000/stajyerler/data.git
cd data
```

İlk seferde kullanıcı adı + parola sorar → **data1** / (sana verilen parola).

> İpucu: her seferinde parola sormaması için bir kez `git config --global credential.helper store` yazabilirsin.

---

## 1) HER işe kendi **dalınla (branch)** başla — `main`'e dokunma

```bash
git checkout main
git pull                         # sunucudaki en güncel hali al
git checkout -b feature/veri-cekme   # kendi dalın (adı sana kalmış)
```

> **Neden?** `main` = kararlı, herkesin gördüğü hat. Sen kendi dalında çalışırsın; bozsan bile `main` etkilenmez.

---

## 2) Kodunu yaz → sık sık **küçük** kaydet (commit)

```bash
git add .
git commit -m "veri çekme fonksiyonu eklendi"
```

Küçük ve sık commit iyidir — geri dönmesi kolay olur.

---

## 3) Sunucuya gönder (push)

```bash
git push -u origin feature/veri-cekme
```

Bu daldan sonraki push'larda sadece `git push` yeter.

---

## 4) Dalını `main`'e almak istersen → **Pull Request**

Web arayüzünden (`http://10.199.0.10/stajyerler/data`) **"New Pull Request"** ile dalını
`main`'e önerirsin. Onaylanınca birleşir. (Doğrudan `main`'e yazma.)

---

## ⚠️ SAKIN bunları yapma

- ❌ **Repoyu SİLME.** (Settings → en altta kırmızı "Delete Repository" — dokunma.)
- ❌ **`main`'e doğrudan / zorla push** (`git push -f`, `--force`) yapma — başkasının işini ezer.
- ❌ **`mimari-referans/` klasörünü değiştirme/silme** — o sadece **örnek mimari** (bak & örnek al, kopyalama). Kendi kodunu repo **köküne** yaz.
- ❓ Emin değilsen **sil-at yapma, sor.**

---

## 😌 Kendi bilgisayarında bir şeyi batırdıysan — PANİK YOK

Sunucudaki hali güvende. Yerel kopyanı sunucudakiyle eşitle:

```bash
git checkout main
git fetch origin
git reset --hard origin/main     # yerel değişikliklerini atar, sunucudakiyle birebir yapar
```

Ya da klasörü tamamen sil, baştan `git clone` yap.
👉 **Sunucuya push etmediğin sürece kimseyi etkilemezsin — rahat ol.**

---

## 📌 Günlük 4 komut (bunları ezberle yeter)

```bash
git pull                  # başlarken: güncel hali al
git add .                 # değişiklikleri hazırla
git commit -m "ne yaptım" # kaydet
git push                  # sunucuya gönder
```

Kolay gelsin! Takılırsan mimari için `mimari-referans/` klasörüne ve `README.md`'ye bak.

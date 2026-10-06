# Föy 04 — SQL Temelleri ve İleri SQL

Modern Veritabanı Yönetim Sistemleri — Laboratuvar teslim deposu.
Görevlerin tam açıklaması **Föy 04 PDF**'indedir; bu dosya kısa bir hatırlatmadır.

## Bu hafta

Geçen hafta 3NF'e ayrıştırdığınız FıratFit şeması bu depoda **hazır** geliyor
(`sql/sema_hazir.sql`). Bu haftanın tamamı sorgu yazmaya ayrılmıştır:
temel sorgular → JOIN'ler → alt sorgular ve CTE → window fonksiyonları.

## Hızlı başlangıç

```bash
echo "230541001" > ogrno.txt              # kendi numaranız
docker compose up -d
python3 veri/uret.py 230541001            # kendi numaranız → 6 CSV
docker exec -i vtys-postgres psql -U vtys -d vtysdb < sql/sema_hazir.sql
docker exec -it vtys-postgres psql -U vtys -d vtysdb
```

## Depo yapısı

| Yol | Ne |
|---|---|
| `ogrno.txt` | Öğrenci numaranız (ilk iş: doldurun) |
| `sql/sema_hazir.sql` | Şema + veri kurulumu — HAZIR, değiştirmeyin |
| `sql/g1_temel.sql` | Görev 1 — temel sorgular (4 soru) |
| `sql/g2_join.sql` | Görev 2 — JOIN'ler (4 soru) |
| `sql/g3_alt.sql` | Görev 3 — alt sorgu ve CTE (3 soru) |
| `sql/g4_window.sql` | Görev 4 — window fonksiyonları (3 soru) |
| `sonuc/` | Sorgu çıktılarınız ve AI köşesi teslimi |


## Push etmeden önce kendinizi kontrol edin

Değerlendiriciyi kendi bilgisayarınızda çalıştırabilirsiniz — GitHub'daki ile
**aynı dosya, aynı puan**:

```bash
docker compose run --rm kontrol
```

Ekrana görev görev puanınız ve eksikleriniz düşer. İlk çalıştırma birkaç
saniye sürer, sonrakiler ~2 saniye. Ayrıca bir şey kurmanız gerekmez; Docker
zaten kurulu.

**Önce burada tam puan alın, sonra push edin.** Her push GitHub'da sınıfın
ortak Actions kotasından dakika harcar; deneme-yanılmayı buraya taşırsanız
kota dönem sonuna kadar yeter.

## Teslim

```bash
git add ogrno.txt sql/ sonuc/
git commit -m "Foy 04 teslimi"
git push
```

Push sonrası **Actions** sekmesinden sonucu görün. Düzeltmeleri önce
`docker compose run --rm kontrol` ile yerelde doğrulayın, sonra push edin. Sıralı istenen sorularda beraberlikler (eşit değerli
satırlar) hangi sırada olursa olsun kabul edilir.

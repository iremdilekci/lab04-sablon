# Yapay Zeka Sorgu Eleştirisi (Soru 3.3)

### Yapay Zekanın Ürettiği İlk Sorgu
```sql
SELECT u.ad, COUNT(k.kayit_id) AS kayit_sayisi
FROM uyeler u
JOIN kayitlar k ON u.uye_id = k.uye_id
GROUP BY u.uye_id, u.ad
ORDER BY kayit_sayisi DESC
LIMIT 1;
Eleştiri ve Değerlendirme
yapay zekaya cte şartından bahsetmeden soru 3.3u verdıgımde bana dırek order by kayit_sayisi desc limit 1 kullanarak bı sorgu yazdı. bu sorguyu kendı ortamımda calıstırdıgımda tek bı uye icin dogru sonuc verıyor gıbı dursada aslında mantıksal olarak eksık. cunku veritabanında en cok kayda sahıp aynı sayıda birden fazla uye olursa yani beraberlik durumu yasanırsa limit 1 kullandıgı ıcın sadece rastgele tek bir uyeyi getiriyor ve diger birinci olan üyeleri yutuyor. bu yuzden beraberlik durumunu hic hesaba katmamıs ve eksik sonuc donduruyor.

ayrıca powershell ortamında sorgu sonuclarını g3.txt dosyasına yazdırırken utf8 kodlama sorunu yasadım turkce karakterler bozuk cıktı. terminalde OutputEncoding ayarını utf8 yapmam gerekti ve ai tarafında cte yerine subquery veya limit tercih edildigi icin sorgunun okunabilirligi de pek iyi degildi. cte ile yazılan sorgu okunabilirlik acısından cok daha temiz ve adımları takip etmesi kolay.

Düzeltilmiş Sorgu (CTE ile Beraberlik Durumunu Kapsayan Hali)
SQL
WITH UyeKayitSayilari AS (
    SELECT u.ad, COUNT(k.kayit_id) AS kayit_sayisi
    FROM uyeler u
    JOIN kayitlar k ON u.uye_id = k.uye_id
    GROUP BY u.uye_id, u.ad
)
SELECT ad, kayit_sayisi
FROM UyeKayitSayilari
WHERE kayit_sayisi = (SELECT MAX(kayit_sayisi) FROM UyeKayitSayilari);
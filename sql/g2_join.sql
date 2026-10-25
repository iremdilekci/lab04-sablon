-- Soru 2.1: Her kaydın üye adı, ders adı ve kayıt tarihi
SELECT u.ad AS uye_adi, d.ad AS ders_adi, k.tarih AS kayit_tarihi
FROM kayitlar k
JOIN uyeler u ON k.uye_id = u.uye_id
JOIN dersler d ON k.ders_id = d.ders_id;

-- Soru 2.2: Her dersin adı, eğitmeninin adı ve salonunun adı (Tek sorguda üç tablo)
SELECT d.ad AS ders_adi, e.ad AS egitmen_adi, s.ad AS salon_adi
FROM dersler d
JOIN egitmenler e ON d.egitmen_id = e.egitmen_id
JOIN salonlar s ON d.salon_id = s.salon_id;

-- Soru 2.3: Hiçbir derse kaydolmamış üyelerin adı
SELECT u.ad
FROM uyeler u
LEFT JOIN kayitlar k ON u.uye_id = k.uye_id
WHERE k.uye_id IS NULL;

-- Soru 2.4: Derslerine en az bir kayıt yapılmış her eğitmenin adı ve toplam kayıt sayısı (Çoktan aza sıralı)
SELECT e.ad AS egitmen_adi, COUNT(k.kayit_id) AS toplam_kayit_sayisi
FROM egitmenler e
JOIN dersler d ON e.egitmen_id = d.egitmen_id
JOIN kayitlar k ON d.ders_id = k.ders_id
GROUP BY e.egitmen_id, e.ad
ORDER BY toplam_kayit_sayisi DESC;
-- Soru 4.1: Her ders için: salon adı, ders adı, ücret ve dersin kendi salonu içindeki ücret sırası
SELECT 
    s.ad AS salon_adi, 
    d.ad AS ders_adi, 
    d.ucret,
    RANK() OVER (PARTITION BY d.salon_id ORDER BY d.ucret DESC) AS ucret_sirasi
FROM dersler d
JOIN salonlar s ON d.salon_id = s.salon_id;

-- Soru 4.2: Her salonun en yüksek ücretli dersi ya da dersleri (beraberlik dahil): salon adı, ders adı, ücret
WITH SiraliDersler AS (
    SELECT 
        s.ad AS salon_adi, 
        d.ad AS ders_adi, 
        d.ucret,
        RANK() OVER (PARTITION BY d.salon_id ORDER BY d.ucret DESC) AS rn
    FROM dersler d
    JOIN salonlar s ON d.salon_id = s.salon_id
)
SELECT salon_adi, ders_adi, ucret
FROM SiraliDersler
WHERE rn = 1;

-- Soru 4.3: Aylara göre kayıt sayısı ve bir önceki aydan fark (LAG)
WITH AylikKayitlar AS (
    SELECT 
        EXTRACT(MONTH FROM tarih)::INTEGER AS ay,
        COUNT(kayit_id) AS kayit_sayisi
    FROM kayitlar
    GROUP BY EXTRACT(MONTH FROM tarih)
)
SELECT 
    ay,
    kayit_sayisi,
    kayit_sayisi - LAG(kayit_sayisi) OVER (ORDER BY ay) AS fark
FROM AylikKayitlar
ORDER BY ay;
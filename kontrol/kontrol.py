#!/usr/bin/env python3
"""Föy 04 — Otomatik Değerlendirici

GitHub Actions içinde çalışır. Temiz şemayı öğrencinin numarasından üretilen
KİŞİYE ÖZEL veriyle kurar ve 14 sorgunun tamamını bu veriye karşı çalıştırıp
Python ile hesaplanan beklenen sonuçlarla karşılaştırır. Hazır SQL cevabı
yoktur.

Sıralama istenen sorularda sıralama sütunu kontrol edilir; beraberlikler
(aynı değere sahip satırlar) hangi sırada olursa olsun kabul edilir.
"""
import os
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "veri"))
from uret import uret  # noqa: E402

try:
    import psycopg
except ImportError:
    print("HATA: psycopg kurulu değil (pip install 'psycopg[binary]').")
    sys.exit(2)

SONUCLAR = []


def kaydet(gorev, alinan, tam, mesaj):
    SONUCLAR.append((gorev, alinan, tam, mesaj))
    durum = "✓" if alinan == tam else ("~" if alinan > 0 else "✗")
    print(f"[{durum}] {gorev}: {alinan}/{tam} — {mesaj}")


def oku(yol):
    p = KOK / yol
    if not p.exists():
        return None
    ham = p.read_bytes()
    # Windows'ta PowerShell'in ">" yonlendirmesi UTF-16 yazar; Not Defteri de
    # UTF-8'e BOM ekler. Bunlari cozmezsek ogrencinin dogru cikti dosyasi
    # taninmaz ve haksiz puan kaybi olur.
    if ham[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return ham.decode("utf-16", errors="replace")
    return ham.decode("utf-8-sig", errors="replace")


def baglanti():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "vtys"),
        password=os.environ.get("PGPASSWORD", "vtys2026"),
        dbname=os.environ.get("PGDATABASE", "vtysdb"),
        autocommit=True,
    )


def ogrno_al():
    icerik = oku("ogrno.txt")
    if icerik is None:
        return None
    icerik = icerik.strip()
    return icerik if icerik.isdigit() else None


def sorgulari_ayir(metin, on_ek):
    parcalar = re.split(rf"--\s*Soru\s*{on_ek}\.(\d)[^\n]*", metin or "")
    sorgular = {}
    for i in range(1, len(parcalar) - 1, 2):
        sorgular[int(parcalar[i])] = parcalar[i + 1].strip().rstrip(";")
    return sorgular


def sema_kur(con, t):
    yol = KOK / "sql" / "sema_hazir.sql"
    ddl = yol.read_text(encoding="utf-8")
    ddl = ddl.split("COPY")[0]          # COPY'ler /veri yoluna bağlı; veriyi biz basarız
    con.execute(ddl)
    sira = [
        ("uyeler", ["uye_id", "ad", "dogum_yili"]),
        ("telefonlar", ["telefon_id", "uye_id", "numara"]),
        ("egitmenler", ["egitmen_id", "ad", "brans"]),
        ("salonlar", ["salon_id", "ad", "kapasite"]),
        ("dersler", ["ders_id", "ad", "egitmen_id", "salon_id", "ucret"]),
        ("kayitlar", ["kayit_id", "uye_id", "ders_id", "tarih"]),
    ]
    with con.cursor() as cur:
        for tablo, kolonlar in sira:
            with cur.copy(f"COPY {tablo} ({', '.join(kolonlar)}) FROM STDIN") as cp:
                for s in t[tablo]:
                    cp.write_row(tuple(s[k] for k in kolonlar))


# ---------------------------------------------------------------- beklenenler
def beklenenleri_hesapla(t):
    """14 sorunun beklenen sonuçları — tamamı üreteç verisinden, Python'la."""
    uye = {u["uye_id"]: u for u in t["uyeler"]}
    egitmen = {e["egitmen_id"]: e for e in t["egitmenler"]}
    salon = {s["salon_id"]: s for s in t["salonlar"]}
    ders = {d["ders_id"]: d for d in t["dersler"]}
    b = {}

    # G1
    b["1.1"] = Counter((u["ad"], u["dogum_yili"])
                       for u in t["uyeler"] if u["dogum_yili"] >= 2000)
    ucretler = [d["ucret"] for d in t["dersler"]]
    b["1.2"] = (min(ucretler), max(ucretler), sum(ucretler))
    b["1.3"] = Counter(e["brans"] for e in t["egitmenler"])
    salon_ders = Counter(salon[d["salon_id"]]["ad"] for d in t["dersler"])
    b["1.4"] = Counter({ad: n for ad, n in salon_ders.items() if n > 3})

    # G2
    b["2.1"] = Counter((uye[k["uye_id"]]["ad"], ders[k["ders_id"]]["ad"],
                        k["tarih"]) for k in t["kayitlar"])
    b["2.2"] = Counter((d["ad"], egitmen[d["egitmen_id"]]["ad"],
                        salon[d["salon_id"]]["ad"]) for d in t["dersler"])
    kayitli_uyeler = {k["uye_id"] for k in t["kayitlar"]}
    b["2.3"] = Counter(u["ad"] for u in t["uyeler"]
                       if u["uye_id"] not in kayitli_uyeler)
    egitmen_kayit = Counter()
    for k in t["kayitlar"]:
        egitmen_kayit[egitmen[ders[k["ders_id"]]["egitmen_id"]]["ad"]] += 1
    b["2.4"] = egitmen_kayit

    # G3
    ort = sum(ucretler) / len(ucretler)
    b["3.1"] = Counter((d["ad"], d["ucret"]) for d in t["dersler"]
                       if d["ucret"] > ort)
    yuzme = {e["egitmen_id"] for e in t["egitmenler"] if e["brans"] == "Yüzme"}
    b["3.2"] = Counter(d["ad"] for d in t["dersler"] if d["egitmen_id"] in yuzme)
    uye_kayit = Counter(k["uye_id"] for k in t["kayitlar"])
    en_cok = max(uye_kayit.values())
    b["3.3"] = Counter((uye[uid]["ad"], n) for uid, n in uye_kayit.items()
                       if n == en_cok)

    # G4
    rank_sonuc = []
    for d in t["dersler"]:
        ayni_salon = [x["ucret"] for x in t["dersler"]
                      if x["salon_id"] == d["salon_id"]]
        sira = 1 + sum(1 for u in ayni_salon if u > d["ucret"])
        rank_sonuc.append((salon[d["salon_id"]]["ad"], d["ad"],
                           d["ucret"], sira))
    b["4.1"] = Counter(rank_sonuc)

    b["4.2"] = Counter()
    for sid, s in salon.items():
        salondakiler = [d for d in t["dersler"] if d["salon_id"] == sid]
        if not salondakiler:
            continue
        tavan = max(d["ucret"] for d in salondakiler)
        for d in salondakiler:
            if d["ucret"] == tavan:
                b["4.2"][(s["ad"], d["ad"], d["ucret"])] += 1

    aylik = Counter(int(k["tarih"][5:7]) for k in t["kayitlar"])
    aylar = sorted(aylik)
    seri = []
    onceki = None
    for ay in aylar:
        fark = None if onceki is None else aylik[ay] - onceki
        seri.append((ay, aylik[ay], fark))
        onceki = aylik[ay]
    b["4.3"] = seri
    return b


# ---------------------------------------------------------------- kıyaslar
def coklu_kume(rows):
    return Counter(tuple(str(x) if x is not None else None for x in r)
                   for r in rows)


def beklenen_kume(beklenen):
    if isinstance(beklenen, Counter):
        beklenen = beklenen.elements()   # çoklukları koru
    return Counter(tuple(str(x) if x is not None else None for x in r)
                   for r in beklenen)


def sirali_azalan(rows, sutun=-1):
    degerler = [r[sutun] for r in rows]
    return degerler == sorted(degerler, reverse=True)


def gorev_kontrol(con, dosya, on_ek, plan, baslik, toplam_puan):
    """plan: {soru_no: (puan, kontrol_fonksiyonu, secenekler)}"""
    metin = oku(dosya)
    if metin is None:
        kaydet(baslik, 0, toplam_puan, f"{dosya} bulunamadı.")
        return
    sorgular = sorgulari_ayir(metin, on_ek)
    puan = 0
    mesajlar = []
    for no, (p, kontrol, secenek) in plan.items():
        q = sorgular.get(no, "")
        if not q:
            mesajlar.append(f"{on_ek}.{no}: sorgu yok.")
            continue
        try:
            rows = con.execute(q).fetchall()
        except Exception as e:
            mesajlar.append(f"{on_ek}.{no}: sorgu hatası ({str(e).splitlines()[0]}).")
            continue
        dogru = kontrol(rows)
        if dogru:
            kazanc = p
            if secenek and not re.search(secenek["desen"], q, re.IGNORECASE):
                kazanc = p // 2
                mesajlar.append(f"{on_ek}.{no}: sonuç doğru ama {secenek['ad']} "
                                f"kullanılmamış — yarım puan.")
            else:
                mesajlar.append(f"{on_ek}.{no}: doğru.")
            puan += kazanc
        else:
            mesajlar.append(f"{on_ek}.{no}: sonuç beklenenden farklı.")
    kaydet(baslik, puan, toplam_puan, " ".join(mesajlar))


def kontrol_ai():
    icerik = oku("sonuc/ai_elestiri.md")
    if not icerik or len(icerik.strip()) < 300:
        kaydet("AI Köşesi", 0, 10,
               "sonuc/ai_elestiri.md yok ya da çok kısa (içerik asistan tarafından ayrıca okunur).")
    else:
        kaydet("AI Köşesi", 10, 10,
               "Dosya teslim edildi (isabet puanı asistan değerlendirmesiyle kesinleşir).")


# ---------------------------------------------------------------- ana akış
def main():
    print("=" * 64)
    print("Föy 04 — Otomatik Değerlendirme")
    print("=" * 64)

    ogrno = ogrno_al()
    if not ogrno:
        print("HATA: ogrno.txt bulunamadı ya da geçerli bir numara içermiyor.")
        sys.exit(1)
    print(f"Öğrenci no: {ogrno} (veri seti bu numaradan yeniden üretiliyor)\n")

    t = uret(ogrno)
    b = beklenenleri_hesapla(t)

    with baglanti() as con:
        sema_kur(con, t)

        gorev_kontrol(con, "sql/g1_temel.sql", 1, {
            1: (5, lambda r: coklu_kume(r) == beklenen_kume(b["1.1"]), None),
            2: (5, lambda r: len(r) == 1 and tuple(int(x) for x in r[0][:3]) == b["1.2"], None),
            3: (5, lambda r: coklu_kume(r) == beklenen_kume(
                b["1.3"].items()) and sirali_azalan(r), None),
            4: (5, lambda r: coklu_kume(r) == beklenen_kume(b["1.4"].items()), None),
        }, "Görev 1 (Temel)", 20)

        gorev_kontrol(con, "sql/g2_join.sql", 2, {
            1: (6, lambda r: coklu_kume(r) == beklenen_kume(b["2.1"]), None),
            2: (6, lambda r: coklu_kume(r) == beklenen_kume(b["2.2"]), None),
            3: (6, lambda r: coklu_kume((x[0],) for x in r)
                == beklenen_kume((a,) for a in b["2.3"].elements()), None),
            4: (7, lambda r: coklu_kume(r) == beklenen_kume(
                b["2.4"].items()) and sirali_azalan(r), None),
        }, "Görev 2 (JOIN)", 25)

        gorev_kontrol(con, "sql/g3_alt.sql", 3, {
            1: (8, lambda r: coklu_kume(r) == beklenen_kume(b["3.1"]), None),
            2: (8, lambda r: coklu_kume((x[0],) for x in r)
                == beklenen_kume((a,) for a in b["3.2"].elements()), None),
            3: (9, lambda r: coklu_kume(r) == beklenen_kume(b["3.3"]),
                {"desen": r"\bWITH\b", "ad": "CTE (WITH)"}),
        }, "Görev 3 (Alt sorgu/CTE)", 25)

        gorev_kontrol(con, "sql/g4_window.sql", 4, {
            1: (7, lambda r: coklu_kume(r) == beklenen_kume(b["4.1"]),
                {"desen": r"OVER\s*\(", "ad": "window fonksiyonu"}),
            2: (7, lambda r: coklu_kume(r) == beklenen_kume(b["4.2"]), None),
            3: (6, lambda r: [(int(x[0]), int(x[1]),
                               None if x[2] is None else int(x[2]))
                              for x in r] == b["4.3"],
                {"desen": r"\bLAG\s*\(", "ad": "LAG"}),
        }, "Görev 4 (Window)", 20)

    kontrol_ai()

    alinan = sum(s[1] for s in SONUCLAR)
    tam = sum(s[2] for s in SONUCLAR)
    print("\n" + "=" * 64)
    print(f"TOPLAM (otomatik kontrol edilen kısım): {alinan}/{tam}")
    print("Ön quiz (5p) bu rapora dahil değildir; AI köşesi asistan")
    print("tarafından ayrıca değerlendirilir.")
    print("=" * 64)

    ozet = os.environ.get("GITHUB_STEP_SUMMARY")
    if ozet:
        with open(ozet, "a", encoding="utf-8") as f:
            f.write("## Föy 04 — Otomatik Değerlendirme\n\n")
            f.write("| Bileşen | Puan | Açıklama |\n|---|---|---|\n")
            for gorev, a, tp, m in SONUCLAR:
                f.write(f"| {gorev} | {a}/{tp} | {m} |\n")
            f.write(f"| **Toplam** | **{alinan}/{tam}** | |\n")

    sys.exit(0 if alinan == tam else 1)


if __name__ == "__main__":
    main()

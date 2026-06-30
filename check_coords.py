#!/usr/bin/env python3
"""
tumanlar.json fayldagi lat/lon qiymatlarini OpenStreetMap (Nominatim)
geocoding xizmati orqali avtomatik tekshiradi.

Ishlatish:
    pip install requests
    python3 check_coords.py tumanlar.json

Natija:
    - Terminalda har bir yozuv uchun: OK / OGOHLANTIRISH / XATO
    - natija.csv fayliga to'liq hisobot yoziladi

Eslatma: Nominatim bepul xizmat, sekundiga 1 ta so'rov limiti bor.
207 yozuv uchun ~3-4 daqiqa vaqt ketadi. Iltimos shoshilmang.
"""

import json
import sys
import time
import csv
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "tumanlar-json-checker/1.0 (shaxsiy tekshiruv skripti)"

# Agar bir nuqta haqiqiy joydan shuncha km dan ko'p uzoq bo'lsa - "XATO" deb belgilanadi
XATO_KM = 30
OGOHLANTIRISH_KM = 12


def haversine_km(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def geocode(query):
    """Nominatim orqali joy nomini lat/lon ga aylantiradi."""
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "uz",
    }
    url = NOMINATIM_URL + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", "")
    except (URLError, TimeoutError, KeyError, IndexError, ValueError) as e:
        print(f"    [tarmoq xatosi: {e}]")
        return None


def collect_entries(data):
    """JSON ichidan barcha viloyat-markaz va tuman/shahar yozuvlarini chiqaradi."""
    entries = []
    for region_key, region in data["uzbekistan"].items():
        entries.append({
            "path": region_key,
            "name_uz": region["name_uz"],
            "name_en": region["name_en"],
            "lat": region["lat"],
            "lon": region["lon"],
            "kind": "viloyat markazi",
        })
        for i, d in enumerate(region["districts"]):
            entries.append({
                "path": f"{region_key}.districts[{i}]",
                "name_uz": d["name_uz"],
                "name_en": d["name_en"],
                "lat": d["lat"],
                "lon": d["lon"],
                "kind": "tuman/shahar",
            })
    return entries


def main():
    if len(sys.argv) < 2:
        print("Ishlatish: python3 check_coords.py tumanlar.json")
        sys.exit(1)

    fname = sys.argv[1]
    with open(fname, encoding="utf-8") as f:
        data = json.load(f)

    entries = collect_entries(data)
    print(f"Jami tekshiriladigan yozuvlar: {len(entries)}")
    print(f"Taxminiy vaqt: ~{len(entries)} soniya (Nominatim 1 so'rov/soniya limiti)\n")

    results = []
    for idx, e in enumerate(entries, 1):
        query = f"{e['name_uz']}, Uzbekistan"
        print(f"[{idx}/{len(entries)}] {e['name_uz']:30s} ", end="", flush=True)

        geo = geocode(query)
        time.sleep(1.1)  # Nominatim siyosati: max 1 so'rov/soniya

        if geo is None:
            print("TOPILMADI (qo'lda tekshiring)")
            results.append({**e, "osm_lat": "", "osm_lon": "", "farq_km": "", "holat": "TOPILMADI", "osm_nomi": ""})
            continue

        osm_lat, osm_lon, osm_nomi = geo
        farq = haversine_km(e["lat"], e["lon"], osm_lat, osm_lon)

        if farq > XATO_KM:
            holat = "XATO"
        elif farq > OGOHLANTIRISH_KM:
            holat = "OGOHLANTIRISH"
        else:
            holat = "OK"

        print(f"farq={farq:6.1f} km  -> {holat}")
        results.append({
            **e,
            "osm_lat": round(osm_lat, 4),
            "osm_lon": round(osm_lon, 4),
            "farq_km": round(farq, 1),
            "holat": holat,
            "osm_nomi": osm_nomi,
        })

    # CSV ga yozish
    out_csv = "natija.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "path", "name_uz", "name_en", "kind",
            "lat", "lon", "osm_lat", "osm_lon", "farq_km", "holat", "osm_nomi"
        ])
        writer.writeheader()
        writer.writerows(results)

    # Xulosa
    xato = [r for r in results if r["holat"] == "XATO"]
    ogoh = [r for r in results if r["holat"] == "OGOHLANTIRISH"]
    topilmadi = [r for r in results if r["holat"] == "TOPILMADI"]

    print("\n" + "=" * 60)
    print(f"NATIJA: {out_csv} fayliga yozildi")
    print(f"  OK:            {len(results) - len(xato) - len(ogoh) - len(topilmadi)}")
    print(f"  OGOHLANTIRISH: {len(ogoh)}")
    print(f"  XATO:          {len(xato)}")
    print(f"  TOPILMADI:     {len(topilmadi)}")

    if xato:
        print("\nXATO deb belgilangan yozuvlar:")
        for r in xato:
            print(f"  - {r['name_uz']:30s} farq={r['farq_km']} km  (fayl: {r['lat']},{r['lon']} | OSM: {r['osm_lat']},{r['osm_lon']})")


if __name__ == "__main__":
    main()

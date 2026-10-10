# Laborator 5, Lucrarea B (B1-B4): forensics pe fișiere
# Student: Șibaev Vasile, grupa SI-265
"""B1 magic bytes, B2 strings, B3 EXIF/GPS, B4 file carving.

Rulare:  python forensics.py
Lucrează doar pe fișierele din probe/.
"""

import re
import zipfile
from pathlib import Path

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

RADACINA = Path(__file__).resolve().parent
PROBE = RADACINA / "probe"

SEMNATURI = [
    (b"%PDF", "pdf"),
    (b"\x89PNG", "png"),
    (b"\xff\xd8", "jpeg"),
    (b"PK\x03\x04", "zip/docx"),
    (b"GIF8", "gif"),
    (b"\x1f\x8b", "gzip"),
    (b"\x7fELF", "elf"),
    (b"Rar!", "rar"),
    (b"7z\xbc\xaf", "7z"),
]


# ---------------------------------------------------------------------------
# B1. Magic bytes: tipul real, nu extensia
# ---------------------------------------------------------------------------
def tip_real(cale):
    """Citește primii octeți (modul "rb") și îi compară cu semnăturile."""
    with open(cale, "rb") as f:
        cap = f.read(8)
    for semnatura, nume in SEMNATURI:
        if cap.startswith(semnatura):
            return nume
    return cap.hex()


def descriere_tip(cale):
    """Tipul real sau, când nu există semnătură cunoscută, 'text' / 'binar'."""
    tip = tip_real(cale)
    if tip in {nume for _, nume in SEMNATURI}:
        return tip
    with open(cale, "rb") as f:
        esantion = f.read(512)
    if esantion and all(32 <= c < 127 or c in (9, 10, 13) for c in esantion):
        return "text (fără semnătură)"
    return "binar (semnătură necunoscută)"


# ---------------------------------------------------------------------------
# B2. strings: textul citibil dintr-un binar
# ---------------------------------------------------------------------------
def strings(cale, minim=4):
    """Toate secvențele de cel puțin `minim` caractere imprimabile."""
    with open(cale, "rb") as f:
        date = f.read()
    tipar = rb"[ -~]{%d,}" % minim
    return [m.decode() for m in re.findall(tipar, date)]


def strings_dupa_iend(cale):
    """Șirurile din coada unui PNG, după chunk-ul IEND (aici stau de obicei
    datele lipite)."""
    with open(cale, "rb") as f:
        date = f.read()
    i = date.find(b"IEND")
    if i == -1:
        return []
    coada = date[i + 8:]      # sărim peste IEND + CRC
    return [m.decode() for m in re.findall(rb"[ -~]{4,}", coada)]


# ---------------------------------------------------------------------------
# B3. EXIF și GPS
# ---------------------------------------------------------------------------
def citeste_exif(cale):
    """Întoarce (exif, gps): două dicționare cu numele etichetelor."""
    img = Image.open(cale)
    brut = img.getexif()
    exif = {}
    for id_, val in brut.items():
        if id_ in (0x8825, 0x8769):       # sunt blocuri (GPS / Exif), le citim separat
            continue
        exif[TAGS.get(id_, id_)] = val
    for id_, val in brut.get_ifd(0x8769).items():
        exif[TAGS.get(id_, id_)] = val
    gps = {GPSTAGS.get(id_, id_): val for id_, val in brut.get_ifd(0x8825).items()}
    return exif, gps


def grade_zecimale(coord, emisfera):
    """(grade, minute, secunde) + N/S/E/W -> grade zecimale (S și W sunt negative)."""
    grade, minute, secunde = (float(x) for x in coord)
    val = grade + minute / 60 + secunde / 3600
    return -val if emisfera in ("S", "W") else val


def coordonate_gps(gps):
    """(latitudine, longitudine) în grade zecimale sau None dacă lipsesc."""
    try:
        lat = grade_zecimale(gps["GPSLatitude"], gps["GPSLatitudeRef"])
        lon = grade_zecimale(gps["GPSLongitude"], gps["GPSLongitudeRef"])
    except KeyError:
        return None
    return lat, lon


# ---------------------------------------------------------------------------
# B4. File carving
# ---------------------------------------------------------------------------
def extrage_zip(cale, iesire=None):
    """Caută semnătura ZIP într-un fișier și salvează tot ce urmează după ea.

    Întoarce poziția (offset-ul) găsită sau None."""
    iesire = Path(iesire) if iesire else RADACINA / "gasit.zip"
    with open(cale, "rb") as f:
        date = f.read()
    i = date.find(b"PK\x03\x04")
    if i == -1:
        return None
    iesire.write_bytes(date[i:])
    return i


def continut_zip(cale_zip, folder=None):
    """Dezarhivează și întoarce [(nume, text)] pentru fișierele găsite."""
    folder = Path(folder) if folder else RADACINA / "gasit_zip"
    rezultat = []
    with zipfile.ZipFile(cale_zip) as z:
        for info in z.infolist():
            try:
                z.extract(info, folder)
                date = (folder / info.filename).read_bytes()
                rezultat.append((info.filename, date.decode("utf-8", "replace")))
            except RuntimeError:
                rezultat.append((info.filename, "<fișier protejat cu parolă>"))
    return rezultat


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== B1. Tipul real al fișierelor ===")
    for f in sorted(PROBE.iterdir()):
        if f.is_file() and f.suffix != ".py":
            print(f"{f.name:20} extensia: {f.suffix or '-':6} tip real: {descriere_tip(f)}")

    print("\n=== B2. strings din probe/ascuns.png ===")
    toate = strings(PROBE / "ascuns.png")
    print(len(toate), "șiruri găsite; cele din coada fișierului (după IEND):")
    for s in strings_dupa_iend(PROBE / "ascuns.png"):
        print("  ", s)

    print("\n=== B3. EXIF și GPS din probe/foto.jpg ===")
    exif, gps = citeste_exif(PROBE / "foto.jpg")
    for k, v in exif.items():
        print(f"{k} = {v}")
    print("GPS brut:", gps)
    coord = coordonate_gps(gps)
    if coord:
        lat, lon = coord
        print(f"Latitudine:  {lat:.6f}")
        print(f"Longitudine: {lon:.6f}")
        print(f"Hartă: https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}")
    else:
        print("Fără coordonate GPS.")

    print("\n=== B4. File carving din probe/ascuns.png ===")
    poz = extrage_zip(PROBE / "ascuns.png")
    if poz is None:
        print("Nu s-a găsit nicio arhivă ZIP.")
    else:
        print("arhiva extrasă de la octetul", poz, "-> gasit.zip")
        for nume, text in continut_zip(RADACINA / "gasit.zip"):
            print(f"[{nume}]\n{text}")

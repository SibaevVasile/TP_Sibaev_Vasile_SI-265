# Laborator 5: pregătirea țintelor de laborator
# Student: Șibaev Vasile, grupa SI-265
"""Creează în probe/ fișierele pe care le analizăm în laborator.
"""

import base64
import hashlib
import io
import zipfile
from pathlib import Path
from urllib.parse import quote

from PIL import Image

AICI = Path(__file__).resolve().parent

PAROLE = ["sunshine", "dragon", "trustno1"]
WORDLIST = [
    "123456", "password", "12345678", "qwerty", "abc123", "monkey", "letmein",
    "football", "iloveyou", "admin", "welcome", "login", "master", "hello",
    "freedom", "whatever", "qazwsx", "baseball", "shadow", "michael",
    "superman", "batman", "princess", "starwars", "cheese", "computer",
    "internet", "secret", "parola", "chisinau", "moldova", "utm2026",
] + PAROLE


def mesaj_straturi():
    """text -> base64 -> url (quote) -> hex; scris în mesaj.txt"""
    text = "FLAG{straturi_de_codare!}"
    strat1 = base64.b64encode(text.encode()).decode()
    strat2 = quote(strat1, safe="")
    assert "%" in strat2, "stratul URL trebuie să conțină %xx"
    strat3 = strat2.encode().hex()
    (AICI / "mesaj.txt").write_text(strat3 + "\n")


def mesaj_xor():
    clar = b"Mesaj XOR: parola este 'trandafir' iar cheia are un singur octet"
    (AICI / "xor.bin").write_bytes(bytes(b ^ 0x2B for b in clar))


def hashuri():
    linii = [
        hashlib.md5(PAROLE[0].encode()).hexdigest(),
        hashlib.sha1(PAROLE[1].encode()).hexdigest(),
        hashlib.sha256(PAROLE[2].encode()).hexdigest(),
    ]
    (AICI / "hashuri.txt").write_text("\n".join(linii) + "\n")
    (AICI / "wordlist.txt").write_text("\n".join(WORDLIST) + "\n")


def poza_gazda(latime=320, inaltime=240):
    img = Image.new("RGB", (latime, inaltime))
    pixeli = [((x * 255) // latime, (y * 255) // inaltime, ((x + y) * 255) // (latime + inaltime))
              for y in range(inaltime) for x in range(latime)]
    img.putdata(pixeli)
    return img


def foto_exif():
    img = poza_gazda()
    exif = Image.Exif()
    exif[0x010F] = "UTM-LAB"                 # Make
    exif[0x0110] = "Telefon-Demo"            # Model
    exif[0x0131] = "pregateste.py"           # Software
    exif[0x8769] = {0x9003: "2026:09:30 14:22:05"}   # DateTimeOriginal
    exif[0x8825] = {                         # GPS: 47°0'37.8"N 28°51'49.7"E (Chișinău)
        1: "N", 2: (47.0, 0.0, 37.8),
        3: "E", 4: (28.0, 51.0, 49.7),
    }
    img.save(AICI / "foto.jpg", "JPEG", quality=95, exif=exif)


def png_cu_arhiva():
    img = poza_gazda(256, 256)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    arhiva = io.BytesIO()
    with zipfile.ZipFile(arhiva, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("secret.txt", "FLAG{fisier_lipit_la_coada}\nAcest fisier era ascuns dupa IEND.\n")
    (AICI / "ascuns.png").write_bytes(buf.getvalue() + arhiva.getvalue())


if __name__ == "__main__":
    mesaj_straturi()
    mesaj_xor()
    hashuri()
    foto_exif()
    png_cu_arhiva()
    print("Fișierele au fost create în", AICI)
    for f in sorted(AICI.iterdir()):
        print(" -", f.name)

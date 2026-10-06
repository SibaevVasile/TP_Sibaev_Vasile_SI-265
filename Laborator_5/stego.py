# Laborator 5, Lucrarea B (B5-B6): steganografie LSB
# Student: Șibaev Vasile, grupa SI-265
"""Ascunde / dezvăluie un mesaj în bitul cel mai puțin semnificativ (LSB)
al canalelor R, G, B ale unei imagini.

    python stego.py ascunde                 # probe/foto.jpg -> stego.png
    python stego.py ascunde "alt mesaj"
    python stego.py dezvaluie               # citește stego.png
"""

import sys
from pathlib import Path

from PIL import Image

RADACINA = Path(__file__).resolve().parent
SURSA = RADACINA / "probe" / "foto.jpg"
IESIRE = RADACINA / "stego.png"
MESAJ = b"FLAG{LSB_STEGANOGRAPHY}"


def ascunde(sursa, mesaj, iesire):
    """Scrie `mesaj` (bytes) + un octet 0 de final în LSB-urile pixelilor.

    Se salvează în PNG (fără pierdere): un JPG ar recompresa imaginea și ar
    distruge biții ascunși.
    """
    img = Image.open(sursa).convert("RGB")
    canale = bytearray(img.tobytes())          # R,G,B,R,G,B,... pentru fiecare pixel
    biti = "".join(f"{x:08b}" for x in mesaj + b"\x00")
    if len(biti) > len(canale):
        raise ValueError(f"mesaj prea lung: {len(biti)} biți, încap {len(canale)}")
    for i, bit in enumerate(biti):
        canale[i] = (canale[i] & ~1) | int(bit)
    Image.frombytes("RGB", img.size, bytes(canale)).save(iesire, "PNG")
    return len(biti)


def dezvaluie(cale):
    """Citește LSB-urile, le grupează câte 8 și se oprește la primul octet 0."""
    canale = Image.open(cale).convert("RGB").tobytes()
    mesaj = bytearray()
    for i in range(0, len(canale) - 7, 8):
        octet = 0
        for j in range(8):
            octet = (octet << 1) | (canale[i + j] & 1)
        if octet == 0:
            break
        mesaj.append(octet)
    return bytes(mesaj)


def diferenta_maxima(a, b):
    """Cea mai mare diferență dintre două canale de pixel (pentru LSB: 1)."""
    ba = Image.open(a).convert("RGB").tobytes()
    bb = Image.open(b).convert("RGB").tobytes()
    return max(abs(x - y) for x, y in zip(ba, bb))


if __name__ == "__main__":
    comanda = sys.argv[1] if len(sys.argv) > 1 else "ascunde"
    if comanda == "ascunde":
        mesaj = sys.argv[2].encode() if len(sys.argv) > 2 else MESAJ
        biti = ascunde(SURSA, mesaj, IESIRE)
        print(f"Ascuns {len(mesaj)} octeți ({biti} biți) în {IESIRE.name}")
        print("Diferența maximă față de original:", diferenta_maxima(SURSA, IESIRE))
    elif comanda == "dezvaluie":
        mesaj = dezvaluie(IESIRE)
        print("Mesaj dezvăluit:", mesaj.decode("utf-8", "replace"))
    else:
        sys.exit("folosire: python stego.py [ascunde [mesaj] | dezvaluie]")

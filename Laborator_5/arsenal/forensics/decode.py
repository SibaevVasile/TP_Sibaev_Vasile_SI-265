# Laborator 5, Lucrarea A: decoderul universal
# Student: Șibaev Vasile, grupa SI-265
"""Decoder universal: recunoaște stratul (url/hex/base64), îl desface în
buclă, sparge un XOR cu cheie de un octet și un hash prin dicționar.

Exemple:
    python arsenal/forensics/decode.py "U2FsdXQ="
    python arsenal/forensics/decode.py probe/mesaj.txt --fisier
    python arsenal/forensics/decode.py probe/xor.bin --fisier --xor
    python arsenal/forensics/decode.py probe/hashuri.txt --fisier --hash
"""

import argparse
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

RADACINA = Path(__file__).resolve().parents[2]   # folderul Laborator_5
FISA = Path(__file__).with_name("fisa.json")

# lungimea hash-ului (în caractere hex) -> algoritm
ALGORITMI = {32: "md5", 40: "sha1", 56: "sha224", 64: "sha256",
             96: "sha384", 128: "sha512"}

# parole foarte frecvente, încercate după wordlist (sau în locul ei)
PAROLE_COMUNE = [
    "123456", "password", "12345678", "qwerty", "abc123", "monkey", "letmein",
    "dragon", "111111", "baseball", "iloveyou", "trustno1", "sunshine",
    "master", "welcome", "shadow", "admin", "football", "login", "secret",
]


# ---------------------------------------------------------------------------
# A1. Text și octeți
# ---------------------------------------------------------------------------
def incalzire():
    s = "Salut"
    b = s.encode()                 # str -> bytes
    print(b, b[0])                 # b'Salut' 83  (b[0] este un număr, nu o literă)
    h = b.hex()
    print(h)                       # 53616c7574
    print(bytes.fromhex(h))        # b'Salut'


# ---------------------------------------------------------------------------
# A2. Recunoaștem stratul după formă
# ---------------------------------------------------------------------------
def ghici_strat(s):
    """Clasifică șirul: 'url', 'hex', 'base64' sau 'necunoscut' (fără decodare).

    Ordinea contează: întâi %xx (URL), apoi hex (alfabet mai strict),
    apoi base64 (alfabetul cel mai larg).
    """
    s = s.strip()
    if not s:
        return "necunoscut"
    if re.search(r"%[0-9a-fA-F]{2}", s):
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# ---------------------------------------------------------------------------
# A3. Desfacem stratul recunoscut
# ---------------------------------------------------------------------------
def desfa(s):
    """Întoarce (strat, rezultat_bytes). Dacă nu se poate decoda: ('necunoscut', s)."""
    s = s.strip()
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "url":
            return strat, unquote(s).encode()
    except (binascii.Error, ValueError):
        pass
    return "necunoscut", s.encode()


# ---------------------------------------------------------------------------
# A4. Straturi multiple, în buclă
# ---------------------------------------------------------------------------
def citibil(b, tolerant=False):
    """True dacă toți octeții sunt 32..126 (cu tolerant=True: și \\t \\n \\r)."""
    if not b:
        return False
    permise = {9, 10, 13} if tolerant else set()
    return all(32 <= c < 127 or c in permise for c in b)


def desface_straturi(val, max_pasi=8):
    """Decodează în buclă până nu mai există un strat care dă text citibil.

    Întoarce (lista_straturilor, text_final, binar_hex). `binar_hex` este None,
    iar dacă ultimul strat a dat octeți ne-citibili (fișier binar) îi dă ca hex.
    Limita max_pasi ne ferește de o buclă infinită.
    """
    straturi = []
    val = val.strip()
    binar = None
    for _ in range(max_pasi):
        strat, b = desfa(val)
        if strat == "necunoscut":
            break
        if not citibil(b, tolerant=True):
            binar = b.hex()
            break
        straturi.append(strat)
        val = b.decode()
        if "FLAG{" in val:      # am ajuns la steag, ne oprim
            break
    return straturi, val, binar


# ---------------------------------------------------------------------------
# A5. XOR cu cheie de un octet (forță brută pe 256 de chei)
# ---------------------------------------------------------------------------
def xor_brute(date):
    """Încearcă toate cele 256 de chei; întoarce [(cheie, text)] ordonat după
    cât de mult seamănă textul cu limbajul natural (litere + spații)."""
    gasite = []
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar, tolerant=True):
            scor = sum(chr(c).isalpha() or c == 32 for c in clar) / len(clar)
            gasite.append((scor, k, clar.decode()))
    gasite.sort(reverse=True)
    return [(k, text) for _, k, text in gasite]


# ---------------------------------------------------------------------------
# A6. Hash spart prin dicționar
# ---------------------------------------------------------------------------
def incarca_wordlist(cale=None):
    """Cuvintele din probe/wordlist.txt (dacă există), apoi parolele comune."""
    cale = Path(cale) if cale else RADACINA / "probe" / "wordlist.txt"
    cuvinte = []
    if cale.exists():
        with open(cale, encoding="latin1") as f:
            cuvinte = [l.strip() for l in f if l.strip()]
    return cuvinte + PAROLE_COMUNE


def sparge_hash(tinta, cuvinte=None):
    """Identifică algoritmul după lungime și caută parola în dicționar.

    Nu „decriptăm” hash-ul: hash-uim fiecare cuvânt și comparăm.
    Întoarce (algoritm, parola) sau (algoritm, None) dacă nu se găsește.
    """
    tinta = tinta.strip().lower()
    algo = ALGORITMI.get(len(tinta))
    if algo is None:
        return None, None
    if cuvinte is None:
        cuvinte = incarca_wordlist()
    for cuv in cuvinte:
        if hashlib.new(algo, cuv.encode()).hexdigest() == tinta:
            return algo, cuv
    return algo, None


# ---------------------------------------------------------------------------
# A7. argparse + fișa JSON
# ---------------------------------------------------------------------------
def salveaza_fisa(fisa):
    with open(FISA, "w", encoding="utf-8") as f:
        json.dump(fisa, f, indent=2, ensure_ascii=False)
    print("Fișă salvată în", FISA)


def main(argv=None):
    p = argparse.ArgumentParser(description="Decoder universal (forensics).")
    p.add_argument("intrare", nargs="?", help="șir sau cale de fișier")
    p.add_argument("--fisier", action="store_true",
                   help="intrarea este o cale; se citesc octeții din fișier")
    p.add_argument("--xor", action="store_true",
                   help="sparge un XOR cu cheie de un octet")
    p.add_argument("--hash", action="store_true",
                   help="sparge hash-ul/hash-urile prin dicționar")
    p.add_argument("--demo", action="store_true", help="rulează încălzirea A1")
    a = p.parse_args(argv)

    if a.demo:
        incalzire()
        print(ghici_strat("%2Fetc"), ghici_strat("48656c6c6f"))
        return 0
    if a.intrare is None:
        p.error("lipsește intrarea (șir sau cale cu --fisier)")

    date = Path(a.intrare).read_bytes() if a.fisier else a.intrare.encode()

    if a.xor:
        rezultate = xor_brute(date)
        if not rezultate:
            print("Nicio cheie nu dă text citibil.")
            return 1
        k, text = rezultate[0]
        print(f"cheie: {k} (0x{k:02x}) -> {text}")
        if len(rezultate) > 1:
            print(f"({len(rezultate) - 1} chei false dau și ele octeți imprimabili, "
                  "dar fără sens)")
        salveaza_fisa({"intrare": a.intrare, "strat": "xor",
                       "cheie": k, "rezultat": text})
        return 0

    text_in = date.decode("latin1").strip()

    if a.hash:
        fisa = {"intrare": a.intrare, "strat": "hash", "hashuri": []}
        cuvinte = incarca_wordlist()
        for linie in text_in.splitlines():
            linie = linie.strip()
            if not linie:
                continue
            algo, parola = sparge_hash(linie, cuvinte)
            print(f"{linie[:16]}... ({algo}) -> {parola or 'negăsit'}")
            fisa["hashuri"].append({"hash": linie, "algoritm": algo, "parola": parola})
        gasit = [h for h in fisa["hashuri"] if h["parola"]]
        fisa["rezultat"] = gasit[0]["parola"] if gasit else None
        salveaza_fisa(fisa)
        return 0

    straturi, text, binar = desface_straturi(text_in)
    print("straturi:", " -> ".join(straturi) or "niciunul")
    print("rezultat:", text)
    if binar:
        print("rest binar (hex):", binar)
    salveaza_fisa({"intrare": a.intrare, "strat": straturi[0] if straturi else "necunoscut",
                   "straturi": straturi, "rezultat": text})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

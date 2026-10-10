# Laborator 5: generează raport.md din rezultatele reale ale uneltelor
# Student: Șibaev Vasile, grupa SI-265
"""Rulează uneltele pe fișierele din probe/ și scrie raport.md cu ce a ieșit.

Se rulează după `python probe/pregateste.py`:   python genereaza_raport.py
"""

import hashlib
import re
from pathlib import Path

import forensics as fo
import stego
from arsenal.forensics import decode as dc

RADACINA = Path(__file__).resolve().parent
PROBE = RADACINA / "probe"


def bloc(text):
    return "```\n" + text.rstrip() + "\n```\n"


def sectiunea_a():
    out = ["## Lucrarea A. Decoderul universal\n"]

    # --- mesaj cu straturi
    mesaj = (PROBE / "mesaj.txt").read_text().strip()
    straturi, text, binar = dc.desface_straturi(mesaj)
    out.append("### A1-A4. Mesajul cu straturi (`probe/mesaj.txt`)\n")
    out.append(f"Intrare: `{mesaj[:60]}{'...' if len(mesaj) > 60 else ''}`\n")
    out.append(f"Straturile desfăcute, în ordine: **{' -> '.join(straturi) or 'niciunul'}**\n")
    out.append(f"Mesajul ascuns: **{text}**\n")
    if binar:
        out.append(f"Rest binar (hex): `{binar}`\n")

    # --- XOR
    out.append("### A5. XOR cu cheie de un octet (`probe/xor.bin`)\n")
    rez = dc.xor_brute((PROBE / "xor.bin").read_bytes())
    if rez:
        k, clar = rez[0]
        out.append(f"Cheia găsită: **{k}** (`0x{k:02x}`)\n")
        out.append(f"Textul în clar: **{clar}**\n")
        out.append(f"(încă {len(rez) - 1} chei dau octeți imprimabili, dar fără sens)\n")
    else:
        out.append("Nicio cheie nu a dat text citibil.\n")

    # --- hash
    out.append("### A6. Hash-uri sparte prin dicționar (`probe/hashuri.txt`)\n")
    out.append("| Hash (început) | Algoritm | Parola |\n|---|---|---|")
    cuvinte = dc.incarca_wordlist()
    for linie in (PROBE / "hashuri.txt").read_text().splitlines():
        linie = linie.strip()
        if linie:
            algo, parola = dc.sparge_hash(linie, cuvinte)
            out.append(f"| `{linie[:16]}...` | {algo} | {parola or 'negăsită'} |")
    out.append("")
    out.append("Algoritmul se alege după lungime: 32 = md5, 40 = sha1, 64 = sha256. "
               "Hash-ul nu se „decriptează”: se hash-uiește fiecare cuvânt din "
               "dicționar și se compară.\n")
    return "\n".join(out)


def sectiunea_b():
    out = ["## Lucrarea B. Forensics pe fișiere și steganografie\n"]

    out.append("### B1. Tipul real al fișierelor\n")
    out.append("| Fișier | Extensie | Tip real (magic bytes) |\n|---|---|---|")
    for f in sorted(PROBE.iterdir()):
        if f.is_file() and f.suffix != ".py":
            out.append(f"| {f.name} | {f.suffix} | {fo.descriere_tip(f)} |")
    out.append("\nTipul se citește din primii octeți (magic bytes), nu din extensie. "
               "Fișierele text nu au semnătură; `xor.bin` este binar (octeți criptați).\n")

    out.append("### B2. strings din `probe/ascuns.png`\n")
    coada = fo.strings_dupa_iend(PROBE / "ascuns.png")
    out.append(f"În tot fișierul sunt {len(fo.strings(PROBE / 'ascuns.png'))} șiruri imprimabile. "
               "În coada lui, după chunk-ul `IEND` (adică după sfârșitul imaginii PNG), apar:\n")
    out.append(bloc("\n".join(coada)))
    out.append("Numele `secret.txt` indică un fișier lipit după imagine.\n")

    out.append("### B3. Metadate EXIF și GPS din `probe/foto.jpg`\n")
    exif, gps = fo.citeste_exif(PROBE / "foto.jpg")
    out.append(bloc("\n".join(f"{k} = {v}" for k, v in exif.items())))
    coord = fo.coordonate_gps(gps)
    if coord:
        lat, lon = coord
        out.append(f"GPS brut: `{gps}`\n")
        out.append(f"Coordonate în grade zecimale: **{lat:.6f}, {lon:.6f}**\n")
        out.append(f"Locația pe hartă: https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}\n")
        out.append("Concluzie OSINT: poza dezvăluie unde a fost făcută. De aceea se "
                   "șterge EXIF înainte de publicare.\n")
    else:
        out.append("Poza nu conține coordonate GPS.\n")

    out.append("### B4. Fișierul ascuns (file carving)\n")
    poz = fo.extrage_zip(PROBE / "ascuns.png")
    if poz is None:
        out.append("Nu s-a găsit nicio semnătură `PK\\x03\\x04`.\n")
    else:
        out.append(f"Semnătura ZIP (`PK\\x03\\x04`) a fost găsită la octetul **{poz}**; "
                   "tot ce urmează a fost salvat ca `gasit.zip`. Conținut:\n")
        for nume, text in fo.continut_zip(RADACINA / "gasit.zip"):
            out.append(f"`{nume}`:\n")
            out.append(bloc(text))

    out.append("### B5-B6. Steganografie LSB\n")
    biti = stego.ascunde(stego.SURSA, stego.MESAJ, stego.IESIRE)
    diff = stego.diferenta_maxima(stego.SURSA, stego.IESIRE)
    dezv = stego.dezvaluie(stego.IESIRE).decode("utf-8", "replace")
    out.append(f"Mesajul ascuns în `stego.png`: `{stego.MESAJ.decode()}` ({biti} biți, "
               "cu un octet 0 la final).\n")
    out.append(f"Diferența maximă dintre un canal al pozei originale și al celei cu mesaj: "
               f"**{diff}**, deci poza arată identic cu ochiul liber.\n")
    out.append(f"Mesajul dezvăluit înapoi din `stego.png`: **{dezv}**\n")
    out.append("`stego.png` se salvează în PNG (fără pierdere); un JPG ar recompresa "
               "imaginea și ar distruge biții ascunși.\n")
    return "\n".join(out)


def sectiunea_varf():
    """Opțional: probe/challenge.bin (strat de base64 peste un XOR)."""
    cale = PROBE / "challenge.bin"
    if not cale.exists():
        return ""
    out = ["## Vârful sălii: `challenge.bin`\n"]
    brut = cale.read_text().strip()
    straturi, text, cheie = dc.desface_cu_xor(brut)
    out.append(f"Lanțul desfăcut: **{' -> '.join(straturi)}**\n")
    out.append(f"Cheia XOR: **{cheie}** (`0x{cheie:02x}`)\n" if cheie is not None
               else "Cheia XOR nu a fost găsită.\n")
    out.append(f"Textul în clar: **{text}**\n")
    hint = PROBE / "challenge_hint.txt"
    if hint.exists():
        gasit = re.search(r"[0-9a-f]{32}", hint.read_text())
        if gasit:
            md5 = hashlib.md5(text.encode()).hexdigest()
            ok = "se potrivește" if md5 == gasit.group(0) else "NU se potrivește"
            out.append(f"Verificare: md5 al textului clar = `{md5}`, {ok} cu cel din "
                       "`challenge_hint.txt`.\n")
    return "\n".join(out)


def main():
    antet = ("# Raport Laborator 5: forensics și steganografie\n\n"
             "Student: Șibaev Vasile, grupa SI-265\n\n"
             "Toate rezultatele de mai jos au fost produse de codul din acest folder, "
             "rulat pe fișierele din `probe/`.\n")
    cuprins = antet + "\n" + sectiunea_a() + "\n" + sectiunea_b() + "\n" + sectiunea_varf()
    (RADACINA / "raport.md").write_text(cuprins, encoding="utf-8")
    # fișa JSON a mesajului decodat (A7)
    dc.main([str(PROBE / "mesaj.txt"), "--fisier"])
    print("Scris raport.md")


if __name__ == "__main__":
    main()

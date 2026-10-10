# Laborator 5: forensics și steganografie

Student: Șibaev Vasile, grupa SI-265

Rulare, din folderul `Laborator_5`, cu mediul virtual activat:

```
pip install pillow pytest
python probe/pregateste.py        # creează fișierele din probe/
python arsenal/forensics/decode.py probe/mesaj.txt --fisier           # A: straturi + fisa.json
python arsenal/forensics/decode.py probe/xor.bin --fisier --xor        # A5
python arsenal/forensics/decode.py probe/hashuri.txt --fisier --hash   # A6
python forensics.py               # B1-B4
python stego.py ascunde           # B5: scrie stego.png
python stego.py dezvaluie         # B6
python arsenal/forensics/decode.py probe/challenge.bin --fisier   # vârful sălii
python -m pytest                  # testele din A7
python genereaza_raport.py        # scrie raport.md din rezultatele reale
```
